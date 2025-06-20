"""location type changed

Revision ID: 353a0ac9de2f
Revises: 310f9b32a70b
Create Date: 2025-06-20 17:48:39.400275
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '353a0ac9de2f'
down_revision: Union[str, None] = '310f9b32a70b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop existing foreign key constraint before altering column
    op.drop_constraint(
        'status_tracker_current_location_fkey',
        'status_tracker',
        type_='foreignkey'
    )
    # Alter column type from Integer to String
    op.alter_column(
        'status_tracker',
        'current_location',
        existing_type=sa.Integer(),
        type_=sa.String(length=100),
        existing_nullable=True,
    )
    # (Optional) add a new foreign key constraint if desired, pointing to a string PK
    # op.create_foreign_key(
    #     'status_tracker_current_location_fkey',
    #     'status_tracker',
    #     'some_table',
    #     ['current_location'],
    #     ['some_string_key']
    # )


def downgrade() -> None:
    # Drop any new constraint if created
    # op.drop_constraint(
    #     'status_tracker_current_location_fkey',
    #     'status_tracker',
    #     type_='foreignkey'
    # )
    # Alter column back to Integer
    op.alter_column(
        'status_tracker',
        'current_location',
        existing_type=sa.String(length=100),
        type_=sa.Integer(),
        existing_nullable=True,
    )
    # Recreate the old foreign key constraint
    op.create_foreign_key(
        'status_tracker_current_location_fkey',
        'status_tracker',
        'addresses',
        ['current_location'],
        ['id'],
    )
