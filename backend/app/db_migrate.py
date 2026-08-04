"""
轻量 schema 补丁：为已有 SQLite/PostgreSQL 库补充人脸与体测分析字段。
"""
from sqlalchemy import inspect, text

from . import database


def _column_names(inspector, table: str) -> set:
    return {c["name"] for c in inspector.get_columns(table)}


def ensure_schema_upgrades() -> None:
    inspector = inspect(database.engine)
    dialect = database.engine.dialect.name

    user_cols = {
        "weekly_run_goal_km": "REAL" if dialect == "sqlite" else "FLOAT",
        "signature": "VARCHAR",
        "avatar_url": "VARCHAR",
        "header_bg_url": "VARCHAR(512)",
        "nickname": "VARCHAR(32)",
        "must_change_password": "BOOLEAN NOT NULL DEFAULT 0"
        if dialect == "sqlite"
        else "BOOLEAN NOT NULL DEFAULT FALSE",
        "token_version": "INTEGER NOT NULL DEFAULT 0",
        "staff_id": "VARCHAR(64)",
    }
    activity_cols = {
        "face_liveness_pass": "INTEGER" if dialect == "sqlite" else "BOOLEAN",
        "face_match_score": "REAL" if dialect == "sqlite" else "FLOAT",
        "face_fail_code": "VARCHAR(64)",
        "face_detail": "VARCHAR",
    }
    metrics_cols = {
        "exercise_type": "VARCHAR(32)",
        "analysis_status": "VARCHAR(32)",
        "analysis_error": "VARCHAR(512)",
    }
    task_cols = {
        "video_url": "VARCHAR",
        "target_group": "VARCHAR DEFAULT 'all'",
        "class_id": "INTEGER",
        "starts_at": "DATETIME" if dialect == "sqlite" else "TIMESTAMP",
    }
    notification_cols = {
        "title": "VARCHAR(255)" if dialect == "sqlite" else "VARCHAR",
        "body": "VARCHAR",
        "ntype": "VARCHAR(64)",
        "payload": "VARCHAR",
        "is_read": "INTEGER" if dialect == "sqlite" else "BOOLEAN",
        "created_at": "DATETIME" if dialect == "sqlite" else "TIMESTAMP",
        "campaign_id": "INTEGER",
        "sender_user_id": "INTEGER",
        "source_type": "VARCHAR(32)",
        "source_id": "VARCHAR(64)",
        "action_type": "VARCHAR(32)",
        "action_payload": "VARCHAR(2000)",
        "event_key": "VARCHAR(160)",
        "read_at": "DATETIME" if dialect == "sqlite" else "TIMESTAMP",
    }
    health_request_cols = {
        "reviewed_by": "INTEGER",
        "reviewed_at": "DATETIME" if dialect == "sqlite" else "TIMESTAMP",
        "review_comment": "VARCHAR(500)",
        "cancelled_at": "DATETIME" if dialect == "sqlite" else "TIMESTAMP",
        "ended_at": "DATETIME" if dialect == "sqlite" else "TIMESTAMP",
    }
    run_group_cols = {
        "status": "VARCHAR(16) NOT NULL DEFAULT 'active'",
        "archived_at": "DATETIME" if dialect == "sqlite" else "TIMESTAMP",
    }

    with database.engine.begin() as conn:
        if inspector.has_table("users"):
            existing = _column_names(inspector, "users")
            for col, typ in user_cols.items():
                if col not in existing:
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} {typ}"))
            conn.execute(text("UPDATE users SET staff_id = student_id, student_id = NULL WHERE role = 'teacher' AND staff_id IS NULL"))

        if inspector.has_table("activities"):
            existing = _column_names(inspector, "activities")
            for col, typ in activity_cols.items():
                if col not in existing:
                    conn.execute(text(f"ALTER TABLE activities ADD COLUMN {col} {typ}"))

        if inspector.has_table("activity_metrics"):
            existing = _column_names(inspector, "activity_metrics")
            for col, typ in metrics_cols.items():
                if col not in existing:
                    conn.execute(text(f"ALTER TABLE activity_metrics ADD COLUMN {col} {typ}"))

        if inspector.has_table("tasks"):
            existing = _column_names(inspector, "tasks")
            for col, typ in task_cols.items():
                if col not in existing:
                    conn.execute(text(f"ALTER TABLE tasks ADD COLUMN {col} {typ}"))

        if inspector.has_table("user_notifications"):
            existing = _column_names(inspector, "user_notifications")
            for col, typ in notification_cols.items():
                if col not in existing:
                    conn.execute(text(f"ALTER TABLE user_notifications ADD COLUMN {col} {typ}"))

        if inspector.has_table("health_requests"):
            existing = _column_names(inspector, "health_requests")
            for col, typ in health_request_cols.items():
                if col not in existing:
                    conn.execute(text(f"ALTER TABLE health_requests ADD COLUMN {col} {typ}"))

        if inspector.has_table("run_groups"):
            existing = _column_names(inspector, "run_groups")
            for col, typ in run_group_cols.items():
                if col not in existing:
                    conn.execute(text(f"ALTER TABLE run_groups ADD COLUMN {col} {typ}"))

        if not inspector.has_table("notification_campaigns"):
            id_type = "INTEGER NOT NULL PRIMARY KEY" if dialect == "sqlite" else "SERIAL PRIMARY KEY"
            timestamp_type = "DATETIME" if dialect == "sqlite" else "TIMESTAMP"
            conn.execute(text(f"""
                CREATE TABLE notification_campaigns (
                    id {id_type},
                    title VARCHAR(60) NOT NULL,
                    body VARCHAR(500),
                    ntype VARCHAR(32) NOT NULL DEFAULT 'system',
                    sender_user_id INTEGER,
                    sender_role VARCHAR(16),
                    target_type VARCHAR(32) NOT NULL,
                    target_spec VARCHAR(2000),
                    recipient_count INTEGER NOT NULL DEFAULT 0,
                    status VARCHAR(16) NOT NULL DEFAULT 'sent',
                    created_at {timestamp_type} NOT NULL
                )
            """))

        if not inspector.has_table("checkpoint_visits"):
            id_type = "INTEGER NOT NULL PRIMARY KEY" if dialect == "sqlite" else "SERIAL PRIMARY KEY"
            timestamp_type = "DATETIME" if dialect == "sqlite" else "TIMESTAMP"
            conn.execute(text(f"""
                CREATE TABLE checkpoint_visits (
                    id {id_type},
                    user_id INTEGER NOT NULL,
                    checkpoint_id INTEGER NOT NULL,
                    latitude FLOAT NOT NULL,
                    longitude FLOAT NOT NULL,
                    distance_m FLOAT NOT NULL,
                    created_at {timestamp_type} NOT NULL
                )
            """))

        if not inspector.has_table("activity_appeals"):
            id_type = "INTEGER NOT NULL PRIMARY KEY" if dialect == "sqlite" else "SERIAL PRIMARY KEY"
            timestamp_type = "DATETIME" if dialect == "sqlite" else "TIMESTAMP"
            conn.execute(text(f"""
                CREATE TABLE activity_appeals (
                    id {id_type},
                    activity_id INTEGER NOT NULL UNIQUE,
                    student_id INTEGER NOT NULL,
                    reason VARCHAR(500) NOT NULL,
                    status VARCHAR(16) NOT NULL DEFAULT 'pending',
                    reviewed_by INTEGER,
                    review_comment VARCHAR(500),
                    created_at {timestamp_type} NOT NULL,
                    reviewed_at {timestamp_type}
                )
            """))

        if not inspector.has_table("import_batches"):
            id_type = "INTEGER NOT NULL PRIMARY KEY" if dialect == "sqlite" else "SERIAL PRIMARY KEY"
            timestamp_type = "DATETIME" if dialect == "sqlite" else "TIMESTAMP"
            conn.execute(text(f"""
                CREATE TABLE import_batches (
                    id {id_type}, import_type VARCHAR(16) NOT NULL,
                    filename VARCHAR(255), status VARCHAR(16) NOT NULL DEFAULT 'completed',
                    total_count INTEGER NOT NULL DEFAULT 0, success_count INTEGER NOT NULL DEFAULT 0,
                    failed_count INTEGER NOT NULL DEFAULT 0, errors VARCHAR(4000),
                    created_user_ids VARCHAR(4000), created_profile_ids VARCHAR(4000), created_by INTEGER,
                    created_at {timestamp_type} NOT NULL, rolled_back_by INTEGER,
                    rolled_back_at {timestamp_type}
                )
            """))

        if dialect == "sqlite":
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_notification_campaigns_created ON notification_campaigns (created_at)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_notifications_campaign ON user_notifications (campaign_id)"))
            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uq_notification_user_event ON user_notifications (user_id, event_key)"))
            if inspector.has_table("health_requests"):
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_health_requests_student_status ON health_requests (student_id, status)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_health_requests_expiry ON health_requests (status, type, end_date)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_checkpoint_visits_user_created ON checkpoint_visits (user_id, created_at)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_checkpoint_visits_user_checkpoint ON checkpoint_visits (user_id, checkpoint_id, created_at)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_activity_appeals_student_created ON activity_appeals (student_id, created_at)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_activity_appeals_status_created ON activity_appeals (status, created_at)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_run_groups_status ON run_groups (status)"))
            conn.execute(text("DELETE FROM run_group_activity_applications WHERE id NOT IN (SELECT MIN(id) FROM run_group_activity_applications GROUP BY activity_id, user_id)"))
            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uq_run_group_activity_application ON run_group_activity_applications (activity_id, user_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_import_batches_created ON import_batches (created_at)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_import_batches_type_status ON import_batches (import_type, status)"))
            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_staff_id ON users (staff_id)"))

        if not inspector.has_table("sunshine_run_rules"):
            if dialect == "sqlite":
                conn.execute(text("""
                    CREATE TABLE sunshine_run_rules (
                        id INTEGER NOT NULL PRIMARY KEY,
                        class_id INTEGER NOT NULL,
                        teacher_id INTEGER,
                        weekly_required_count INTEGER NOT NULL DEFAULT 3,
                        min_distance_km REAL NOT NULL DEFAULT 2.0,
                        min_duration_sec INTEGER NOT NULL DEFAULT 0,
                        min_pace REAL NOT NULL DEFAULT 3.0,
                        max_pace REAL NOT NULL DEFAULT 10.0,
                        enabled INTEGER NOT NULL DEFAULT 1,
                        updated_at DATETIME,
                        created_at DATETIME,
                        UNIQUE (class_id)
                    )
                """))
            else:
                conn.execute(text("""
                    CREATE TABLE sunshine_run_rules (
                        id SERIAL PRIMARY KEY,
                        class_id INTEGER NOT NULL UNIQUE,
                        teacher_id INTEGER,
                        weekly_required_count INTEGER NOT NULL DEFAULT 3,
                        min_distance_km FLOAT NOT NULL DEFAULT 2.0,
                        min_duration_sec INTEGER NOT NULL DEFAULT 0,
                        min_pace FLOAT NOT NULL DEFAULT 3.0,
                        max_pace FLOAT NOT NULL DEFAULT 10.0,
                        enabled BOOLEAN NOT NULL DEFAULT TRUE,
                        updated_at TIMESTAMP,
                        created_at TIMESTAMP
                    )
                """))

        if not inspector.has_table("student_face_profiles"):
            if dialect == "sqlite":
                conn.execute(text("""
                    CREATE TABLE student_face_profiles (
                        id INTEGER NOT NULL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        image_url VARCHAR NOT NULL,
                        embedding_json VARCHAR NOT NULL,
                        status VARCHAR(32) NOT NULL DEFAULT 'verified',
                        model_version VARCHAR(64),
                        fail_reason VARCHAR(512),
                        quality_score REAL,
                        created_at DATETIME,
                        updated_at DATETIME,
                        UNIQUE (user_id)
                    )
                """))
            else:
                conn.execute(text("""
                    CREATE TABLE student_face_profiles (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL UNIQUE,
                        image_url VARCHAR NOT NULL,
                        embedding_json VARCHAR NOT NULL,
                        status VARCHAR(32) NOT NULL DEFAULT 'verified',
                        model_version VARCHAR(64),
                        fail_reason VARCHAR(512),
                        quality_score FLOAT,
                        created_at TIMESTAMP,
                        updated_at TIMESTAMP
                    )
                """))

    if dialect == "sqlite":
        # SQLite 无 BOOLEAN，上面已按 BOOLEAN 添加，通常映射为 INTEGER
        pass
