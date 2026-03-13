"""FastAPI dependencies: get_db, auth, etc."""
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel

from adapters.driven.persistence.db import get_db
from config import JWT_ALGORITHM, JWT_SECRET


class CurrentUser(BaseModel):
    sub: str
    tenant_id: str
    role: str


def get_current_user(
    authorization: str | None = Header(None, alias="Authorization"),
) -> CurrentUser:
    """Extract and validate JWT from Authorization: Bearer <token>. Raises 401 if missing or invalid."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )
    token = authorization[7:].strip()
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        sub = payload.get("sub")
        tenant_id = payload.get("tenant_id")
        role = payload.get("role")
        if not sub or not tenant_id or not role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        return CurrentUser(sub=sub, tenant_id=tenant_id, role=role)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def require_admin(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> CurrentUser:
    """Require role admin; raises 403 for non-admin."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return current_user
