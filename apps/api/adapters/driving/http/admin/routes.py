"""Single admin router: assembles all admin sub-routers and GET /admin/me."""
from typing import Annotated

from fastapi import APIRouter, Depends

from dependencies import CurrentUser, require_admin

from . import (
    routes_actions,
    routes_connectors,
    routes_documents,
    routes_filters,
    routes_groups,
    routes_tags,
    routes_users,
)

# Router for GET /admin/me (current user info)
_me_router = APIRouter(prefix="/admin", tags=["admin"])


@_me_router.get("/me", response_model=CurrentUser)
def admin_me(
    current_user: Annotated[CurrentUser, Depends(require_admin)],
) -> CurrentUser:
    """Return current admin user: sub, tenant_id, role."""
    return current_user


# Assembled admin router (no prefix): includes /admin/me and all resource routers
router = APIRouter()
router.include_router(_me_router)
router.include_router(routes_users.router)
router.include_router(routes_tags.router)
router.include_router(routes_filters.router)
router.include_router(routes_groups.router)
router.include_router(routes_connectors.router)
router.include_router(routes_actions.router)
router.include_router(routes_documents.router)
