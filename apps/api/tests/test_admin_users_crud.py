"""
Admin CRUD users: list/get/create/update/delete, tenant-scoped.
- All operations use tenant_id from JWT (CurrentUser), never from body.
- Cross-tenant: 404 (do not leak existence).
"""
import uuid


def _uuid_eq(a: str, b: str) -> bool:
    """Compare two UUID strings regardless of hex vs canonical form."""
    try:
        return uuid.UUID(str(a)) == uuid.UUID(str(b))
    except (ValueError, TypeError):
        return a == b

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from config import JWT_ALGORITHM, JWT_SECRET
from domain.models import Tenant, User
from main import app
from dependencies import get_db
from jose import jwt
from datetime import datetime, timedelta, timezone
from auth.service import hash_password


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


def test_list_users_empty_200(client: TestClient, tenant, admin_user):
    """GET /admin/users returns 200 and [] when no other users."""
    r = client.get(
        "/admin/users",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    # Admin may or may not appear in list depending on product choice; allow both
    assert len(data) <= 1


def test_list_users_tenant_scoped(client: TestClient, tenant, other_tenant, admin_user, db_session: Session):
    """Users from other tenant are not returned."""
    other_user = User(
        id=_id(),
        tenant_id=other_tenant.id,
        email="user@other.com",
        role="user",
        password_hash=hash_password("x"),
    )
    db_session.add(other_user)
    db_session.flush()

    r = client.get(
        "/admin/users",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 200
    data = r.json()
    ids = [u["id"] for u in data]
    assert other_user.id not in ids


def test_list_users_unauth_401(client: TestClient):
    r = client.get("/admin/users")
    assert r.status_code == 401


def test_list_users_non_admin_403(client: TestClient, tenant, db_session: Session):
    u = User(
        id=_id(),
        tenant_id=tenant.id,
        email="u@acme.com",
        role="user",
        password_hash=hash_password("x"),
    )
    db_session.add(u)
    db_session.flush()
    r = client.get("/admin/users", headers=_auth_headers(tenant.id, u.id, role="user"))
    assert r.status_code == 403


# ----- Get by id -----


def test_get_user_same_tenant_200(client: TestClient, tenant, admin_user, db_session: Session):
    target = User(
        id=_id(),
        tenant_id=tenant.id,
        email="u@acme.com",
        role="user",
        password_hash=hash_password("x"),
    )
    db_session.add(target)
    db_session.flush()

    r = client.get(
        f"/admin/users/{target.id}",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 200
    assert _uuid_eq(r.json()["id"], target.id)
    assert r.json()["email"] == "u@acme.com"
    assert "password_hash" not in r.json()


def test_get_user_other_tenant_404(client: TestClient, tenant, other_tenant, admin_user, db_session: Session):
    """Cross-tenant: 404 to avoid leaking existence."""
    other_user = User(
        id=_id(),
        tenant_id=other_tenant.id,
        email="u@other.com",
        role="user",
        password_hash=hash_password("x"),
    )
    db_session.add(other_user)
    db_session.flush()

    r = client.get(
        f"/admin/users/{other_user.id}",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 404


def test_get_user_not_found_404(client: TestClient, tenant, admin_user):
    r = client.get(
        f"/admin/users/{_id()}",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 404


# ----- Create -----


def test_create_user_201(client: TestClient, tenant, admin_user):
    r = client.post(
        "/admin/users",
        headers=_auth_headers(tenant.id, admin_user.id),
        json={
            "email": "new@acme.com",
            "role": "user",
            "password": "plainpass",
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == "new@acme.com"
    assert data["role"] == "user"
    assert _uuid_eq(data["tenant_id"], tenant.id)
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data


def test_create_user_tenant_from_jwt_ignores_body(client: TestClient, tenant, other_tenant, admin_user):
    """tenant_id in body must be ignored; user is created in JWT tenant."""
    r = client.post(
        "/admin/users",
        headers=_auth_headers(tenant.id, admin_user.id),
        json={
            "tenant_id": other_tenant.id,
            "email": "hacker@acme.com",
            "role": "user",
            "password": "x",
        },
    )
    assert r.status_code == 201
    assert _uuid_eq(r.json()["tenant_id"], tenant.id)


def test_create_user_duplicate_email_409(client: TestClient, tenant, admin_user, db_session: Session):
    db_session.add(
        User(
            id=_id(),
            tenant_id=tenant.id,
            email="dup@acme.com",
            role="user",
            password_hash=hash_password("x"),
        )
    )
    db_session.flush()

    r = client.post(
        "/admin/users",
        headers=_auth_headers(tenant.id, admin_user.id),
        json={"email": "dup@acme.com", "role": "user", "password": "y"},
    )
    assert r.status_code == 409


# ----- Update -----


def test_update_user_200(client: TestClient, tenant, admin_user, db_session: Session):
    target = User(
        id=_id(),
        tenant_id=tenant.id,
        email="old@acme.com",
        role="user",
        password_hash=hash_password("x"),
    )
    db_session.add(target)
    db_session.flush()

    r = client.patch(
        f"/admin/users/{target.id}",
        headers=_auth_headers(tenant.id, admin_user.id),
        json={"email": "new@acme.com", "role": "admin"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == "new@acme.com"
    assert data["role"] == "admin"


def test_update_user_other_tenant_404(client: TestClient, tenant, other_tenant, admin_user, db_session: Session):
    other_user = User(
        id=_id(),
        tenant_id=other_tenant.id,
        email="u@other.com",
        role="user",
        password_hash=hash_password("x"),
    )
    db_session.add(other_user)
    db_session.flush()

    r = client.patch(
        f"/admin/users/{other_user.id}",
        headers=_auth_headers(tenant.id, admin_user.id),
        json={"email": "hacked@acme.com"},
    )
    assert r.status_code == 404


# ----- Delete -----


def test_delete_user_204(client: TestClient, tenant, admin_user, db_session: Session):
    target = User(
        id=_id(),
        tenant_id=tenant.id,
        email="del@acme.com",
        role="user",
        password_hash=hash_password("x"),
    )
    db_session.add(target)
    db_session.flush()
    uid = target.id

    r = client.delete(
        f"/admin/users/{uid}",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 204

    # Verify gone
    r2 = client.get(f"/admin/users/{uid}", headers=_auth_headers(tenant.id, admin_user.id))
    assert r2.status_code == 404


def test_delete_user_other_tenant_404(client: TestClient, tenant, other_tenant, admin_user, db_session: Session):
    other_user = User(
        id=_id(),
        tenant_id=other_tenant.id,
        email="u@other.com",
        role="user",
        password_hash=hash_password("x"),
    )
    db_session.add(other_user)
    db_session.flush()

    r = client.delete(
        f"/admin/users/{other_user.id}",
        headers=_auth_headers(tenant.id, admin_user.id),
    )
    assert r.status_code == 404
