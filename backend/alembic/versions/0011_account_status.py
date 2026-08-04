"""新增账号停用状态并支持令牌即时失效。"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0011_account_status"
down_revision = "0010_import_batches"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    columns = {row["name"] for row in inspect(bind).get_columns("users")}
    with op.batch_alter_table("users") as batch:
        if "is_active" not in columns:
            batch.add_column(sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
        if "disabled_at" not in columns:
            batch.add_column(sa.Column("disabled_at", sa.DateTime(), nullable=True))
        if "disabled_reason" not in columns:
            batch.add_column(sa.Column("disabled_reason", sa.String(length=255), nullable=True))


def downgrade() -> None:
    columns = {row["name"] for row in inspect(op.get_bind()).get_columns("users")}
    with op.batch_alter_table("users") as batch:
        for name in ("disabled_reason", "disabled_at", "is_active"):
            if name in columns:
                batch.drop_column(name)
