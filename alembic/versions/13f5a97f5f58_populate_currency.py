"""populate_currency

Revision ID: 13f5a97f5f58
Revises: f51d623441b6
Create Date: 2025-07-07 13:07:37.556767

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '13f5a97f5f58'
down_revision: Union[str, None] = 'f51d623441b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


currencies = [
    {"code": "USD"},
    {"code": "EUR"},
    {"code": "GBP"},
    {"code": "INR"},
    {"code": "JPY"},
    {"code": "CNY"},
    {"code": "AUD"},
    {"code": "CAD"},
    {"code": "CHF"},
    {"code": "SGD"},
    {"code": "HKD"},
    {"code": "NZD"},
    {"code": "SEK"},
    {"code": "KRW"},
    {"code": "ZAR"},
    {"code": "BRL"},
    {"code": "MXN"},
    {"code": "IDR"},
    {"code": "TRY"},
    {"code": "RUB"},
    {"code": "SAR"},
    {"code": "AED"},
    {"code": "PLN"},
    {"code": "NOK"},
    {"code": "THB"},
    {"code": "MYR"},
    {"code": "PHP"},
    {"code": "VND"},
    {"code": "BDT"},
    {"code": "PKR"},
    {"code": "EGP"},
    {"code": "KWD"},
    {"code": "QAR"},
    {"code": "DZD"},
    {"code": "MAD"},
    {"code": "NGN"},
    {"code": "KES"},
    {"code": "GHS"},
    {"code": "TZS"}
]

def upgrade() -> None:
    connection = op.get_bind()
    for currency in currencies:
        connection.execute(
    sa.text(
        "INSERT INTO currency (currency, is_deleted) VALUES (:currency, :is_deleted)"
    ),
    {"currency": currency["code"], "is_deleted": False}
)

def downgrade() -> None:
    connection = op.get_bind()
    for currency in currencies:
        connection.execute(
            sa.text(
                "DELETE FROM currency WHERE currency = :currency"
            ),
            {"currency": currency}
        )