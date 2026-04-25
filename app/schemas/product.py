import uuid
from decimal import Decimal

from pydantic import BaseModel, Field


class ProductCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    sku: str | None = Field(None, max_length=100)
    category: str | None = Field(None, max_length=100)
    pic_url: str | None = Field(None, max_length=2048)
    price: Decimal = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)
    gst_percent: Decimal = Field(default=Decimal("0.00"), ge=0)
    is_active: bool = True


class ProductUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    sku: str | None = Field(None, max_length=100)
    category: str | None = Field(None, max_length=100)
    pic_url: str | None = Field(None, max_length=2048)
    price: Decimal | None = Field(None, gt=0)
    gst_percent: Decimal | None = Field(None, ge=0)
    is_active: bool | None = None


class StockUpdateRequest(BaseModel):
    quantity: int = Field(..., description="Positive to add, negative to reduce")


class ProductResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    sku: str | None
    category: str | None
    pic_url: str | None
    price: Decimal
    stock: int
    gst_percent: Decimal
    is_active: bool

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
