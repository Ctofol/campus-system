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
    }
    activity_cols = {
        "face_liveness_pass": "INTEGER" if dialect == "sqlite" else "BOOLEAN",
        "face_match_score": "REAL" if dialect == "sqlite" else "FLOAT",
        "face_fail_code": "VARCHAR(64)",
    }
    metrics_cols = {
        "exercise_type": "VARCHAR(32)",
        "analysis_status": "VARCHAR(32)",
        "analysis_error": "VARCHAR(512)",
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

    if dialect == "sqlite":
        # SQLite 无 BOOLEAN，上面已按 BOOLEAN 添加，通常映射为 INTEGER
        pass
