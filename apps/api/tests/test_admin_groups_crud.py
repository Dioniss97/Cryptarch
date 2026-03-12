"""
Admin CRUD groups: list/get/create/update/delete, tenant-scoped.
- All operations use tenant_id from JWT; filter ids must exist and belong to tenant (404 otherwise).
- Cross-tenant: 404 (do not leak existence).
"""
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from config import JWT_ALGORITHM, JWT_SECRET
from domain.models import (
    Group,
    GroupActionFilter,
    GroupDocumentFilter,
    GroupUserFilter,
    SavedFilter,
    Tenant,
    User,
)
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
def tenant_filters(db_session: Session, tenant):
    """Three saved filters (user, action, document) in tenant for group bindings."""
    uf = SavedFilter(
        id=_id(),
        tenant_id=tenant.id,
        target_type="user",
        name="user-filter",
    )
    af = SavedFilter(
        id=_id(),
        tenant_id=tenant.id,
        target_type="action",
        name="action-filter",
    )
    df = SavedFilter(
        id=_id(),
        tenant_id=tenant.id,
        target_type="document",
        name="document-filter",
    )
    db_session.add_all([uf, af, df])
    db_session.flush()
    return {"user": uf, "action": af, "document": df}


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


def test_list_groups_empty_200(client: TestClient, tenant, admin_user):
    """GET /admin/groups returns 200 and [] when no groups."""
    r = client.get(
        "/admin/groups",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_list_groups_tenant_scoped(
    client: TestClient, tenant, other_tenant, admin_user, db_session: Session
):
    """Groups from other tenant are not returned."""
    other_g = Group(
        id=_id(),
        tenant_id=other_tenant.id,
        name="other-group",
    )
    db_session.add(other_g)
    db_session.flush()

    r = client.get(
        "/admin/groups",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 200
    data = r.json()
    ids = [g["id"] for g in data]
    assert other_g.id not in ids and str(other_g.id) not in ids


def test_list_groups_unauth_401(client: TestClient):
    r = client.get("/admin/groups")
    assert r.status_code == 401


def test_list_groups_non_admin_403(client: TestClient, tenant, db_session: Session):
    u = User(
        id=_id(),
        tenant_id=tenant.id,
        email="u@acme.com",
        role="user",
        password_hash=hash_password("x"),
    )
    db_session.add(u)
    db_session.flush()
    r = client.get("/admin/groups", headers=_auth_headers(tenant.id, u.id, role="user"))
    assert r.status_code == 403


# ----- Get by id -----


def test_get_group_same_tenant_200(
    client: TestClient, tenant, admin_user, tenant_filters, db_session: Session
):
    g = Group(id=_id(), tenant_id=tenant.id, name="my-group")
    db_session.add(g)
    db_session.flush()
    db_session.add(GroupUserFilter(group_id=g.id, saved_filter_id=tenant_filters["user"].id))
    db_session.add(GroupActionFilter(group_id=g.id, saved_filter_id=tenant_filters["action"].id))
    db_session.flush()

    r = client.get(
        f"/admin/groups/{g.id}",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 200
    data = r.json()
    assert _uuid_eq(data["id"], g.id)
    assert data["name"] == "my-group"
    assert _uuid_eq(data["tenant_id"], tenant.id)
    assert "user_filter_ids" in data
    assert "action_filter_ids" in data
    assert "document_filter_ids" in data
    assert len(data["user_filter_ids"]) == 1
    assert len(data["action_filter_ids"]) == 1
    assert len(data["document_filter_ids"]) == 0


def test_get_group_other_tenant_404(
    client: TestClient, tenant, other_tenant, admin_user, db_session: Session
):
    other_g = Group(
        id=_id(),
        tenant_id=other_tenant.id,
        name="other-group",
    )
    db_session.add(other_g)
    db_session.flush()

    r = client.get(
        f"/admin/groups/{other_g.id}",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 404


def test_get_group_not_found_404(client: TestClient, tenant, admin_user):
    r = client.get(
        f"/admin/groups/{_id()}",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 404


# ----- Create -----


def test_create_group_201(client: TestClient, tenant, admin_user, tenant_filters):
    r = client.post(
        "/admin/groups",
        headers=_auth_headers(tenant.id, admin_user.id),
        json={
            "name": "Team A",
            "user_filter_ids": [str(tenant_filters["user"].id)],
            "action_filter_ids": [str(tenant_filters["action"].id)],
            "document_filter_ids": [str(tenant_filters["document"].id)],
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Team A"
    assert _uuid_eq(data["tenant_id"], tenant.id)
    assert "id" in data
    assert len(data["user_filter_ids"]) == 1
    assert len(data["action_filter_ids"]) == 1
    assert len(data["document_filter_ids"]) == 1


def test_create_group_empty_filters_201(client: TestClient, tenant, admin_user):
    r = client.post(
        "/admin/groups",
        headers=_auth_headers(tenant.id, admin_user.id),
        json={
            "name": "Empty Group",
            "user_filter_ids": [],
            "action_filter_ids": [],
            "document_filter_ids": [],
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["user_filter_ids"] == []
    assert data["action_filter_ids"] == []
    assert data["document_filter_ids"] == []


def test_create_group_filter_not_found_404(
    client: TestClient, tenant, admin_user, tenant_filters
):
    r = client.post(
        "/admin/groups",
        headers=_auth_headers(tenant.id, admin_user.id),
        json={
            "name": "Bad",
            "user_filter_ids": [str(tenant_filters["user"].id), _id()],
            "action_filter_ids": [],
            "document_filter_ids": [],
        },
    )
    assert r.status_code == 404


def test_create_group_filter_other_tenant_404(
    client: TestClient,
    tenant,
    other_tenant,
    admin_user,
    tenant_filters,
    db_session: Session,
):
    other_f = SavedFilter(
        id=_id(),
        tenant_id=other_tenant.id,
        target_type="user",
        name="other-filter",
    )
    db_session.add(other_f)
    db_session.flush()
    r = client.post(
        "/admin/groups",
        headers=_auth_headers(tenant.id, admin_user.id),
        json={
            "name": "Bad",
            "user_filter_ids": [str(tenant_filters["user"].id), str(other_f.id)],
            "action_filter_ids": [],
            "document_filter_ids": [],
        },
    )
    assert r.status_code == 404


# ----- Update -----


def test_update_group_200(
    client: TestClient, tenant, admin_user, tenant_filters, db_session: Session
):
    g = Group(id=_id(), tenant_id=tenant.id, name="old-name")
    db_session.add(g)
    db_session.flush()

    r = client.patch(
        f"/admin/groups/{g.id}",
        headers=_auth_headers(tenant.id, admin_user.id),
        json={"name": "new-name"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "new-name"


def test_update_group_filter_ids_200(
    client: TestClient, tenant, admin_user, tenant_filters, db_session: Session
):
    g = Group(id=_id(), tenant_id=tenant.id, name="g")
    db_session.add(g)
    db_session.flush()

    r = client.patch(
        f"/admin/groups/{g.id}",
        headers=_auth_headers(tenant.id, admin_user.id),
        json={
            "user_filter_ids": [str(tenant_filters["user"].id)],
            "action_filter_ids": [str(tenant_filters["action"].id)],
            "document_filter_ids": [str(tenant_filters["document"].id)],
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data["user_filter_ids"]) == 1
    assert len(data["action_filter_ids"]) == 1
    assert len(data["document_filter_ids"]) == 1


def test_update_group_other_tenant_404(
    client: TestClient, tenant, other_tenant, admin_user, db_session: Session
):
    other_g = Group(
        id=_id(),
        tenant_id=other_tenant.id,
        name="other",
    )
    db_session.add(other_g)
    db_session.flush()

    r = client.patch(
        f"/admin/groups/{other_g.id}",
        headers=_auth_headers(tenant.id, admin_user.id),
        json={"name": "hacked"},
    )
    assert r.status_code == 404


# ----- Delete -----


def test_delete_group_204(
    client: TestClient, tenant, admin_user, db_session: Session
):
    g = Group(id=_id(), tenant_id=tenant.id, name="del-group")
    db_session.add(g)
    db_session.flush()
    group_id = g.id

    r = client.delete(
        f"/admin/groups/{group_id}",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 204

    r2 = client.get(
        f"/admin/groups/{group_id}",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r2.status_code == 404


def test_delete_group_other_tenant_404(
    client: TestClient, tenant, other_tenant, admin_user, db_session: Session
):
    other_g = Group(
        id=_id(),
        tenant_id=other_tenant.id,
        name="other",
    )
    db_session.add(other_g)
    db_session.flush()

    r = client.delete(
        f"/admin/groups/{other_g.id}",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 404
