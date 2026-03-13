"""Admin HTTP routes for Actions. Uses core.application.action and repositories."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from adapters.driven.persistence.action_repository import ActionRepositoryImpl
from adapters.driven.persistence.connector_repository import SqlAlchemyConnectorRepository
from adapters.driven.persistence.tag_repository import SqlAlchemyTagRepository
from adapters.driving.schemas.action import (
    ActionCreateBody,
    ActionUpdateBody,
    action_to_response,
)
from core.application import action as action_use_cases
from core.application.action import (
    ActionNotFoundError,
    ConnectorNotFoundError,
    TagNotFoundError,
)
from dependencies import CurrentUser, get_db, require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


def _tag_ids_to_str(tag_ids: list) -> list[str]:
    """Convert list of UUID to canonical string list."""
    return [str(t) for t in tag_ids]


@router.get("/actions")
def list_actions(
    connector_id: uuid.UUID | None = None,
    current_user: Annotated[CurrentUser, Depends(require_admin)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """List actions of the current tenant. Optional connector_id filter (must be tenant's connector)."""
    repo = ActionRepositoryImpl(db)
    connector_id_str = str(connector_id) if connector_id is not None else None
    if connector_id is not None:
        connector_repo = SqlAlchemyConnectorRepository(db)
        conn = connector_repo.get_by_id(connector_id_str, current_user.tenant_id)
        if not conn:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Connector not found",
            )
    actions = action_use_cases.list_actions(
        current_user.tenant_id, repo, connector_id=connector_id_str
    )
    return [
        action_to_response(a, tag_ids=repo.get_action_tag_ids(a.id))
        for a in actions
    ]


@router.get("/actions/{action_id}")
def get_action(
    action_id: str,
    current_user: Annotated[CurrentUser, Depends(require_admin)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """Get action by id; 404 if not in current tenant. Response includes tag_ids."""
    repo = ActionRepositoryImpl(db)
    a = action_use_cases.get_action(action_id, current_user.tenant_id, repo)
    if a is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found",
        )
    tag_ids = repo.get_action_tag_ids(a.id)
    return action_to_response(a, tag_ids=tag_ids)


@router.post("/actions", status_code=status.HTTP_201_CREATED)
def create_action(
    body: ActionCreateBody,
    current_user: Annotated[CurrentUser, Depends(require_admin)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """Create action in current tenant. connector_id and tag_ids must exist and belong to tenant; 404 if not."""
    repo = ActionRepositoryImpl(db)
    connector_repo = SqlAlchemyConnectorRepository(db)
    tag_repo = SqlAlchemyTagRepository(db)
    tag_ids_str = _tag_ids_to_str(body.tag_ids)
    try:
        action = action_use_cases.create_action(
            current_user.tenant_id,
            str(body.connector_id),
            body.method,
            body.path,
            body.name,
            body.request_config,
            body.input_schema_json,
            body.input_schema_version,
            tag_ids_str,
            repo,
            connector_repo,
            tag_repo,
        )
        db.commit()
    except ConnectorNotFoundError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connector not found",
        )
    except TagNotFoundError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return action_to_response(action, tag_ids=tag_ids_str)


@router.patch("/actions/{action_id}")
def update_action(
    action_id: str,
    body: ActionUpdateBody,
    current_user: Annotated[CurrentUser, Depends(require_admin)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """Update action; 404 if not in current tenant. tag_ids must exist and belong to tenant."""
    repo = ActionRepositoryImpl(db)
    tag_repo = SqlAlchemyTagRepository(db)
    tag_ids_str = _tag_ids_to_str(body.tag_ids) if body.tag_ids is not None else None
    try:
        action = action_use_cases.update_action(
            action_id,
            current_user.tenant_id,
            body.method,
            body.path,
            body.name,
            body.request_config,
            body.input_schema_json,
            body.input_schema_version,
            tag_ids_str,
            repo,
            tag_repo,
        )
        db.commit()
    except ActionNotFoundError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found",
        )
    except TagNotFoundError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    tag_ids = repo.get_action_tag_ids(action.id)
    return action_to_response(action, tag_ids=tag_ids)


@router.delete("/actions/{action_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_action(
    action_id: str,
    current_user: Annotated[CurrentUser, Depends(require_admin)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """Delete action; 404 if not in current tenant."""
    repo = ActionRepositoryImpl(db)
    try:
        action_use_cases.delete_action(action_id, current_user.tenant_id, repo)
    except ActionNotFoundError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found",
        )
    db.commit()
    return None
