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
    }

    with database.engine.begin() as conn:
        if inspector.has_table("users"):
            existing = _column_names(inspector, "users")
            for col, typ in user_cols.items():
                if col not in existing:
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} {typ}"))

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
