import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class RetailerCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=10, max_length=20)
    pin: str = Field(..., min_length=4, max_length=4, pattern=r"^\d{4}$")
    shop_name: str = Field(..., min_length=1, max_length=255)
    address: str | None = None
    credit_limit: Decimal = Field(default=Decimal("0.00"), ge=0)


class RetailerUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    phone: str | None = Field(None, min_length=10, max_length=20)
    pin: str | None = Field(None, min_length=4, max_length=4, pattern=r"^\d{4}$")
    shop_name: str | None = Field(None, min_length=1, max_length=255)
    address: str | None = None
    credit_limit: Decimal | None = Field(None, ge=0)
    is_active: bool | None = None


class RetailerResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID
    shop_name: str
    address: str | None
    credit_limit: Decimal
    outstanding: Decimal
    created_at: datetime
    user_name: str
    user_phone: str
    is_active: bool

    model_config = {"from_attributes": True}


class RetailerListResponse(BaseModel):
    items: list[RetailerResponse]
    total: int
