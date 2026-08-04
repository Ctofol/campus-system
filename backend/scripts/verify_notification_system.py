"""只读核对通知系统迁移结果，不修改任何业务数据。"""

import json
import sys
from pathlib import Path

from sqlalchemy import inspect, text

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import engine


def main() -> None:
    inspector = inspect(engine)
    notification_columns = {row["name"] for row in inspector.get_columns("user_notifications")}
    required = {
        "campaign_id", "sender_user_id", "source_type", "source_id",
        "action_type", "action_payload", "event_key", "read_at",
    }
    has_campaign_table = inspector.has_table("notification_campaigns")
    with engine.connect() as connection:
        result = {
            "version": connection.execute(text("select version_num from alembic_version")).scalar(),
            "history_count": connection.execute(text("select count(id) from user_notifications")).scalar(),
            "campaign_count": connection.execute(text("select count(id) from notification_campaigns")).scalar() if has_campaign_table else None,
            "campaign_table": has_campaign_table,
            "required_columns": sorted(required & notification_columns),
            "missing_columns": sorted(required - notification_columns),
        }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
