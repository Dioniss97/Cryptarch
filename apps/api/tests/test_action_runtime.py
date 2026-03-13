import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy.orm import Session

from config import JWT_ALGORITHM, JWT_SECRET
from dependencies import get_db
from domain.models import (
    Action,
    ActionTag,
    Connector,
    Group,
    GroupActionFilter,
    GroupUserFilter,
    SavedFilter,
    SavedFilterTag,
    Tag,
    Tenant,
    User,
    UserTag,
)
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
def other_tenant(db_session: Session):
    t = Tenant(id=_id(), name="Other")
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


def _allow_user_to_action(
    db_session: Session, tenant_id: str, user_id: str, action_id: str, tag_id: str
) -> None:
    db_session.add(UserTag(user_id=user_id, tag_id=tag_id))
    db_session.add(ActionTag(action_id=action_id, tag_id=tag_id))
    user_filter = SavedFilter(
        id=_id(),
        tenant_id=tenant_id,
        target_type="user",
        name="uf",
    )
    action_filter = SavedFilter(
        id=_id(),
        tenant_id=tenant_id,
        target_type="action",
        name="af",
    )
    db_session.add_all([user_filter, action_filter])
    db_session.flush()
    db_session.add(SavedFilterTag(saved_filter_id=user_filter.id, tag_id=tag_id))
    db_session.add(SavedFilterTag(saved_filter_id=action_filter.id, tag_id=tag_id))
    group = Group(id=_id(), tenant_id=tenant_id, name="g")
    db_session.add(group)
    db_session.flush()
    db_session.add(GroupUserFilter(group_id=group.id, saved_filter_id=user_filter.id))
    db_session.add(GroupActionFilter(group_id=group.id, saved_filter_id=action_filter.id))
    db_session.flush()


def test_get_action_input_schema_200_when_effectively_allowed(
    client: TestClient, db_session: Session, tenant, user
):
    tag = Tag(id=_id(), tenant_id=tenant.id, name="perm")
    conn = Connector(id=_id(), tenant_id=tenant.id, base_url="https://api")
    db_session.add_all([tag, conn])
    db_session.flush()
    action = Action(
        id=_id(),
        tenant_id=tenant.id,
        connector_id=conn.id,
        method="POST",
        path="/run",
        name="Run",
        input_schema_version=1,
        input_schema_json={
            "fields": [
                {
                    "type": "text",
                    "name": "query",
                    "label": "Query",
                    "required": True,
                }
            ]
        },
    )
    db_session.add(action)
    db_session.flush()
    _allow_user_to_action(db_session, tenant.id, user.id, action.id, tag.id)

    token = _make_token(tenant.id, user.id, "user")
    r = client.get(
        f"/actions/{action.id}/input-schema",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["input_schema_version"] == 1
    assert data["input_schema_json"]["fields"][0]["name"] == "query"


def test_get_action_input_schema_403_when_not_allowed(
    client: TestClient, db_session: Session, tenant, user
):
    conn = Connector(id=_id(), tenant_id=tenant.id, base_url="https://api")
    db_session.add(conn)
    db_session.flush()
    action = Action(
        id=_id(),
        tenant_id=tenant.id,
        connector_id=conn.id,
        method="POST",
        path="/run",
        name="Run",
    )
    db_session.add(action)
    db_session.flush()

    token = _make_token(tenant.id, user.id, "user")
    r = client.get(
        f"/actions/{action.id}/input-schema",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403


def test_get_action_input_schema_404_on_other_tenant(
    client: TestClient, db_session: Session, tenant, other_tenant, user
):
    other_conn = Connector(id=_id(), tenant_id=other_tenant.id, base_url="https://other")
    db_session.add(other_conn)
    db_session.flush()
    other_action = Action(
        id=_id(),
        tenant_id=other_tenant.id,
        connector_id=other_conn.id,
        method="GET",
        path="/x",
    )
    db_session.add(other_action)
    db_session.flush()

    token = _make_token(tenant.id, user.id, "user")
    r = client.get(
        f"/actions/{other_action.id}/input-schema",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 404


def test_execute_action_200_with_stub_response(
    client: TestClient, db_session: Session, tenant, user
):
    tag = Tag(id=_id(), tenant_id=tenant.id, name="perm")
    conn = Connector(id=_id(), tenant_id=tenant.id, base_url="https://api")
    db_session.add_all([tag, conn])
    db_session.flush()
    action = Action(
        id=_id(),
        tenant_id=tenant.id,
        connector_id=conn.id,
        method="POST",
        path="/run",
        input_schema_version=1,
        input_schema_json={
            "fields": [
                {
                    "type": "number",
                    "name": "limit",
                    "label": "Limit",
                    "required": True,
                }
            ]
        },
    )
    db_session.add(action)
    db_session.flush()
    _allow_user_to_action(db_session, tenant.id, user.id, action.id, tag.id)

    token = _make_token(tenant.id, user.id, "user")
    r = client.post(
        f"/actions/{action.id}/execute",
        headers={"Authorization": f"Bearer {token}"},
        json={"payload": {"limit": 10}},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["result"]["mode"] == "stub-sync"
    assert data["result"]["echo"]["payload"] == {"limit": 10}


def test_execute_action_422_when_payload_invalid(
    client: TestClient, db_session: Session, tenant, user
):
    tag = Tag(id=_id(), tenant_id=tenant.id, name="perm")
    conn = Connector(id=_id(), tenant_id=tenant.id, base_url="https://api")
    db_session.add_all([tag, conn])
    db_session.flush()
    action = Action(
        id=_id(),
        tenant_id=tenant.id,
        connector_id=conn.id,
        method="POST",
        path="/run",
        input_schema_version=1,
        input_schema_json={
            "fields": [
                {
                    "type": "number",
                    "name": "limit",
                    "label": "Limit",
                    "required": True,
                }
            ]
        },
    )
    db_session.add(action)
    db_session.flush()
    _allow_user_to_action(db_session, tenant.id, user.id, action.id, tag.id)

    token = _make_token(tenant.id, user.id, "user")
    r = client.post(
        f"/actions/{action.id}/execute",
        headers={"Authorization": f"Bearer {token}"},
        json={"payload": {"limit": "bad"}},
    )
    assert r.status_code == 422
    data = r.json()
    assert data["ok"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"
