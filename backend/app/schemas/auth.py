from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    full_name: str | None = Field(default=None, max_length=120)
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
class AccountResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str | None
    model_config = {"from_attributes": True}
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    account: AccountResponse
