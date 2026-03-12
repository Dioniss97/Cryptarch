"""Admin-only routes. All require admin role via require_admin dependency."""
from fastapi import APIRouter, Depends

from dependencies import CurrentUser, require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/me")
def admin_me(current_user: CurrentUser = Depends(require_admin)):
    """Current admin user info from JWT. Used to verify admin guard."""
    return {
        "sub": current_user.sub,
        "tenant_id": current_user.tenant_id,
        "role": current_user.role,
    }
