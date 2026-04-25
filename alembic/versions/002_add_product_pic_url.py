"""add product pic_url

Revision ID: 002
Revises: 001
Create Date: 2025-04-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("products", sa.Column("pic_url", sa.String(2048), nullable=True))


def downgrade() -> None:
    op.drop_column("products", "pic_url")
