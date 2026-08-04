"""增加跑团归档状态与活动报名唯一约束。"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


revision = "0009_run_group_safety"
down_revision = "0008_activity_appeals"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {row["name"] for row in inspector.get_columns("run_groups")}
    with op.batch_alter_table("run_groups") as batch:
        if "status" not in columns:
            batch.add_column(sa.Column("status", sa.String(length=16), nullable=False, server_default="active"))
        if "archived_at" not in columns:
            batch.add_column(sa.Column("archived_at", sa.DateTime(), nullable=True))

    # 历史重复报名只保留最早一条，随后由数据库保证并发唯一性。
    bind.execute(text("""
        DELETE FROM run_group_activity_applications
        WHERE id NOT IN (
            SELECT MIN(id) FROM run_group_activity_applications GROUP BY activity_id, user_id
        )
    """))
    inspector = inspect(bind)
    indexes = {row["name"] for row in inspector.get_indexes("run_group_activity_applications")}
    if "uq_run_group_activity_application" not in indexes:
        op.create_index(
            "uq_run_group_activity_application",
            "run_group_activity_applications",
            ["activity_id", "user_id"],
            unique=True,
        )
    group_indexes = {row["name"] for row in inspect(bind).get_indexes("run_groups")}
    if "ix_run_groups_status" not in group_indexes:
        op.create_index("ix_run_groups_status", "run_groups", ["status"])


def downgrade() -> None:
    op.drop_index("uq_run_group_activity_application", table_name="run_group_activity_applications")
    op.drop_index("ix_run_groups_status", table_name="run_groups")
    with op.batch_alter_table("run_groups") as batch:
        batch.drop_column("archived_at")
        batch.drop_column("status")
