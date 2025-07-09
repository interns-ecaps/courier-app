"""razorpay column

Revision ID: ad97dd983bf0
Revises: 13f5a97f5f58
Create Date: 2025-07-09 16:34:14.798581

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ad97dd983bf0'
down_revision: Union[str, None] = '13f5a97f5f58'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('payments', sa.Column('razorpay_order_id', sa.String(length=255), nullable=True))
    op.add_column('payments', sa.Column('razorpay_payment_id', sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column('payments', 'razorpay_payment_id')
    op.drop_column('payments', 'razorpay_order_id')