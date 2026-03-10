"""
Auth tests: login, token contents, 401 on wrong credentials.
Require PostgreSQL (same as domain tests).
"""
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from config import JWT_SECRET
from domain.models import Tenant, User
from main import app
from dependencies import get_db


def _id():
    return uuid.uuid4().hex


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


def test_login_success_returns_token(client: TestClient, db_session: Session, tenant):
    from auth.service import hash_password

    pw_hash = hash_password("secret123")
    user = User(
        id=_id(),
        tenant_id=tenant.id,
        email="admin@acme.com",
        role="admin",
        password_hash=pw_hash,
    )
    db_session.add(user)
    db_session.flush()

    response = client.post(
        "/auth/login",
        json={"tenant_id": tenant.id, "email": "admin@acme.com", "password": "secret123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    from jose import jwt

    payload = jwt.decode(
        data["access_token"], JWT_SECRET, algorithms=["HS256"]
    )
    # DB/JWT may return UUID with hyphens; model uses hex
    assert payload["sub"].replace("-", "") == user.id.replace("-", "")
    assert payload["tenant_id"].replace("-", "") == tenant.id.replace("-", "")
    assert payload["role"] == "admin"


def test_login_wrong_password_401(client: TestClient, db_session: Session, tenant):
    from auth.service import hash_password

    user = User(
        id=_id(),
        tenant_id=tenant.id,
        email="u@acme.com",
        role="user",
        password_hash=hash_password("right"),
    )
    db_session.add(user)
    db_session.flush()

    response = client.post(
        "/auth/login",
        json={"tenant_id": tenant.id, "email": "u@acme.com", "password": "wrong"},
    )
    assert response.status_code == 401


def test_login_unknown_email_401(client: TestClient, db_session: Session, tenant):
    response = client.post(
        "/auth/login",
        json={"tenant_id": tenant.id, "email": "nobody@acme.com", "password": "any"},
    )
    assert response.status_code == 401


def test_login_missing_body_422(client: TestClient):
    response = client.post("/auth/login", json={})
    assert response.status_code == 422
