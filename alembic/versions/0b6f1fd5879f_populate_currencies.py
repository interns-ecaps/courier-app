"""populate currencies

Revision ID: 0b6f1fd5879f
Revises: ce310b9ef265
Create Date: 2025-07-02 16:25:24.037796

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0b6f1fd5879f'
down_revision: Union[str, None] = 'ce310b9ef265'
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