"""user_id added in package as foreign key

Revision ID: 589795a5773a
Revises: 99bc153be730
Create Date: 2025-06-25 10:35:24.238342
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '589795a5773a'
down_revision: Union[str, None] = '99bc153be730'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Add column as nullable
    op.add_column('packages', sa.Column('user_id', sa.Integer(), nullable=True))

    # Step 2: Assign a valid user_id to existing rows
    op.execute("UPDATE packages SET user_id = 1")  # Ensure user with ID 1 exists

    # Step 3: Make column NOT NULL
    op.alter_column('packages', 'user_id', nullable=False)

    # Step 4: Add foreign key constraint
    op.create_foreign_key('fk_packages_user_id', 'packages', 'users', ['user_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_packages_user_id', 'packages', type_='foreignkey')
    op.drop_column('packages', 'user_id')
