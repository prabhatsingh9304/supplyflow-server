import asyncio
import logging
import os
import uuid
from datetime import datetime
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


INVOICE_DIR = "/app/invoices"
INVOICE_TTL_SECONDS = 300

logger = logging.getLogger(__name__)


def schedule_pdf_cleanup(filepath: str) -> None:
    """Schedule deletion of a PDF file after INVOICE_TTL_SECONDS."""
    loop = asyncio.get_event_loop()
    loop.call_later(INVOICE_TTL_SECONDS, _delete_file, filepath)


def _delete_file(filepath: str) -> None:
    try:
        os.remove(filepath)
        logger.info("Deleted invoice PDF: %s", filepath)
    except OSError as e:
        logger.warning("Failed to delete invoice PDF %s: %s", filepath, e)


def generate_invoice_pdf(
    invoice_no: str,
    org_name: str,
    org_phone: str,
    org_gst: str | None,
    org_address: str | None,
    order_date: datetime,
    retailer_name: str,
    retailer_shop: str,
    retailer_address: str | None,
    retailer_phone: str,
    items: list[dict],
    subtotal: Decimal,
    tax: Decimal,
    total: Decimal,
) -> str:
    os.makedirs(INVOICE_DIR, exist_ok=True)
    filename = f"{invoice_no}_{uuid.uuid4().hex[:8]}.pdf"
    filepath = os.path.join(INVOICE_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"<b>{org_name}</b>", styles["Title"]))
    if org_gst:
        elements.append(Paragraph(f"GST: {org_gst}", styles["Normal"]))
    elements.append(Paragraph(f"Phone: {org_phone}", styles["Normal"]))
    if org_address:
        elements.append(Paragraph(f"Address: {org_address}", styles["Normal"]))
    elements.append(Paragraph(f"Date: {order_date.strftime('%d %b %Y')}", styles["Normal"]))
    elements.append(Spacer(1, 10 * mm))

    elements.append(Paragraph(f"<b>Invoice: {invoice_no}</b>", styles["Heading2"]))
    elements.append(Paragraph(f"To: {retailer_name} — {retailer_shop}", styles["Normal"]))
    elements.append(Paragraph(f"Phone: {retailer_phone}", styles["Normal"]))
    if retailer_address:
        elements.append(Paragraph(f"Address: {retailer_address}", styles["Normal"]))
    elements.append(Spacer(1, 8 * mm))

    table_data = [["#", "Product", "Qty", "Price", "GST %", "Amount"]]
    for i, item in enumerate(items, 1):
        line_amount = item["price"] * item["qty"]
        table_data.append([
            str(i),
            item["name"],
            str(item["qty"]),
            f'{item["price"]:.2f}',
            f'{item["gst_percent"]:.1f}%',
            f"{line_amount:.2f}",
        ])

    table_data.append(["", "", "", "", "Subtotal", f"{subtotal:.2f}"])
    table_data.append(["", "", "", "", "Tax", f"{tax:.2f}"])
    table_data.append(["", "", "", "", "Total", f"{total:.2f}"])

    table = Table(table_data, colWidths=[10 * mm, 60 * mm, 15 * mm, 25 * mm, 20 * mm, 30 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -4), 0.5, colors.grey),
        ("LINEABOVE", (4, -3), (-1, -3), 1, colors.black),
        ("FONTNAME", (4, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    elements.append(table)

    doc.build(elements)
    return filepath
