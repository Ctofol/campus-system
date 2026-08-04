"""新增关键操作审计日志。"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0003_audit_logs"
down_revision = "0002_query_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = inspect(op.get_bind())
    if not inspector.has_table("audit_logs"):
        op.create_table(
            "audit_logs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("action", sa.String(length=64), nullable=False),
            sa.Column("resource_type", sa.String(length=64), nullable=False),
            sa.Column("resource_id", sa.String(length=64), nullable=True),
            sa.Column("detail", sa.String(length=1024), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )

    existing_indexes = {
        item["name"] for item in inspect(op.get_bind()).get_indexes("audit_logs")
    }
    if "ix_audit_logs_actor_created" not in existing_indexes:
        op.create_index(
            "ix_audit_logs_actor_created",
            "audit_logs",
            ["actor_user_id", "created_at"],
        )
    if "ix_audit_logs_resource" not in existing_indexes:
        op.create_index(
            "ix_audit_logs_resource",
            "audit_logs",
            ["resource_type", "resource_id"],
        )


def downgrade() -> None:
    op.drop_index("ix_audit_logs_resource", table_name="audit_logs")
    op.drop_index("ix_audit_logs_actor_created", table_name="audit_logs")
    op.drop_table("audit_logs")
