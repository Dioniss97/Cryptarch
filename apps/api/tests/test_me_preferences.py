"""
GET/PATCH /me/preferences: preferencias de usuario autenticado (tenant-scoped).
"""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from auth.service import hash_password
from config import JWT_ALGORITHM, JWT_SECRET
from dependencies import get_db
from domain.models import Tenant, User
from fastapi.testclient import TestClient
from jose import jwt
from main import app
from sqlalchemy.orm import Session


def _id():
    return uuid.uuid4().hex


def _make_token(tenant_id: str, user_id: str, role: str = "user") -> str:
    payload = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "role": role,
        "exp": datetime.now(UTC) + timedelta(hours=1),
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _auth_headers(tenant_id: str, user_id: str, role: str = "user"):
    return {"Authorization": f"Bearer {_make_token(tenant_id, user_id, role)}"}


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
def user(db_session: Session, tenant):
    u = User(
        id=_id(),
        tenant_id=tenant.id,
        email="u@acme.com",
        role="user",
        password_hash=hash_password("x"),
    )
    db_session.add(u)
    db_session.flush()
    return u


@pytest.fixture
def other_user(db_session: Session, other_tenant):
    u = User(
        id=_id(),
        tenant_id=other_tenant.id,
        email="u@other.com",
        role="user",
        password_hash=hash_password("x"),
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


def test_get_preferences_requires_auth(client: TestClient):
    r = client.get("/me/preferences")
    assert r.status_code == 401


def test_patch_preferences_requires_auth(client: TestClient):
    r = client.patch("/me/preferences", json={"theme": "dark"})
    assert r.status_code == 401


def test_get_returns_defaults_when_no_row(client: TestClient, tenant, user):
    r = client.get("/me/preferences", headers=_auth_headers(tenant.id, user.id))
    assert r.status_code == 200
    assert r.json() == {
        "theme": "system",
        "language": "es",
        "table_density": "comfortable",
        "metadata": {},
    }


def test_patch_partial_update_persists_and_get_reflects(
    client: TestClient, tenant, user
):
    headers = _auth_headers(tenant.id, user.id)
    r = client.patch("/me/preferences", headers=headers, json={"theme": "dark"})
    assert r.status_code == 200
    body = r.json()
    assert body["theme"] == "dark"
    assert body["language"] == "es"
    assert body["table_density"] == "comfortable"
    assert body["metadata"] == {}

    r2 = client.get("/me/preferences", headers=headers)
    assert r2.status_code == 200
    assert r2.json()["theme"] == "dark"


def test_patch_updates_multiple_fields(client: TestClient, tenant, user):
    headers = _auth_headers(tenant.id, user.id)
    r = client.patch(
        "/me/preferences",
        headers=headers,
        json={
            "language": "en",
            "table_density": "compact",
            "metadata": {"sidebar": "collapsed"},
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["theme"] == "system"
    assert body["language"] == "en"
    assert body["table_density"] == "compact"
    assert body["metadata"] == {"sidebar": "collapsed"}


def test_patch_invalid_theme_returns_422(client: TestClient, tenant, user):
    r = client.patch(
        "/me/preferences",
        headers=_auth_headers(tenant.id, user.id),
        json={"theme": "neon"},
    )
    assert r.status_code == 422


def test_patch_invalid_table_density_returns_422(client: TestClient, tenant, user):
    r = client.patch(
        "/me/preferences",
        headers=_auth_headers(tenant.id, user.id),
        json={"table_density": "spacious"},
    )
    assert r.status_code == 422


def test_patch_invalid_language_returns_422(client: TestClient, tenant, user):
    r = client.patch(
        "/me/preferences",
        headers=_auth_headers(tenant.id, user.id),
        json={"language": ""},
    )
    assert r.status_code == 422


def test_preferences_scoped_per_user(
    client: TestClient, tenant, user, other_user, other_tenant
):
    headers_a = _auth_headers(tenant.id, user.id)
    headers_b = _auth_headers(other_tenant.id, other_user.id)

    client.patch("/me/preferences", headers=headers_a, json={"theme": "light"})
    client.patch("/me/preferences", headers=headers_b, json={"theme": "dark"})

    r_a = client.get("/me/preferences", headers=headers_a)
    r_b = client.get("/me/preferences", headers=headers_b)
    assert r_a.json()["theme"] == "light"
    assert r_b.json()["theme"] == "dark"
