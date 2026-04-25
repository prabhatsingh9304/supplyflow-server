import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    gst_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    users: Mapped[list["User"]] = relationship(back_populates="organization")  # noqa: F821
    retailers: Mapped[list["Retailer"]] = relationship(back_populates="organization")  # noqa: F821
    products: Mapped[list["Product"]] = relationship(back_populates="organization")  # noqa: F821
    orders: Mapped[list["Order"]] = relationship(back_populates="organization")  # noqa: F821
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="organization")  # noqa: F821
