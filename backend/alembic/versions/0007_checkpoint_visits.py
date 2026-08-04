"""保存校园打卡记录。"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0007_checkpoint_visits"
down_revision = "0006_health_request_lifecycle"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if not inspector.has_table("checkpoint_visits"):
        op.create_table(
            "checkpoint_visits",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("checkpoint_id", sa.Integer(), sa.ForeignKey("checkpoints.id"), nullable=False),
            sa.Column("latitude", sa.Float(), nullable=False),
            sa.Column("longitude", sa.Float(), nullable=False),
            sa.Column("distance_m", sa.Float(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
    inspector = inspect(bind)
    indexes = {row["name"] for row in inspector.get_indexes("checkpoint_visits")}
    for name, cols in (
        ("ix_checkpoint_visits_user_created", ["user_id", "created_at"]),
        ("ix_checkpoint_visits_user_checkpoint", ["user_id", "checkpoint_id", "created_at"]),
    ):
        if name not in indexes:
            op.create_index(name, "checkpoint_visits", cols)


def downgrade() -> None:
    op.drop_table("checkpoint_visits")
