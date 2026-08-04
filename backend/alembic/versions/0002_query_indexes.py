"""添加高频查询所需的非唯一索引。

Revision ID: 0002_query_indexes
Revises: 0001_schema_baseline
"""

from alembic import op
from sqlalchemy import inspect


revision = "0002_query_indexes"
down_revision = "0001_schema_baseline"
branch_labels = None
depends_on = None


INDEXES = (
    ("ix_activities_user_started", "activities", ["user_id", "started_at"]),
    ("ix_activities_task_status", "activities", ["task_id", "status"]),
    ("ix_activity_metrics_activity", "activity_metrics", ["activity_id"]),
    ("ix_tasks_class_deadline", "tasks", ["class_id", "deadline"]),
    ("ix_tasks_creator_created", "tasks", ["created_by", "created_at"]),
    ("ix_notifications_user_read_created", "user_notifications", ["user_id", "is_read", "created_at"]),
    ("ix_enrollments_student_course", "enrollments", ["student_id", "course_id"]),
    ("ix_course_progress_student_content", "course_progress", ["student_id", "content_id"]),
    ("ix_run_group_members_group_user", "run_group_members", ["group_id", "user_id"]),
    ("ix_run_group_applications_activity_user", "run_group_activity_applications", ["activity_id", "user_id"]),
    ("ix_teacher_classes_teacher_class", "teacher_classes", ["teacher_id", "class_name"]),
)


def _existing_index_names(table: str) -> set[str]:
    inspector = inspect(op.get_bind())
    if not inspector.has_table(table):
        return set()
    return {item["name"] for item in inspector.get_indexes(table)}


def upgrade() -> None:
    for name, table, columns in INDEXES:
        if name not in _existing_index_names(table):
            op.create_index(name, table, columns, unique=False)


def downgrade() -> None:
    for name, table, _columns in reversed(INDEXES):
        if name in _existing_index_names(table):
            op.drop_index(name, table_name=table)
