"""Auth request/response schemas."""
from pydantic import BaseModel


class LoginBody(BaseModel):
    tenant_id: str
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
