"""补全健康报备审核、取消和结束生命周期。"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0006_health_request_lifecycle"
down_revision = "0005_notification_system"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {row["name"] for row in inspector.get_columns("health_requests")}
    additions = (
        ("reviewed_by", sa.Column("reviewed_by", sa.Integer(), sa.ForeignKey("users.id", name="fk_health_request_reviewer"), nullable=True)),
        ("reviewed_at", sa.Column("reviewed_at", sa.DateTime(), nullable=True)),
        ("review_comment", sa.Column("review_comment", sa.String(length=500), nullable=True)),
        ("cancelled_at", sa.Column("cancelled_at", sa.DateTime(), nullable=True)),
        ("ended_at", sa.Column("ended_at", sa.DateTime(), nullable=True)),
    )
    with op.batch_alter_table("health_requests") as batch:
        for name, column in additions:
            if name not in columns:
                batch.add_column(column)

    inspector = inspect(bind)
    indexes = {row["name"] for row in inspector.get_indexes("health_requests")}
    for name, cols in (
        ("ix_health_requests_status", ["status"]),
        ("ix_health_requests_student_status", ["student_id", "status"]),
        ("ix_health_requests_expiry", ["status", "type", "end_date"]),
    ):
        if name not in indexes:
            op.create_index(name, "health_requests", cols)


def downgrade() -> None:
    for name in ("ix_health_requests_expiry", "ix_health_requests_student_status", "ix_health_requests_status"):
        op.drop_index(name, table_name="health_requests")
    with op.batch_alter_table("health_requests") as batch:
        for name in ("ended_at", "cancelled_at", "review_comment", "reviewed_at", "reviewed_by"):
            batch.drop_column(name)
