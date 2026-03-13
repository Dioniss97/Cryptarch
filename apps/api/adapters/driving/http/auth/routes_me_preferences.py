"""Authenticated user endpoints for personal preferences."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from adapters.driven.persistence.user_preferences_repository import (
    UserPreferencesRepositoryImpl,
)
from adapters.driving.schemas.user_preferences import (
    UserPreferencesPatchBody,
    to_response,
    validate_allowed_values,
)
from core.application import user_preferences as user_preferences_use_cases
from dependencies import CurrentUser, get_current_user, get_db

router = APIRouter(tags=["me"])


@router.get("/me/preferences")
def get_me_preferences(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    repo = UserPreferencesRepositoryImpl(db)
    data = user_preferences_use_cases.get_user_preferences(
        current_user.tenant_id, current_user.sub, repo
    )
    return to_response(data)


@router.patch("/me/preferences")
def patch_me_preferences(
    body: UserPreferencesPatchBody,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    try:
        validate_allowed_values(body)
        repo = UserPreferencesRepositoryImpl(db)
        updated = user_preferences_use_cases.set_user_preferences(
            current_user.tenant_id,
            current_user.sub,
            repo,
            language=body.language,
            theme=body.theme,
            table_density=body.table_density,
            metadata=body.metadata,
        )
        db.commit()
        return to_response(updated)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
