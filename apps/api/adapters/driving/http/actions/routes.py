"""User routes: permitted actions (non-admin)."""

from typing import Annotated

from core.application import user_action_list
from dependencies import CurrentUser, get_current_user, get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from adapters.driven.persistence.action_repository import ActionRepositoryImpl
from adapters.driven.persistence.permission_query import PermissionQueryImpl
from adapters.driving.schemas.user_action import permitted_action_summary_to_response

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
