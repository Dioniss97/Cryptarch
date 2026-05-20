"""User routes: permitted actions (non-admin)."""

from typing import Annotated

from core.application import user_action_execute, user_action_list
from core.application.user_action_execute import (
    ActionNotFoundError,
    ActionNotPermittedError,
)
from core.domain.input_schema_contract import ActionPayloadValidationError
from dependencies import CurrentUser, get_current_user, get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from adapters.driven.persistence.action_repository import ActionRepositoryImpl
from adapters.driven.persistence.permission_query import PermissionQueryImpl
from adapters.driving.schemas.user_action import permitted_action_summary_to_response
from adapters.driving.schemas.user_action_execute import (
    ExecuteActionBody,
    execute_action_result_to_response,
)

router = APIRouter(tags=["actions"])


@router.get("/actions")
def list_permitted_actions(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Actions allowed for the current user (effective group permissions)."""
    permission_port = PermissionQueryImpl(db)
    action_repo = ActionRepositoryImpl(db)
    rows = user_action_list.list_permitted_actions_for_user(
        current_user.tenant_id,
        current_user.sub,
        permission_port,
        action_repo,
    )
    return [permitted_action_summary_to_response(r) for r in rows]


@router.post("/actions/{action_id}/execute")
def execute_action(
    action_id: str,
    body: ExecuteActionBody,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Execute an allowed action (stub). Validates payload against input_schema_json."""
    permission_port = PermissionQueryImpl(db)
    action_repo = ActionRepositoryImpl(db)
    try:
        result = user_action_execute.execute_action_for_user(
            current_user.tenant_id,
            current_user.sub,
            action_id,
            body.payload,
            permission_port,
            action_repo,
        )
    except ActionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found",
        )
    except ActionNotPermittedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action not permitted",
        )
    except ActionPayloadValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    return execute_action_result_to_response(result)
