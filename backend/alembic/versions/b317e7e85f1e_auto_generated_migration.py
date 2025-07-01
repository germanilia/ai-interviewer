"""Add QUESTION_EVALUATION to PromptType enum

Revision ID: b317e7e85f1e
Revises: 31917c56d930
Create Date: 2025-07-01 11:59:20.699664

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b317e7e85f1e'
down_revision = '31917c56d930'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add the new enum value to the existing prompttype enum
    op.execute("ALTER TYPE prompttype ADD VALUE 'QUESTION_EVALUATION'")


def downgrade() -> None:
    # Note: PostgreSQL doesn't support removing enum values directly
    # This would require recreating the enum and updating all references
    pass
