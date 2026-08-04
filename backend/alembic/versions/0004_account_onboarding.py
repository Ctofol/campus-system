"""新增账号首次完善、昵称和令牌版本字段。"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0004_account_onboarding"
down_revision = "0003_audit_logs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    columns = {item["name"]: item for item in inspect(bind).get_columns("users")}

    with op.batch_alter_table("users") as batch:
        if "nickname" not in columns:
            batch.add_column(sa.Column("nickname", sa.String(length=32), nullable=True))
        if "must_change_password" not in columns:
            batch.add_column(
                sa.Column(
                    "must_change_password",
                    sa.Boolean(),
                    nullable=False,
                    server_default=sa.false(),
                )
            )
        if "token_version" not in columns:
            batch.add_column(
                sa.Column(
                    "token_version",
                    sa.Integer(),
                    nullable=False,
                    server_default="0",
                )
            )
        if "phone" in columns and not columns["phone"].get("nullable", True):
            batch.alter_column("phone", existing_type=sa.String(), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.alter_column("phone", existing_type=sa.String(), nullable=False)
        batch.drop_column("token_version")
        batch.drop_column("must_change_password")
        batch.drop_column("nickname")
