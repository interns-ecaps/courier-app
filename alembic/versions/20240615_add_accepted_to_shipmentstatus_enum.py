"""
Add 'accepted' value to shipmentstatus enum
"""
from alembic import op

def upgrade():
    op.execute("ALTER TYPE shipmentstatus ADD VALUE IF NOT EXISTS 'accepted';")

def downgrade():
    # Downgrade is not supported for enum value removal
    pass 