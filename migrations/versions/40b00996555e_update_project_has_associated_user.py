"""update project_has_associated_user

Revision ID: 40b00996555e
Revises: 72936c3fdac6
Create Date: 2023-11-03 11:10:23.808252

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import logging
# revision identifiers, used by Alembic.
revision = '40b00996555e'
down_revision = '72936c3fdac6'
branch_labels = None
depends_on = None

logger = logging.getLogger("amanuensis.alembic")

def upgrade() -> None:
    logger.warn("userporataldatamodel must be at version (FILL IN) or greater")
    op.add_column("project_has_associated_user", sa.Column('role_id', sa.Integer, sa.ForeignKey('associated_user_roles.id')))
    op.drop_column("project_has_associated_user", 'role')

def downgrade() -> None:
    logger.warn("userportaldatamodel must be at version 1.5.0 or less")
    op.add_column("project_has_associated_user", sa.Column('role', sa.Text, nullable=False, default='METADATA_ACCESS'))
    op.drop_column("project_has_associated_user", 'role_id')
