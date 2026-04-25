import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class InvoiceResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    order_id: uuid.UUID
    invoice_no: str
    total: Decimal
    pdf_path: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
