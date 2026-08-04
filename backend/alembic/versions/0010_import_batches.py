"""新增导入批次跟踪与受限回滚记录。"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0010_import_batches"
down_revision = "0009_run_group_safety"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    user_columns = {row["name"] for row in inspect(bind).get_columns("users")}
    if "staff_id" not in user_columns:
        with op.batch_alter_table("users") as batch:
            batch.add_column(sa.Column("staff_id", sa.String(length=64), nullable=True))
    bind.execute(sa.text("UPDATE users SET staff_id = student_id, student_id = NULL WHERE role = 'teacher' AND staff_id IS NULL"))
    user_indexes = {row["name"] for row in inspect(bind).get_indexes("users")}
    if "ix_users_staff_id" not in user_indexes:
        op.create_index("ix_users_staff_id", "users", ["staff_id"], unique=True)
    if not inspect(bind).has_table("import_batches"):
        op.create_table(
            "import_batches",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("import_type", sa.String(length=16), nullable=False),
            sa.Column("filename", sa.String(length=255), nullable=True),
            sa.Column("status", sa.String(length=16), nullable=False, server_default="completed"),
            sa.Column("total_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("success_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("failed_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("errors", sa.String(length=4000), nullable=True),
            sa.Column("created_user_ids", sa.String(length=4000), nullable=True),
            sa.Column("created_profile_ids", sa.String(length=4000), nullable=True),
            sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("rolled_back_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("rolled_back_at", sa.DateTime(), nullable=True),
        )
    indexes = {row["name"] for row in inspect(bind).get_indexes("import_batches")}
    for name, cols in (
        ("ix_import_batches_created", ["created_at"]),
        ("ix_import_batches_type_status", ["import_type", "status"]),
    ):
        if name not in indexes:
            op.create_index(name, "import_batches", cols)


def downgrade() -> None:
    op.drop_table("import_batches")
    op.drop_index("ix_users_staff_id", table_name="users")
    with op.batch_alter_table("users") as batch:
        batch.drop_column("staff_id")
