"""populate currencies

Revision ID: 000602394677
Revises: 0b6f1fd5879f
Create Date: 2025-07-02 16:43:12.345284

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '000602394677'
down_revision: Union[str, None] = '0b6f1fd5879f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
