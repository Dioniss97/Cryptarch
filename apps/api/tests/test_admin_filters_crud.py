"""
Admin CRUD saved filters: list/get/create/update/delete, tenant-scoped.
- All operations use tenant_id from JWT; tag_ids must exist and belong to tenant (404 otherwise).
- Cross-tenant: 404 (do not leak existence).
"""
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from config import JWT_ALGORITHM, JWT_SECRET
from domain.models import SavedFilter, SavedFilterTag, Tag, Tenant, User
from main import app
from dependencies import get_db
from jose import jwt
from datetime import datetime, timedelta, timezone
from auth.service import hash_password


def _uuid_eq(a: str, b: str) -> bool:
    """Compare two UUID strings regardless of hex vs canonical form."""
    try:
        return uuid.UUID(str(a)) == uuid.UUID(str(b))
    except (ValueError, TypeError):
        return a == b


def _id():
    return uuid.uuid4().hex


def _make_token(tenant_id: str, user_id: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


@pytest.fixture
def tenant(db_session: Session):
    t = Tenant(id=_id(), name="Acme")
    db_session.add(t)
    db_session.flush()
    return t


@pytest.fixture
def other_tenant(db_session: Session):
    t = Tenant(id=_id(), name="OtherCo")
    db_session.add(t)
    db_session.flush()
    return t


@pytest.fixture
def admin_user(db_session: Session, tenant):
    u = User(
        id=_id(),
        tenant_id=tenant.id,
        email="admin@acme.com",
        role="admin",
        password_hash=hash_password("secret"),
    )
    db_session.add(u)
    db_session.flush()
    return u


@pytest.fixture
def tenant_tags(db_session: Session, tenant):
    """Two tags in tenant for use in filter tests."""
    t1 = Tag(id=_id(), tenant_id=tenant.id, name="tag-a")
    t2 = Tag(id=_id(), tenant_id=tenant.id, name="tag-b")
    db_session.add_all([t1, t2])
    db_session.flush()
    return [t1, t2]


@pytest.fixture
def client(db_session: Session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_db, None)


def _auth_headers(tenant_id: str, user_id: str, role: str = "admin"):
    return {"Authorization": f"Bearer {_make_token(tenant_id, user_id, role)}"}


# ----- List -----


def test_list_filters_empty_200(client: TestClient, tenant, admin_user):
    """GET /admin/filters returns 200 and [] when no filters."""
    r = client.get(
        "/admin/filters",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_list_filters_tenant_scoped(
    client: TestClient, tenant, other_tenant, admin_user, db_session: Session
):
    """Filters from other tenant are not returned."""
    other_f = SavedFilter(
        id=_id(),
        tenant_id=other_tenant.id,
        target_type="user",
        name="other-filter",
    )
    db_session.add(other_f)
    db_session.flush()

    r = client.get(
        "/admin/filters",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 200
    data = r.json()
    ids = [f["id"] for f in data]
    assert other_f.id not in ids and str(other_f.id) not in ids


def test_list_filters_unauth_401(client: TestClient):
    r = client.get("/admin/filters")
    assert r.status_code == 401


def test_list_filters_non_admin_403(client: TestClient, tenant, db_session: Session):
    u = User(
        id=_id(),
        tenant_id=tenant.id,
        email="u@acme.com",
        role="user",
        password_hash=hash_password("x"),
    )
    db_session.add(u)
    db_session.flush()
    r = client.get("/admin/filters", headers=_auth_headers(tenant.id, u.id, role="user"))
    assert r.status_code == 403


# ----- Get by id -----


def test_get_filter_same_tenant_200(
    client: TestClient, tenant, admin_user, db_session: Session
):
    target = SavedFilter(
        id=_id(),
        tenant_id=tenant.id,
        target_type="action",
        name="my-filter",
    )
    db_session.add(target)
    db_session.flush()

    r = client.get(
        f"/admin/filters/{target.id}",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 200
    data = r.json()
    assert _uuid_eq(data["id"], target.id)
    assert data["name"] == "my-filter"
    assert data["target_type"] == "action"
    assert _uuid_eq(data["tenant_id"], tenant.id)
    assert "tag_ids" in data
    assert isinstance(data["tag_ids"], list)


def test_get_filter_with_tag_ids(
    client: TestClient, tenant, admin_user, tenant_tags, db_session: Session
):
    target = SavedFilter(
        id=_id(),
        tenant_id=tenant.id,
        target_type="user",
        name="filter-with-tags",
    )
    db_session.add(target)
    db_session.flush()
    for tag in tenant_tags:
        db_session.add(
            SavedFilterTag(saved_filter_id=target.id, tag_id=tag.id)
        )
    db_session.flush()

    r = client.get(
        f"/admin/filters/{target.id}",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data["tag_ids"]) == 2
    expected = {str(uuid.UUID(t.id)) for t in tenant_tags}
    assert set(data["tag_ids"]) == expected
    for tid in data["tag_ids"]:
        assert len(tid) == 36 and "-" in tid


def test_get_filter_other_tenant_404(
    client: TestClient, tenant, other_tenant, admin_user, db_session: Session
):
    other_f = SavedFilter(
        id=_id(),
        tenant_id=other_tenant.id,
        target_type="user",
        name="other-filter",
    )
    db_session.add(other_f)
    db_session.flush()

    r = client.get(
        f"/admin/filters/{other_f.id}",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 404


def test_get_filter_not_found_404(client: TestClient, tenant, admin_user):
    r = client.get(
        f"/admin/filters/{_id()}",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 404


# ----- Create -----


def test_create_filter_201(client: TestClient, tenant, admin_user, tenant_tags):
    tag_ids = [str(tenant_tags[0].id), str(tenant_tags[1].id)]
    r = client.post(
        "/admin/filters",
        headers=_auth_headers(tenant.id, admin_user.id),
        json={
            "name": "vip-users",
            "target_type": "user",
            "tag_ids": tag_ids,
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "vip-users"
    assert data["target_type"] == "user"
    assert _uuid_eq(data["tenant_id"], tenant.id)
    assert "id" in data
    assert len(data["tag_ids"]) == 2


def test_create_filter_no_tags_201(client: TestClient, tenant, admin_user):
    r = client.post(
        "/admin/filters",
        headers=_auth_headers(tenant.id, admin_user.id),
        json={"name": "empty-filter", "target_type": "document", "tag_ids": []},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["tag_ids"] == []


def test_create_filter_tag_not_found_404(
    client: TestClient, tenant, admin_user, tenant_tags
):
    """tag_ids reference non-existent tag -> 404."""
    r = client.post(
        "/admin/filters",
        headers=_auth_headers(tenant.id, admin_user.id),
        json={
            "name": "bad",
            "target_type": "user",
            "tag_ids": [str(tenant_tags[0].id), _id()],
        },
    )
    assert r.status_code == 404


def test_create_filter_tag_other_tenant_404(
    client: TestClient, tenant, other_tenant, admin_user, tenant_tags, db_session: Session
):
    """tag_ids reference tag from other tenant -> 404."""
    other_tag = Tag(
        id=_id(), tenant_id=other_tenant.id, name="other-tag"
    )
    db_session.add(other_tag)
    db_session.flush()
    r = client.post(
        "/admin/filters",
        headers=_auth_headers(tenant.id, admin_user.id),
        json={
            "name": "bad",
            "target_type": "user",
            "tag_ids": [str(tenant_tags[0].id), str(other_tag.id)],
        },
    )
    assert r.status_code == 404


# ----- Update -----


def test_update_filter_200(
    client: TestClient, tenant, admin_user, tenant_tags, db_session: Session
):
    target = SavedFilter(
        id=_id(),
        tenant_id=tenant.id,
        target_type="user",
        name="old-name",
    )
    db_session.add(target)
    db_session.flush()
    db_session.add(
        SavedFilterTag(saved_filter_id=target.id, tag_id=tenant_tags[0].id)
    )
    db_session.flush()

    r = client.patch(
        f"/admin/filters/{target.id}",
        headers=_auth_headers(tenant.id, admin_user.id),
        json={"name": "new-name"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "new-name"


def test_update_filter_tag_ids_200(
    client: TestClient, tenant, admin_user, tenant_tags, db_session: Session
):
    target = SavedFilter(
        id=_id(),
        tenant_id=tenant.id,
        target_type="user",
        name="f",
    )
    db_session.add(target)
    db_session.flush()

    r = client.patch(
        f"/admin/filters/{target.id}",
        headers=_auth_headers(tenant.id, admin_user.id),
        json={"tag_ids": [str(tenant_tags[0].id), str(tenant_tags[1].id)]},
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data["tag_ids"]) == 2


def test_update_filter_other_tenant_404(
    client: TestClient, tenant, other_tenant, admin_user, db_session: Session
):
    other_f = SavedFilter(
        id=_id(),
        tenant_id=other_tenant.id,
        target_type="user",
        name="other",
    )
    db_session.add(other_f)
    db_session.flush()

    r = client.patch(
        f"/admin/filters/{other_f.id}",
        headers=_auth_headers(tenant.id, admin_user.id),
        json={"name": "hacked"},
    )
    assert r.status_code == 404


# ----- Delete -----


def test_delete_filter_204(
    client: TestClient, tenant, admin_user, db_session: Session
):
    target = SavedFilter(
        id=_id(),
        tenant_id=tenant.id,
        target_type="document",
        name="del-filter",
    )
    db_session.add(target)
    db_session.flush()
    filter_id = target.id

    r = client.delete(
        f"/admin/filters/{filter_id}",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 204

    r2 = client.get(
        f"/admin/filters/{filter_id}",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r2.status_code == 404


def test_delete_filter_other_tenant_404(
    client: TestClient, tenant, other_tenant, admin_user, db_session: Session
):
    other_f = SavedFilter(
        id=_id(),
        tenant_id=other_tenant.id,
        target_type="user",
        name="other",
    )
    db_session.add(other_f)
    db_session.flush()

    r = client.delete(
        f"/admin/filters/{other_f.id}",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 404
