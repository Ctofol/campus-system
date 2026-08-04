"""为任务和课程增加可追溯的归档生命周期。"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0012_content_lifecycle"
down_revision = "0011_account_status"
branch_labels = None
depends_on = None


def _add_lifecycle(table: str) -> None:
    bind = op.get_bind()
    columns = {row["name"] for row in inspect(bind).get_columns(table)}
    with op.batch_alter_table(table) as batch:
        if "lifecycle_status" not in columns:
            batch.add_column(sa.Column("lifecycle_status", sa.String(length=16), nullable=False, server_default="published"))
        if "archived_at" not in columns:
            batch.add_column(sa.Column("archived_at", sa.DateTime(), nullable=True))
    indexes = {row["name"] for row in inspect(bind).get_indexes(table)}
    index_name = f"ix_{table}_lifecycle_status"
    if index_name not in indexes:
        op.create_index(index_name, table, ["lifecycle_status"])


def upgrade() -> None:
    _add_lifecycle("tasks")
    _add_lifecycle("courses")


def downgrade() -> None:
    for table in ("courses", "tasks"):
        indexes = {row["name"] for row in inspect(op.get_bind()).get_indexes(table)}
        index_name = f"ix_{table}_lifecycle_status"
        if index_name in indexes:
            op.drop_index(index_name, table_name=table)
        columns = {row["name"] for row in inspect(op.get_bind()).get_columns(table)}
        with op.batch_alter_table(table) as batch:
            for name in ("archived_at", "lifecycle_status"):
                if name in columns:
                    batch.drop_column(name)
