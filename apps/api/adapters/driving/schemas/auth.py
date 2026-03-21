"""Auth request/response schemas."""

from pydantic import BaseModel
from shared_contract import TOKEN_TYPE_BEARER


class LoginBody(BaseModel):
    tenant_id: str
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = TOKEN_TYPE_BEARER
