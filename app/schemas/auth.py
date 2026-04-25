import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class SupplierRegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=6, max_length=128)
    organization_name: str = Field(..., min_length=1, max_length=255)
    gst_number: str | None = Field(None, max_length=20)


class LoginRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=128)


class UserResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    role: str
    name: str
    phone: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
