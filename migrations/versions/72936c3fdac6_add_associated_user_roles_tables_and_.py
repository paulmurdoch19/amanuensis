"""add associated user roles tables and data and update project has associated user

Revision ID: 72936c3fdac6
Revises: 09a38764b3a0
Create Date: 2023-10-05 12:58:29.304829

"""
from alembic import op
import sqlalchemy as sa
from userportaldatamodel.models import AssociatedUserRoles
from sqlalchemy.orm import Session

# revision identifiers, used by Alembic.
revision = '72936c3fdac6'
down_revision = '09a38764b3a0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table('project_has_associated_user')

    op.create_table(
        'associated_user_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('create_date', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('update_date', sa.DateTime(), nullable=False, server_default=sa.text('NOW()'), onupdate=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        "project_has_associated_user",
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("associated_user_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column(
            "create_date",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "update_date",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["associated_user_id"],
            ["associated_user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["project.id"],
        ),
        sa.PrimaryKeyConstraint("project_id", "associated_user_id"),
    )

    conn = op.get_bind()
    session = Session(bind=conn)
    roles = []

    roles.append(AssociatedUserRoles(role="DATA_ACCESS", code="DATA_ACCESS"))
    roles.append(AssociatedUserRoles(role="METADATA_ACCESS", code="METADATA_ACCESS"))
    
    session.add_all(roles)


    session.commit()


def downgrade() -> None:
    op.drop_table('associated_user_roles')
    op.drop_table('project_has_associated_user')
    op.create_table(
        "project_has_associated_user",
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("associated_user_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column(
            "create_date",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "update_date",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["associated_user_id"],
            ["associated_user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["project.id"],
        ),
        sa.PrimaryKeyConstraint("project_id", "associated_user_id"),
    )
