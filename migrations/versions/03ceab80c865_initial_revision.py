"""Initial revision

Amanuensis version: 0.1.3
Release version: 2.2.3

Revision ID: 03ceab80c865
Revises: 
Create Date: 2022-08-01 14:23:46.869309

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import logging
from sqlalchemy import engine_from_config
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = "03ceab80c865"
down_revision = None
branch_labels = None
depends_on = None

logger = logging.getLogger("amanuensis.alembic")


config = op.get_context().config
engine = engine_from_config(config.get_section(config.config_ini_section), prefix='sqlalchemy.')
inspector = inspect(engine)
tables = inspector.get_table_names(schema="public")

def table_does_not_exist(table):

    if table in tables:
        logger.info(f"{table} table already exists. Skipping create table.")
        return False
    logger.info(f"Creating table: {table}.")
    return True


def upgrade() -> None:
    logger.info("Initializing Amanuensis database for the first time ...")

    if table_does_not_exist("associated_user"):
        op.create_table(
            "associated_user",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("user_source", sa.String(), nullable=True),
            sa.Column("email", sa.Text(), nullable=True),
            sa.Column("active", sa.Boolean(), nullable=True),
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
            sa.PrimaryKeyConstraint("id"),
        )

    if table_does_not_exist("project_has_associated_user"):
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

    if table_does_not_exist("consortium_data_contributor"):
        op.create_table(
            "consortium_data_contributor",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("code", sa.String(), nullable=True),
            sa.Column("name", sa.String(), nullable=True),
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
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("code"),
        )

    if table_does_not_exist("input_type"):
        op.create_table(
            "input_type",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("code", sa.String(), nullable=True),
            sa.Column("function", sa.String(), nullable=True),
            sa.Column("description", sa.String(), nullable=True),
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
            sa.PrimaryKeyConstraint("id"),
        )

    if table_does_not_exist("project"):
        op.create_table(
            "project",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("name", sa.String(), nullable=True),
            sa.Column("first_name", sa.String(), nullable=True),
            sa.Column("last_name", sa.String(), nullable=True),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("user_source", sa.String(), nullable=True),
            sa.Column("institution", sa.String(), nullable=True),
            sa.Column("description", sa.String(), nullable=True),
            sa.Column("approved_url", sa.String(), nullable=True),
            sa.Column("active", sa.Boolean(), nullable=True),
            sa.Column(
                "update_date",
                sa.DateTime(),
                server_default=sa.text("now()"),
                nullable=True,
            ),
            sa.Column(
                "create_date",
                sa.DateTime(),
                server_default=sa.text("now()"),
                nullable=True,
            ),
            sa.PrimaryKeyConstraint("id"),
        )
    if table_does_not_exist("search"):
        op.create_table(
            "search",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("user_source", sa.String(), nullable=True),
            sa.Column("name", sa.String(), nullable=True),
            sa.Column("description", sa.String(), nullable=True),
            sa.Column(
                "filter_object",
                postgresql.JSONB(astext_type=sa.Text()),
                server_default=sa.text("'{}'"),
                nullable=True,
            ),
            sa.Column(
                "filter_source",
                sa.Enum("explorer", "manual", name="filtersourcetype"),
                nullable=True,
            ),
            sa.Column("filter_source_internal_id", sa.Integer(), nullable=True),
            sa.Column("ids_list", postgresql.ARRAY(sa.Text()), nullable=True),
            sa.Column(
                "graphql_object",
                postgresql.JSONB(astext_type=sa.Text()),
                server_default=sa.text("'{}'"),
                nullable=True,
            ),
            sa.Column("es_index", sa.String(length=255), nullable=True),
            sa.Column("dataset_version", sa.String(length=255), nullable=True),
            sa.Column("is_superseded_by", sa.Integer(), nullable=True),
            sa.Column("active", sa.Boolean(), nullable=True),
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
            sa.PrimaryKeyConstraint("id"),
        )

    if table_does_not_exist("state"):
        op.create_table(
            "state",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("name", sa.String(), nullable=True),
            sa.Column("code", sa.String(), nullable=True),
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
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("code"),
        )

    if table_does_not_exist("statistician"):
        op.create_table(
            "statistician",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("user_source", sa.String(), nullable=True),
            sa.Column("email", sa.Text(), nullable=True),
            sa.Column("active", sa.Boolean(), nullable=True),
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
            sa.PrimaryKeyConstraint("id"),
        )

    if table_does_not_exist("attribute_list"):

        op.create_table(
            "attribute_list",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("code", sa.String(), nullable=True),
            sa.Column("name", sa.String(), nullable=True),
            sa.Column("input_type_id", sa.Integer(), nullable=True),
            sa.Column("extra_info", sa.String(), nullable=True),
            sa.Column("extra_info_type", sa.String(), nullable=True),
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
                ["input_type_id"],
                ["input_type.id"],
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    if table_does_not_exist("project_has_search"):
        op.create_table(
            "project_has_search",
            sa.Column("project_id", sa.Integer(), nullable=False),
            sa.Column("search_id", sa.Integer(), nullable=False),
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
                ["project_id"],
                ["project.id"],
            ),
            sa.ForeignKeyConstraint(
                ["search_id"],
                ["search.id"],
            ),
            sa.PrimaryKeyConstraint("project_id", "search_id"),
        )

    if table_does_not_exist("project_has_statistician"):
        op.create_table(
            "project_has_statistician",
            sa.Column("project_id", sa.Integer(), nullable=False),
            sa.Column("statistician_id", sa.Integer(), nullable=False),
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
                ["project_id"],
                ["project.id"],
            ),
            sa.ForeignKeyConstraint(
                ["statistician_id"],
                ["statistician.id"],
            ),
            sa.PrimaryKeyConstraint("project_id", "statistician_id"),
        )

    if table_does_not_exist("request"):
        op.create_table(
            "request",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("project_id", sa.Integer(), nullable=True),
            sa.Column("consortium_data_contributor_id", sa.Integer(), nullable=True),
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
                ["consortium_data_contributor_id"],
                ["consortium_data_contributor.id"],
            ),
            sa.ForeignKeyConstraint(
                ["project_id"],
                ["project.id"],
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    if table_does_not_exist("attribute_list_value"):
        op.create_table(
            "attribute_list_value",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("value", sa.String(), nullable=True),
            sa.Column("input_type_id", sa.Integer(), nullable=False),
            sa.Column("attribute_list_id", sa.Integer(), nullable=True),
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
                ["attribute_list_id"],
                ["attribute_list.id"],
            ),
            sa.ForeignKeyConstraint(
                ["input_type_id"],
                ["input_type.id"],
            ),
            sa.PrimaryKeyConstraint("id", "input_type_id"),
        )

    if table_does_not_exist("attributes"):
        op.create_table(
            "attributes",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("attribute_list_id", sa.Integer(), nullable=True),
            sa.Column("request_id", sa.Integer(), nullable=True),
            sa.Column("value", sa.String(), nullable=True),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("user_source", sa.String(), nullable=True),
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
                ["attribute_list_id"],
                ["attribute_list.id"],
            ),
            sa.ForeignKeyConstraint(
                ["request_id"],
                ["request.id"],
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    if table_does_not_exist("message"):
        op.create_table(
            "message",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("sender_id", sa.Integer(), nullable=True),
            sa.Column("sender_source", sa.String(), nullable=True),
            sa.Column(
                "sent_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True
            ),
            sa.Column("body", sa.String(), nullable=True),
            sa.Column("request_id", sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(
                ["request_id"],
                ["request.id"],
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    if table_does_not_exist("request_has_state"):
        op.create_table(
            "request_has_state",
            sa.Column("request_id", sa.Integer(), nullable=False),
            sa.Column("state_id", sa.Integer(), nullable=False),
            sa.Column(
                "create_date",
                sa.DateTime(),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column(
                "update_date",
                sa.DateTime(),
                server_default=sa.text("now()"),
                nullable=True,
            ),
            sa.ForeignKeyConstraint(
                ["request_id"],
                ["request.id"],
            ),
            sa.ForeignKeyConstraint(
                ["state_id"],
                ["state.id"],
            ),
            sa.PrimaryKeyConstraint("request_id", "state_id", "create_date"),
        )

    if table_does_not_exist("receiver"):
        op.create_table(
            "receiver",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("receiver_id", sa.Integer(), nullable=True),
            sa.Column("receiver_source", sa.String(), nullable=True),
            sa.Column(
                "received_at",
                sa.DateTime(),
                server_default=sa.text("now()"),
                nullable=True,
            ),
            sa.Column("message_id", sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(
                ["message_id"],
                ["message.id"],
            ),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade() -> None:
    logger.info("Removing tables ...")
    op.drop_table("project_has_associated_user")
    op.drop_table("associated_user")
    op.drop_table("receiver")
    op.drop_table("request_has_state")
    op.drop_table("message")
    op.drop_table("attributes")
    op.drop_table("attribute_list_value")
    op.drop_table("request")
    op.drop_table("project_has_statistician")
    op.drop_table("project_has_search")
    op.drop_table("attribute_list")
    op.drop_table("statistician")
    op.drop_table("state")
    op.drop_table("search")
    op.drop_table("project")
    op.drop_table("input_type")
    op.drop_table("consortium_data_contributor")
    logger.info("Tables removed.")
