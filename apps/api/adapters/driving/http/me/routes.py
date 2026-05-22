"""Current-user routes: preferences."""

from typing import Annotated

from core.application import user_preferences as prefs_use_cases
from dependencies import CurrentUser, get_current_user, get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from adapters.driven.persistence.user_preferences_repository import (
    UserPreferencesRepositoryImpl,
)
from adapters.driving.schemas.user_preferences import (
    UserPreferencesPatchBody,
    preferences_to_response,
)

router = APIRouter(prefix="/me", tags=["me"])


@router.get("/preferences")
def get_my_preferences(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    repo = UserPreferencesRepositoryImpl(db)
    prefs = prefs_use_cases.get_preferences(
        current_user.tenant_id, current_user.sub, repo
    )
    return preferences_to_response(prefs)


@router.patch("/preferences")
def patch_my_preferences(
    body: UserPreferencesPatchBody,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    repo = UserPreferencesRepositoryImpl(db)
    prefs = prefs_use_cases.update_preferences(
        current_user.tenant_id,
        current_user.sub,
        theme=body.theme.value if body.theme is not None else None,
        language=body.language,
        table_density=body.table_density,
        metadata=body.metadata,
        repo=repo,
    )
    return preferences_to_response(prefs)
