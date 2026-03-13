"""
Implements ActionRepository port. Uses Session and ORM models (ActionOrm, ActionTagOrm).
"""
from typing import List

from sqlalchemy import or_
from sqlalchemy.orm import Session

from adapters.driven.persistence.models import ActionOrm, ActionTagOrm
from adapters.driven.persistence.uuid_utils import normalize_uuid, parse_uuid, to_hex
from core.domain.models import Action
from core.ports.action_repository import ActionRepository


def _orm_to_domain(orm: ActionOrm) -> Action:
    return Action(
        id=str(orm.id),
        tenant_id=str(orm.tenant_id),
        connector_id=str(orm.connector_id),
        method=orm.method,
        path=orm.path,
        name=orm.name,
        request_config=orm.request_config,
        input_schema_json=orm.input_schema_json,
        input_schema_version=orm.input_schema_version,
    )


class ActionRepositoryImpl(ActionRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_by_tenant(
        self, tenant_id: str, connector_id: str | None = None
    ) -> List[Action]:
        tid = parse_uuid(tenant_id)
        if tid is None:
            return []
        q = self._session.query(ActionOrm).filter(
            or_(ActionOrm.tenant_id == tid.hex, ActionOrm.tenant_id == str(tid))
        )
        if connector_id is not None:
            cid = parse_uuid(connector_id)
            if cid is not None:
                c_hex, c_canonical = cid.hex, str(cid)
                q = q.filter(
                    or_(
                        ActionOrm.connector_id == c_hex,
                        ActionOrm.connector_id == c_canonical,
                    )
                )
        return [_orm_to_domain(a) for a in q.all()]

    def get_by_id(self, action_id: str, tenant_id: str) -> Action | None:
        aid = parse_uuid(action_id)
        if aid is None:
            return None
        a_hex, a_canonical = aid.hex, str(aid)
        orm = (
            self._session.query(ActionOrm)
            .filter(or_(ActionOrm.id == a_hex, ActionOrm.id == a_canonical))
            .first()
        )
        if not orm or normalize_uuid(str(orm.tenant_id)) != normalize_uuid(tenant_id):
            return None
        return _orm_to_domain(orm)

    def get_action_tag_ids(self, action_id: str) -> list[str]:
        """Return tag_ids for the action as canonical UUID strings."""
        aid = parse_uuid(action_id)
        if aid is None:
            return []
        a_hex, a_canonical = aid.hex, str(aid)
        rows = (
            self._session.query(ActionTagOrm.tag_id)
            .filter(
                or_(
                    ActionTagOrm.action_id == a_hex,
                    ActionTagOrm.action_id == a_canonical,
                )
            )
            .all()
        )
        result = []
        for (tag_id,) in rows:
            u = parse_uuid(tag_id) if tag_id else None
            result.append(str(u) if u else str(tag_id))
        return result

    def add(self, action: Action, tag_ids: list[str]) -> Action:
        orm = ActionOrm(
            tenant_id=action.tenant_id,
            connector_id=action.connector_id,
            method=action.method,
            path=action.path,
            name=action.name,
            request_config=action.request_config,
            input_schema_json=action.input_schema_json,
            input_schema_version=action.input_schema_version,
        )
        self._session.add(orm)
        self._session.flush()
        for tag_id in tag_ids:
            self._session.add(
                ActionTagOrm(
                    action_id=orm.id,
                    tag_id=to_hex(tag_id),
                )
            )
        self._session.flush()
        self._session.refresh(orm)
        return _orm_to_domain(orm)

    def save(self, action: Action, tag_ids: list[str] | None) -> Action:
        aid = parse_uuid(action.id)
        if aid is None:
            return action
        a_hex, a_canonical = aid.hex, str(aid)
        orm = (
            self._session.query(ActionOrm)
            .filter(or_(ActionOrm.id == a_hex, ActionOrm.id == a_canonical))
            .first()
        )
        if not orm:
            return action
        if tag_ids is not None:
            self._session.query(ActionTagOrm).filter(
                ActionTagOrm.action_id == orm.id
            ).delete()
            for tag_id in tag_ids:
                self._session.add(
                    ActionTagOrm(
                        action_id=orm.id,
                        tag_id=to_hex(tag_id),
                    )
                )
        if action.method is not None:
            orm.method = action.method
        if action.path is not None:
            orm.path = action.path
        orm.name = action.name
        orm.request_config = action.request_config
        orm.input_schema_json = action.input_schema_json
        orm.input_schema_version = action.input_schema_version
        self._session.flush()
        self._session.refresh(orm)
        return _orm_to_domain(orm)

    def delete(self, action: Action) -> None:
        aid = parse_uuid(action.id)
        if aid is None:
            return
        a_hex, a_canonical = aid.hex, str(aid)
        orm = (
            self._session.query(ActionOrm)
            .filter(or_(ActionOrm.id == a_hex, ActionOrm.id == a_canonical))
            .first()
        )
        if orm is not None:
            self._session.query(ActionTagOrm).filter(
                ActionTagOrm.action_id == orm.id
            ).delete()
            self._session.delete(orm)


# Transitional semantic alias for Sprint 02.5 task-08a.
IntegrationActionRepositoryImpl = ActionRepositoryImpl
