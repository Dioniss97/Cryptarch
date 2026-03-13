"""
Admin CRUD tags: list/get/create/update/delete, tenant-scoped.
- All operations use tenant_id from JWT (CurrentUser), never from body.
- Cross-tenant: 404 (do not leak existence).
"""
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from config import JWT_ALGORITHM, JWT_SECRET
from domain.models import Tag, Tenant, User
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


def test_list_tags_empty_200(client: TestClient, tenant, admin_user):
    """GET /admin/tags returns 200 and [] when no tags."""
    r = client.get(
        "/admin/tags",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_list_tags_tenant_scoped(client: TestClient, tenant, other_tenant, admin_user, db_session: Session):
    """Tags from other tenant are not returned."""
    other_tag = Tag(
        id=_id(),
        tenant_id=other_tenant.id,
        name="other-tag",
    )
    db_session.add(other_tag)
    db_session.flush()

    r = client.get(
        "/admin/tags",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 200
    data = r.json()
    ids = [t["id"] for t in data]
    assert other_tag.id not in ids


def test_list_tags_unauth_401(client: TestClient):
    r = client.get("/admin/tags")
    assert r.status_code == 401


def test_list_tags_non_admin_403(client: TestClient, tenant, db_session: Session):
    u = User(
        id=_id(),
        tenant_id=tenant.id,
        email="u@acme.com",
        role="user",
        password_hash=hash_password("x"),
    )
    db_session.add(u)
    db_session.flush()
    r = client.get("/admin/tags", headers=_auth_headers(tenant.id, u.id, role="user"))
    assert r.status_code == 403


# ----- Get by id -----


def test_get_tag_same_tenant_200(client: TestClient, tenant, admin_user, db_session: Session):
    target = Tag(
        id=_id(),
        tenant_id=tenant.id,
        name="support",
    )
    db_session.add(target)
    db_session.flush()

    r = client.get(
        f"/admin/tags/{target.id}",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 200
    assert _uuid_eq(r.json()["id"], target.id)
    assert r.json()["name"] == "support"
    assert _uuid_eq(r.json()["tenant_id"], tenant.id)


def test_get_tag_other_tenant_404(client: TestClient, tenant, other_tenant, admin_user, db_session: Session):
    """Cross-tenant: 404 to avoid leaking existence."""
    other_tag = Tag(
        id=_id(),
        tenant_id=other_tenant.id,
        name="other-tag",
    )
    db_session.add(other_tag)
    db_session.flush()

    r = client.get(
        f"/admin/tags/{other_tag.id}",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 404


def test_get_tag_not_found_404(client: TestClient, tenant, admin_user):
    r = client.get(
        f"/admin/tags/{_id()}",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 404


# ----- Create -----


def test_create_tag_201(client: TestClient, tenant, admin_user):
    r = client.post(
        "/admin/tags",
        headers=_auth_headers(tenant.id, admin_user.id),
        json={"name": "vip"},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "vip"
    assert _uuid_eq(data["tenant_id"], tenant.id)
    assert "id" in data


def test_create_tag_duplicate_name_409(client: TestClient, tenant, admin_user, db_session: Session):
    db_session.add(
        Tag(
            id=_id(),
            tenant_id=tenant.id,
            name="dup-tag",
        )
    )
    db_session.flush()

    r = client.post(
        "/admin/tags",
        headers=_auth_headers(tenant.id, admin_user.id),
        json={"name": "dup-tag"},
    )
    assert r.status_code == 409


# ----- Update -----


def test_update_tag_200(client: TestClient, tenant, admin_user, db_session: Session):
    target = Tag(
        id=_id(),
        tenant_id=tenant.id,
        name="old-name",
    )
    db_session.add(target)
    db_session.flush()

    r = client.patch(
        f"/admin/tags/{target.id}",
        headers=_auth_headers(tenant.id, admin_user.id),
        json={"name": "new-name"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "new-name"


def test_update_tag_other_tenant_404(client: TestClient, tenant, other_tenant, admin_user, db_session: Session):
    other_tag = Tag(
        id=_id(),
        tenant_id=other_tenant.id,
        name="other-tag",
    )
    db_session.add(other_tag)
    db_session.flush()

    r = client.patch(
        f"/admin/tags/{other_tag.id}",
        headers=_auth_headers(tenant.id, admin_user.id),
        json={"name": "hacked"},
    )
    assert r.status_code == 404


def test_update_tag_duplicate_name_409(client: TestClient, tenant, admin_user, db_session: Session):
    target = Tag(
        id=_id(),
        tenant_id=tenant.id,
        name="tag-a",
    )
    other = Tag(
        id=_id(),
        tenant_id=tenant.id,
        name="tag-b",
    )
    db_session.add_all([target, other])
    db_session.flush()

    r = client.patch(
        f"/admin/tags/{target.id}",
        headers=_auth_headers(tenant.id, admin_user.id),
        json={"name": "tag-b"},
    )
    assert r.status_code == 409


# ----- Delete -----


def test_delete_tag_204(client: TestClient, tenant, admin_user, db_session: Session):
    target = Tag(
        id=_id(),
        tenant_id=tenant.id,
        name="del-tag",
    )
    db_session.add(target)
    db_session.flush()
    tag_id = target.id

    r = client.delete(
        f"/admin/tags/{tag_id}",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 204

    r2 = client.get(f"/admin/tags/{tag_id}", headers=_auth_headers(tenant.id, admin_user.id))
    assert r2.status_code == 404


def test_delete_tag_other_tenant_404(client: TestClient, tenant, other_tenant, admin_user, db_session: Session):
    other_tag = Tag(
        id=_id(),
        tenant_id=other_tenant.id,
        name="other-tag",
    )
    db_session.add(other_tag)
    db_session.flush()

    r = client.delete(
        f"/admin/tags/{other_tag.id}",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 404
