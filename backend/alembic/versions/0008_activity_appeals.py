"""新增异常运动申诉记录。"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0008_activity_appeals"
down_revision = "0007_checkpoint_visits"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if not inspector.has_table("activity_appeals"):
        op.create_table(
            "activity_appeals",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("activity_id", sa.Integer(), sa.ForeignKey("activities.id"), nullable=False),
            sa.Column("student_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("reason", sa.String(length=500), nullable=False),
            sa.Column("status", sa.String(length=16), nullable=False, server_default="pending"),
            sa.Column("reviewed_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("review_comment", sa.String(length=500), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("reviewed_at", sa.DateTime(), nullable=True),
            sa.UniqueConstraint("activity_id", name="uq_activity_appeal_activity"),
        )
    inspector = inspect(bind)
    indexes = {row["name"] for row in inspector.get_indexes("activity_appeals")}
    for name, cols in (
        ("ix_activity_appeals_student_created", ["student_id", "created_at"]),
        ("ix_activity_appeals_status_created", ["status", "created_at"]),
    ):
        if name not in indexes:
            op.create_index(name, "activity_appeals", cols)


def downgrade() -> None:
    op.drop_table("activity_appeals")
