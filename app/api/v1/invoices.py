import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_role
from app.models.user import User
from app.schemas.invoice import InvoiceResponse
from app.services import invoice as invoice_service

router = APIRouter(prefix="/api/v1/invoices", tags=["Invoices"])

SupplierUser = Annotated[User, Depends(require_role("supplier"))]


@router.post("/{order_id}/generate", response_model=InvoiceResponse, status_code=201)
async def generate_invoice(
    order_id: uuid.UUID,
    current_user: SupplierUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await invoice_service.generate_invoice(db, order_id, current_user)


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: uuid.UUID,
    current_user: SupplierUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await invoice_service.get_invoice(
        db, invoice_id, current_user.organization_id
    )


@router.get("/{invoice_id}/pdf")
async def get_invoice_pdf(
    invoice_id: uuid.UUID,
    current_user: SupplierUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    pdf_path = await invoice_service.get_invoice_pdf_path(
        db, invoice_id, current_user.organization_id
    )
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=pdf_path.split("/")[-1],
    )
