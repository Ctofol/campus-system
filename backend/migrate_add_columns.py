"""Add missing columns to database: activities.task_id and tasks.starts_at"""
from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    existing = [row[0] for row in conn.execute(text("PRAGMA table_info(activities)")).fetchall()]
    if "task_id" not in existing:
        print("Adding task_id column to activities...")
        conn.execute(text("ALTER TABLE activities ADD COLUMN task_id INTEGER REFERENCES tasks(id)"))
    else:
        print("task_id already exists in activities")

    existing = [row[0] for row in conn.execute(text("PRAGMA table_info(tasks)")).fetchall()]
    if "starts_at" not in existing:
        print("Adding starts_at column to tasks...")
        conn.execute(text("ALTER TABLE tasks ADD COLUMN starts_at DATETIME"))
    else:
        print("starts_at already exists in tasks")

    conn.commit()
    print("Migration completed successfully")
