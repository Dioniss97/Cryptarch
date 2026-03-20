"""Admin HTTP routes for Users. Uses core.application.user use cases and UserRepositoryImpl."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from adapters.driven.persistence.password_hasher import PasswordHasherImpl
from adapters.driven.persistence.user_repository import UserRepositoryImpl
from adapters.driving.schemas.user import (
    UserCreateBody,
    UserUpdateBody,
    user_to_response,
)
from core.application import user as user_use_cases
from dependencies import CurrentUser, get_db, require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users")
def list_users(
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """List users of the current tenant."""
    repo = UserRepositoryImpl(db)
    users = user_use_cases.list_users(current_user.tenant_id, repo)
    return [user_to_response(u) for u in users]


@router.get("/users/{user_id}")
def get_user(
    user_id: str,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """Get user by id; 404 if not in current tenant."""
    repo = UserRepositoryImpl(db)
    user = user_use_cases.get_user(user_id, current_user.tenant_id, repo)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_to_response(user)


@router.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(
    body: UserCreateBody,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """Create user in current tenant. tenant_id from JWT only."""
    repo = UserRepositoryImpl(db)
    password_hasher = PasswordHasherImpl()
    try:
        user = user_use_cases.create_user(
            tenant_id=current_user.tenant_id,
            email=body.email,
            role=body.role,
            password=body.password,
            repo=repo,
            password_hasher=password_hasher,
        )
        db.commit()
    except ValueError as e:
        db.rollback()
        if "already exists" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists in tenant",
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    return user_to_response(user)


@router.patch("/users/{user_id}")
def update_user(
    user_id: str,
    body: UserUpdateBody,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """Update user; 404 if not in current tenant."""
    repo = UserRepositoryImpl(db)
    password_hasher = PasswordHasherImpl()
    user = user_use_cases.update_user(
        user_id=user_id,
        tenant_id=current_user.tenant_id,
        repo=repo,
        email=body.email,
        role=body.role,
        password=body.password,
        password_hasher=password_hasher,
    )
    if user is None:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.commit()
    return user_to_response(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """Delete user; 404 if not in current tenant."""
    repo = UserRepositoryImpl(db)
    deleted = user_use_cases.delete_user(user_id, current_user.tenant_id, repo)
    if not deleted:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.commit()
    return None
