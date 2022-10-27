"""Add search snapshot

Revision ID: b1c926c2d318
Revises: 03ceab80c865
Create Date: 2022-08-12 19:25:41.315459

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b1c926c2d318"
down_revision = "03ceab80c865"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "search_is_shared",
        sa.Column("search_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("write_access", sa.Boolean(), nullable=True),
        sa.Column("delete_access", sa.Boolean(), nullable=True),
        sa.Column("shareable_token", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(
            ["search_id"],
            ["search.id"],
        ),
        sa.PrimaryKeyConstraint("search_id", "user_id"),
    )
    op.add_column("search", sa.Column("is_snapshot", sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column("search", "is_snapshot")
    op.drop_table("search_is_shared")
