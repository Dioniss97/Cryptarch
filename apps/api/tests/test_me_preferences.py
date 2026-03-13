import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy.orm import Session

from config import JWT_ALGORITHM, JWT_SECRET
from dependencies import get_db
from domain.models import Tenant, User
from main import app


def _id() -> str:
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
def user(db_session: Session, tenant):
    u = User(
        id=_id(),
        tenant_id=tenant.id,
        email="user@acme.com",
        role="user",
        password_hash="x",
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


def test_get_me_preferences_returns_defaults_when_absent(
    client: TestClient, tenant, user
):
    token = _make_token(tenant.id, user.id, "user")
    r = client.get("/me/preferences", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json() == {
        "language": "es",
        "theme": "system",
        "table_density": "comfortable",
        "metadata": None,
    }


def test_patch_me_preferences_persists_and_get_returns_saved(
    client: TestClient, tenant, user
):
    token = _make_token(tenant.id, user.id, "user")
    patch = client.patch(
        "/me/preferences",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "language": "en",
            "theme": "dark",
            "table_density": "compact",
            "metadata": {"shell": "advanced"},
        },
    )
    assert patch.status_code == 200

    get_after = client.get(
        "/me/preferences",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_after.status_code == 200
    assert get_after.json() == {
        "language": "en",
        "theme": "dark",
        "table_density": "compact",
        "metadata": {"shell": "advanced"},
    }


def test_patch_me_preferences_rejects_invalid_theme(client: TestClient, tenant, user):
    token = _make_token(tenant.id, user.id, "user")
    r = client.patch(
        "/me/preferences",
        headers={"Authorization": f"Bearer {token}"},
        json={"theme": "neon"},
    )
    assert r.status_code == 422
