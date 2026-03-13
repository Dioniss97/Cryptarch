"""Auth HTTP routes: login, logout. Uses core.application.auth and JWT in driving layer."""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from sqlalchemy.orm import Session

from adapters.driven.persistence.password_hasher import PasswordHasherImpl
from adapters.driven.persistence.user_repository import UserRepositoryImpl
from adapters.driving.schemas.auth import LoginBody, TokenResponse
from config import JWT_ALGORITHM, JWT_SECRET
from core.application import auth as auth_use_cases
from dependencies import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


def _create_token(user) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user.id,
        "tenant_id": user.tenant_id,
        "role": user.role,
        "exp": now + timedelta(hours=24),
        "iat": now,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginBody, db: Session = Depends(get_db)):
    user_repo = UserRepositoryImpl(db)
    password_hasher = PasswordHasherImpl()
    user = auth_use_cases.login(
        body.tenant_id, body.email, body.password, user_repo, password_hasher
    )
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(access_token=_create_token(user))


@router.post("/logout", status_code=204)
def logout():
    """JWT is stateless; client should discard the token. Returns 204."""
    return None
