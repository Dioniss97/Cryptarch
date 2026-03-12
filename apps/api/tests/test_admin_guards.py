"""
Role guards: admin-only routes return 200 for admin, 403 for user, 401 when unauthenticated.
Requires PostgreSQL (same as auth/domain tests).
"""
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from config import JWT_ALGORITHM, JWT_SECRET
from domain.models import Tenant, User
from main import app
from dependencies import get_db
from jose import jwt
from datetime import datetime, timedelta, timezone


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
def client(db_session: Session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_db, None)


def test_admin_me_with_admin_token_200(client: TestClient, tenant):
    """GET /admin/me with valid admin JWT returns 200 and role in body."""
    user_id = _id()
    token = _make_token(tenant.id, user_id, "admin")
    response = client.get(
        "/admin/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("role") == "admin"
    assert data.get("sub") == user_id
    assert data.get("tenant_id") == tenant.id


def test_admin_me_with_user_token_403(client: TestClient, tenant):
    """GET /admin/me with valid user (non-admin) JWT returns 403."""
    token = _make_token(tenant.id, _id(), "user")
    response = client.get(
        "/admin/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_admin_me_without_auth_401(client: TestClient):
    """GET /admin/me without Authorization header returns 401."""
    response = client.get("/admin/me")
    assert response.status_code == 401


def test_admin_me_invalid_token_401(client: TestClient):
    """GET /admin/me with invalid or malformed token returns 401."""
    response = client.get(
        "/admin/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401
