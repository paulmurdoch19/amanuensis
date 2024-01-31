"""require value for role

Revision ID: 57bc0c5a9733
Revises: 40b00996555e
Create Date: 2024-01-31 14:09:20.480237

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '57bc0c5a9733'
down_revision = '40b00996555e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('project_has_associated_user', 'role_id', nullable=False)


def downgrade() -> None:
    op.alter_column('project_has_associated_user', 'role_id', nullable=True)
