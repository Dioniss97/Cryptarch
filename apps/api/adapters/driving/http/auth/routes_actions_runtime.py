"""Authenticated endpoints for action schema read and sync stub execute."""
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from adapters.driven.persistence.action_repository import ActionRepositoryImpl
from adapters.driven.persistence.permission_query import PermissionQueryImpl
from core.application import action_runtime as action_runtime_use_cases
from core.domain.input_schema import PayloadValidationError
from dependencies import CurrentUser, get_current_user, get_db

router = APIRouter(tags=["actions"])


class ExecuteActionBody(BaseModel):
    payload: dict[str, Any] = Field(default_factory=dict)


@router.get("/actions/{action_id}/input-schema")
def get_action_input_schema(
    action_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    action_repo = ActionRepositoryImpl(db)
    permission_query = PermissionQueryImpl(db)
    try:
        return action_runtime_use_cases.get_action_input_schema(
            action_id=action_id,
            tenant_id=current_user.tenant_id,
            user_id=current_user.sub,
            action_repo=action_repo,
            permission_query=permission_query,
        )
    except action_runtime_use_cases.ActionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found",
        )
    except action_runtime_use_cases.ActionForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action not allowed",
        )


@router.post("/actions/{action_id}/execute")
def execute_action(
    action_id: str,
    body: ExecuteActionBody,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    action_repo = ActionRepositoryImpl(db)
    permission_query = PermissionQueryImpl(db)
    try:
        return action_runtime_use_cases.execute_action(
            action_id=action_id,
            tenant_id=current_user.tenant_id,
            user_id=current_user.sub,
            payload=body.payload,
            action_repo=action_repo,
            permission_query=permission_query,
        )
    except action_runtime_use_cases.ActionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found",
        )
    except action_runtime_use_cases.ActionForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action not allowed",
        )
    except PayloadValidationError as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=action_runtime_use_cases.build_validation_error(exc),
        )
