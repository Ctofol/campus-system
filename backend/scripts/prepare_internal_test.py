#!/usr/bin/env python3
"""
Prepare a clean internal-test dataset while keeping account and class data.

Default behavior keeps:
- users, student_profiles, classes, majors
- teacher bindings and subject options
- checkpoints, courses, course contents
- tasks
- medal definitions

Default behavior clears:
- run/test activity records and scores
- health requests
- notifications
- course enrollments and progress
- run-group activity applications
- earned medals
- student transient status fields

Run without --yes for a dry run.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable, Tuple

BACKEND_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_ROOT.parent
sys.path.insert(0, str(BACKEND_ROOT))

from app import database, models  # noqa: E402


DeleteSpec = Tuple[str, object]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean business records before internal student testing."
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Actually delete/update records. Without this flag only prints counts.",
    )
    parser.add_argument(
        "--delete-tasks",
        action="store_true",
        help="Also delete teacher-created tasks. Default keeps tasks.",
    )
    parser.add_argument(
        "--delete-courses",
        action="store_true",
        help="Also delete courses and course contents. Default keeps courses.",
    )
    parser.add_argument(
        "--delete-run-groups",
        action="store_true",
        help="Also delete run groups, members, and group activities. Default keeps them.",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip SQLite database backup before applying changes.",
    )
    return parser.parse_args()


def sqlite_database_path() -> Path | None:
    url = database.SQLALCHEMY_DATABASE_URL
    if not url.startswith("sqlite:///"):
        return None
    raw = url.replace("sqlite:///", "", 1)
    return Path(raw)


def backup_sqlite_database() -> Path | None:
    db_path = sqlite_database_path()
    if not db_path or not db_path.exists():
        return None
    backup_dir = PROJECT_ROOT / "backups"
    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{db_path.stem}_before_internal_test_{timestamp}{db_path.suffix}"
    shutil.copy2(db_path, backup_path)
    return backup_path


def delete_specs(args: argparse.Namespace) -> list[DeleteSpec]:
    specs: list[DeleteSpec] = [
        ("activity_review", models.ActivityReview),
        ("activity_evidence", models.ActivityEvidence),
        ("activity_metrics", models.ActivityMetrics),
        ("activities", models.Activity),
        ("health_requests", models.HealthRequest),
        ("user_notifications", models.UserNotification),
        ("course_progress", models.CourseProgress),
        ("enrollments", models.Enrollment),
        ("run_group_activity_applications", models.RunGroupActivityApplication),
        ("user_medals", models.UserMedal),
    ]

    if args.delete_run_groups:
        specs.extend(
            [
                ("run_group_activities", models.RunGroupActivity),
                ("run_group_members", models.RunGroupMember),
                ("run_groups", models.RunGroup),
            ]
        )

    if args.delete_tasks:
        specs.append(("tasks", models.Task))

    if args.delete_courses:
        specs.extend(
            [
                ("course_contents", models.CourseContent),
                ("courses", models.Course),
            ]
        )

    return specs


def count_rows(db, specs: Iterable[DeleteSpec]) -> list[tuple[str, int]]:
    rows: list[tuple[str, int]] = []
    for label, model in specs:
        rows.append((label, db.query(model).count()))
    return rows


def print_counts(title: str, rows: Iterable[tuple[str, int]]) -> None:
    print(title)
    for label, count in rows:
        print(f"  {label}: {count}")


def reset_student_state(db, apply_changes: bool) -> int:
    query = db.query(models.User).filter(models.User.role == "student")
    count = query.count()
    if apply_changes:
        query.update(
            {
                models.User.health_status: "normal",
                models.User.abnormal_reason: None,
                models.User.regular_score: 0.0,
            },
            synchronize_session=False,
        )
    return count


def reset_run_group_application_counts(db, apply_changes: bool) -> int:
    count = db.query(models.RunGroupActivity).count()
    if apply_changes:
        db.query(models.RunGroupActivity).update(
            {models.RunGroupActivity.apply_count: 0},
            synchronize_session=False,
        )
    return count


def apply_cleanup(db, specs: Iterable[DeleteSpec]) -> None:
    for _, model in specs:
        db.query(model).delete(synchronize_session=False)


def main() -> int:
    args = parse_args()
    db = database.SessionLocal()

    try:
        specs = delete_specs(args)
        before = count_rows(db, specs)
        print_counts("Records selected for cleanup:", before)
        student_count = reset_student_state(db, apply_changes=False)
        group_activity_count = reset_run_group_application_counts(db, apply_changes=False)
        print(f"Student status rows to reset: {student_count}")
        print(f"Run-group activity apply_count rows to reset: {group_activity_count}")

        if not args.yes:
            print("\nDry run only. Re-run with --yes to apply cleanup.")
            return 0

        backup_path = None if args.no_backup else backup_sqlite_database()
        if backup_path:
            print(f"SQLite backup created: {backup_path}")
        elif sqlite_database_path() and not args.no_backup:
            print("SQLite backup skipped: database file was not found.")
        elif not args.no_backup:
            print("SQLite backup skipped: current database is not SQLite.")

        apply_cleanup(db, specs)
        reset_student_state(db, apply_changes=True)
        if not args.delete_run_groups:
            reset_run_group_application_counts(db, apply_changes=True)

        db.commit()
        after = count_rows(db, specs)
        print_counts("\nRecords after cleanup:", after)
        print("\nInternal-test cleanup completed.")
        return 0
    except Exception as exc:
        db.rollback()
        print(f"Cleanup failed: {exc}", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
