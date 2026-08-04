"""新增通知批次、精准跳转、阅读时间与去重字段。"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0005_notification_system"
down_revision = "0004_account_onboarding"
branch_labels = None
depends_on = None


def _index_names(inspector, table: str) -> set[str]:
    return {row["name"] for row in inspector.get_indexes(table)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not inspector.has_table("notification_campaigns"):
        op.create_table(
            "notification_campaigns",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("title", sa.String(length=60), nullable=False),
            sa.Column("body", sa.String(length=500), nullable=True),
            sa.Column("ntype", sa.String(length=32), nullable=False, server_default="system"),
            sa.Column("sender_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("sender_role", sa.String(length=16), nullable=True),
            sa.Column("target_type", sa.String(length=32), nullable=False),
            sa.Column("target_spec", sa.String(length=2000), nullable=True),
            sa.Column("recipient_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("status", sa.String(length=16), nullable=False, server_default="sent"),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )

    inspector = inspect(bind)
    campaign_indexes = _index_names(inspector, "notification_campaigns")
    for name, columns in (
        ("ix_notification_campaigns_created", ["created_at"]),
        ("ix_notification_campaigns_type", ["ntype"]),
        ("ix_notification_campaigns_target", ["target_type"]),
        ("ix_notification_campaigns_sender", ["sender_user_id"]),
    ):
        if name not in campaign_indexes:
            op.create_index(name, "notification_campaigns", columns)

    columns = {row["name"] for row in inspector.get_columns("user_notifications")}
    with op.batch_alter_table("user_notifications") as batch:
        additions = (
            ("campaign_id", sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("notification_campaigns.id", name="fk_user_notifications_campaign"), nullable=True)),
            ("sender_user_id", sa.Column("sender_user_id", sa.Integer(), sa.ForeignKey("users.id", name="fk_user_notifications_sender"), nullable=True)),
            ("source_type", sa.Column("source_type", sa.String(length=32), nullable=True)),
            ("source_id", sa.Column("source_id", sa.String(length=64), nullable=True)),
            ("action_type", sa.Column("action_type", sa.String(length=32), nullable=True)),
            ("action_payload", sa.Column("action_payload", sa.String(length=2000), nullable=True)),
            ("event_key", sa.Column("event_key", sa.String(length=160), nullable=True)),
            ("read_at", sa.Column("read_at", sa.DateTime(), nullable=True)),
        )
        for name, column in additions:
            if name not in columns:
                batch.add_column(column)

    inspector = inspect(bind)
    indexes = _index_names(inspector, "user_notifications")
    for name, columns, unique in (
        ("ix_notifications_campaign", ["campaign_id"], False),
        ("ix_notifications_sender", ["sender_user_id"], False),
        ("ix_notifications_source", ["source_type", "source_id"], False),
        ("ix_notifications_user_created", ["user_id", "created_at"], False),
        ("ix_notifications_user_unread", ["user_id", "is_read", "created_at"], False),
        ("ix_notifications_campaign_read", ["campaign_id", "is_read"], False),
        ("uq_notification_user_event", ["user_id", "event_key"], True),
    ):
        if name not in indexes:
            op.create_index(name, "user_notifications", columns, unique=unique)


def downgrade() -> None:
    for name in (
        "uq_notification_user_event",
        "ix_notifications_source",
        "ix_notifications_sender",
        "ix_notifications_campaign",
        "ix_notifications_campaign_read",
        "ix_notifications_user_unread",
        "ix_notifications_user_created",
    ):
        op.drop_index(name, table_name="user_notifications")
    with op.batch_alter_table("user_notifications") as batch:
        for name in (
            "read_at", "event_key", "action_payload", "action_type",
            "source_id", "source_type", "sender_user_id", "campaign_id",
        ):
            batch.drop_column(name)
    op.drop_table("notification_campaigns")
