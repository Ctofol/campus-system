#!/usr/bin/env python3
"""
Seed a stable demo dataset for the product promotion video.

Run from backend directory:
  python scripts/seed_demo_video.py --reset

The script only touches demo-scoped rows:
  - phone numbers starting with 1880000
  - student numbers starting with DEMO
  - titles/names starting with [PROMO]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import auth, models  # noqa: E402
from app.database import Base, SessionLocal, engine  # noqa: E402


DEMO_PREFIX = "[PROMO]"
TEACHER_PHONE = "18800000001"
TEACHER_PASSWORD = "DemoTeacher123"
STUDENT_PASSWORD = "DemoStudent123"
STUDENT_PHONE_START = 18800000101

MAJOR_NAME = f"{DEMO_PREFIX} Digital Sports"
CLASS_NAMES = [f"{DEMO_PREFIX} Class A", f"{DEMO_PREFIX} Class B"]

STUDENT_NAMES = [
    "Chen Yu",
    "Li Ming",
    "Wang Xin",
    "Zhao Rui",
    "Liu Yang",
    "Sun Yue",
    "Zhou Ran",
    "Wu Hao",
    "Xu Qing",
    "He Fan",
    "Gao Yuan",
    "Lin Xi",
    "Deng Lei",
    "Qin Mo",
    "Tang Yi",
    "Fang Ning",
    "Shen Ke",
    "Jiang Nan",
    "Ma Jun",
    "Guo Chen",
    "Xia An",
    "Song Qi",
    "Yuan Bo",
    "Han Lu",
]


def now_utc() -> datetime:
    return datetime.utcnow().replace(microsecond=0)


def get_or_create(db, model, defaults=None, **filters):
    row = db.query(model).filter_by(**filters).first()
    if row:
        return row, False
    data = dict(filters)
    data.update(defaults or {})
    row = model(**data)
    db.add(row)
    db.flush()
    return row, True


def build_track(lat0=23.1291, lng0=113.2644, points=36, loop=False):
    track = []
    for i in range(points):
        lat = lat0 + (i % 12) * 0.00036
        lng = lng0 + (i // 12) * 0.00042
        if loop and i >= points // 2:
            lat = lat0 + ((points - i) % 12) * 0.00036
            lng = lng0 + ((points - i) // 12) * 0.00042
        track.append(
            {
                "lat": round(lat, 6),
                "lng": round(lng, 6),
                "timestamp": (now_utc() - timedelta(minutes=points - i)).isoformat(),
            }
        )
    return json.dumps(track, ensure_ascii=False)


def create_notification(db, user_id, title, body, ntype, payload=None, unread=True):
    db.add(
        models.UserNotification(
            user_id=user_id,
            title=title,
            body=body,
            ntype=ntype,
            payload=json.dumps(payload or {"demo": True}, ensure_ascii=False),
            is_read=not unread,
            created_at=now_utc() - timedelta(minutes=15),
        )
    )


def reset_demo_data(db):
    demo_users = db.query(models.User).filter(models.User.phone.like("1880000%")).all()
    demo_user_ids = [u.id for u in demo_users]
    demo_student_nos = [u.student_id for u in demo_users if u.student_id]

    if demo_user_ids:
        demo_activity_ids = [
            row.id
            for row in db.query(models.Activity.id)
            .filter(models.Activity.user_id.in_(demo_user_ids))
            .all()
        ]
        if demo_activity_ids:
            db.query(models.ActivityReview).filter(
                models.ActivityReview.activity_id.in_(demo_activity_ids)
            ).delete(synchronize_session=False)
            db.query(models.ActivityEvidence).filter(
                models.ActivityEvidence.activity_id.in_(demo_activity_ids)
            ).delete(synchronize_session=False)
            db.query(models.ActivityMetrics).filter(
                models.ActivityMetrics.activity_id.in_(demo_activity_ids)
            ).delete(synchronize_session=False)
            db.query(models.Activity).filter(
                models.Activity.id.in_(demo_activity_ids)
            ).delete(synchronize_session=False)

        db.query(models.HealthRequest).filter(
            models.HealthRequest.student_id.in_(demo_user_ids)
        ).delete(synchronize_session=False)
        db.query(models.UserNotification).filter(
            models.UserNotification.user_id.in_(demo_user_ids)
        ).delete(synchronize_session=False)
        db.query(models.RunGroupActivityApplication).filter(
            models.RunGroupActivityApplication.user_id.in_(demo_user_ids)
        ).delete(synchronize_session=False)
        db.query(models.RunGroupMember).filter(
            models.RunGroupMember.user_id.in_(demo_user_ids)
        ).delete(synchronize_session=False)
        db.query(models.TeacherStudent).filter(
            (models.TeacherStudent.teacher_id.in_(demo_user_ids))
            | (models.TeacherStudent.student_user_id.in_(demo_user_ids))
        ).delete(synchronize_session=False)
        db.query(models.TeacherSubject).filter(
            models.TeacherSubject.teacher_id.in_(demo_user_ids)
        ).delete(synchronize_session=False)
        db.query(models.TeacherClass).filter(
            models.TeacherClass.teacher_id.in_(demo_user_ids)
        ).delete(synchronize_session=False)

    demo_tasks = db.query(models.Task).filter(models.Task.title.like(f"{DEMO_PREFIX}%")).all()
    demo_task_ids = [t.id for t in demo_tasks]
    if demo_task_ids:
        db.query(models.UserNotification).filter(
            models.UserNotification.ntype.in_(["task", "task_reminder"])
        ).filter(models.UserNotification.payload.like("%demo_video%")).delete(
            synchronize_session=False
        )
        db.query(models.Task).filter(models.Task.id.in_(demo_task_ids)).delete(
            synchronize_session=False
        )

    demo_group_ids = [
        row.id
        for row in db.query(models.RunGroup.id)
        .filter(models.RunGroup.name.like(f"{DEMO_PREFIX}%"))
        .all()
    ]
    if demo_group_ids:
        demo_rg_activity_ids = [
            row.id
            for row in db.query(models.RunGroupActivity.id)
            .filter(models.RunGroupActivity.group_id.in_(demo_group_ids))
            .all()
        ]
        if demo_rg_activity_ids:
            db.query(models.RunGroupActivityApplication).filter(
                models.RunGroupActivityApplication.activity_id.in_(demo_rg_activity_ids)
            ).delete(synchronize_session=False)
            db.query(models.RunGroupActivity).filter(
                models.RunGroupActivity.id.in_(demo_rg_activity_ids)
            ).delete(synchronize_session=False)
        db.query(models.RunGroupMember).filter(
            models.RunGroupMember.group_id.in_(demo_group_ids)
        ).delete(synchronize_session=False)
        db.query(models.RunGroup).filter(models.RunGroup.id.in_(demo_group_ids)).delete(
            synchronize_session=False
        )

    if demo_user_ids:
        db.query(models.User).filter(models.User.id.in_(demo_user_ids)).delete(
            synchronize_session=False
        )
    if demo_student_nos:
        db.query(models.StudentProfile).filter(
            models.StudentProfile.student_id.in_(demo_student_nos)
        ).delete(synchronize_session=False)

    demo_class_ids = [
        row.id
        for row in db.query(models.Class.id)
        .filter(models.Class.name.in_(CLASS_NAMES))
        .all()
    ]
    if demo_class_ids:
        db.query(models.SunshineRunRule).filter(
            models.SunshineRunRule.class_id.in_(demo_class_ids)
        ).delete(synchronize_session=False)
        db.query(models.Class).filter(models.Class.id.in_(demo_class_ids)).delete(
            synchronize_session=False
        )
    db.query(models.Major).filter(models.Major.name == MAJOR_NAME).delete(
        synchronize_session=False
    )
    db.commit()


def seed_demo_data(reset=False):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if reset:
            print("Resetting previous promo demo data...")
            reset_demo_data(db)

        print("Creating promo demo accounts and data...")
        major, _ = get_or_create(db, models.Major, name=MAJOR_NAME)

        teacher, _ = get_or_create(
            db,
            models.User,
            phone=TEACHER_PHONE,
            defaults={
                "name": "Demo Teacher",
                "role": "teacher",
                "password_hash": auth.get_password_hash(TEACHER_PASSWORD),
                "signature": "Smart PE management demo account",
            },
        )
        teacher.password_hash = auth.get_password_hash(TEACHER_PASSWORD)

        classes = []
        for name in CLASS_NAMES:
            cls, _ = get_or_create(
                db,
                models.Class,
                name=name,
                major_id=major.id,
                defaults={"teacher_id": teacher.id},
            )
            cls.teacher_id = teacher.id
            classes.append(cls)
        db.flush()

        for cls in classes:
            get_or_create(
                db,
                models.TeacherClass,
                teacher_id=teacher.id,
                class_name=cls.name,
            )
            get_or_create(
                db,
                models.SunshineRunRule,
                class_id=cls.id,
                defaults={
                    "teacher_id": teacher.id,
                    "weekly_required_count": 3,
                    "min_distance_km": 2.0,
                    "min_duration_sec": 900,
                    "min_pace": 3.0,
                    "max_pace": 10.0,
                    "enabled": True,
                },
            )

        for subject in ["Running", "Fitness", "Basketball"]:
            get_or_create(
                db,
                models.TeacherSubject,
                teacher_id=teacher.id,
                subject_name=subject,
            )

        students = []
        for idx, name in enumerate(STUDENT_NAMES):
            class_obj = classes[idx % len(classes)]
            student_no = f"DEMO{idx + 1:03d}"
            phone = str(STUDENT_PHONE_START + idx)
            gender = "female" if idx % 3 == 0 else "male"
            profile, _ = get_or_create(
                db,
                models.StudentProfile,
                student_id=student_no,
                defaults={
                    "full_name": name,
                    "gender": gender,
                    "class_name": class_obj.name,
                    "major": major.name,
                    "subject": "Running",
                    "is_activated": True,
                },
            )
            profile.full_name = name
            profile.class_name = class_obj.name
            profile.is_activated = True

            student, _ = get_or_create(
                db,
                models.User,
                phone=phone,
                defaults={
                    "name": name,
                    "role": "student",
                    "password_hash": auth.get_password_hash(STUDENT_PASSWORD),
                    "student_id": student_no,
                    "class_id": class_obj.id,
                    "major_id": major.id,
                    "major_name": major.name,
                    "subject": "Running",
                    "gender": gender,
                    "group_name": ["A Group", "B Group", "C Group"][idx % 3],
                    "weekly_run_goal_km": 8.0,
                    "regular_score": 80 + (idx % 12),
                },
            )
            student.password_hash = auth.get_password_hash(STUDENT_PASSWORD)
            student.student_id = student_no
            student.class_id = class_obj.id
            student.major_id = major.id
            student.major_name = major.name
            student.subject = "Running"
            student.gender = gender
            student.group_name = ["A Group", "B Group", "C Group"][idx % 3]
            student.weekly_run_goal_km = 8.0
            student.regular_score = 80 + (idx % 12)
            if idx in (5, 16):
                student.health_status = "leave"
                student.abnormal_reason = "Promo leave application"
            elif idx in (8, 19):
                student.health_status = "injured"
                student.abnormal_reason = "Promo ankle discomfort"
            else:
                student.health_status = "normal"
                student.abnormal_reason = None
            students.append(student)

        db.flush()

        for stu in students:
            get_or_create(
                db,
                models.TeacherStudent,
                teacher_id=teacher.id,
                student_user_id=stu.id,
            )

        task_specs = [
            ("3km Campus Run Task", classes[0], 3.0, 1500, 8),
            ("Weekly Endurance Run", classes[1], 2.5, 1200, 7),
            ("Fitness Check Task", classes[0], None, None, 10),
        ]
        tasks = []
        for title, cls, min_distance, min_duration, days in task_specs:
            task, _ = get_or_create(
                db,
                models.Task,
                title=f"{DEMO_PREFIX} {title}",
                defaults={
                    "type": "test" if "Fitness" in title else "run",
                    "description": "Promo video demo task data.",
                    "min_distance": min_distance,
                    "min_duration": min_duration,
                    "min_count": 40 if "Fitness" in title else None,
                    "starts_at": now_utc() - timedelta(days=1),
                    "deadline": now_utc() + timedelta(days=days),
                    "target_group": "class",
                    "class_id": cls.id,
                    "created_by": teacher.id,
                },
            )
            task.created_by = teacher.id
            task.class_id = cls.id
            task.deadline = now_utc() + timedelta(days=days)
            tasks.append(task)
        db.flush()

        for task in tasks:
            target_students = [s for s in students if s.class_id == task.class_id]
            for stu in target_students:
                create_notification(
                    db,
                    stu.id,
                    "New training task",
                    f"Teacher released {task.title}. Please complete it before deadline.",
                    "task",
                    {"demo_video": True, "task_id": task.id, "class_id": task.class_id},
                    unread=stu == target_students[0],
                )

        # Free sunshine runs for student home and teacher trend.
        activity_rows = []
        for idx, stu in enumerate(students):
            if stu.health_status != "normal":
                continue
            for day in range(0, 5):
                start = now_utc() - timedelta(days=day, hours=idx % 5)
                distance = round(2.2 + ((idx + day) % 8) * 0.28, 2)
                duration = int(distance * (330 + (idx % 4) * 18))
                is_valid = day != 0 or idx % 6 != 0
                fail_reason = None if is_valid else "Abnormal pace detected"
                activity_rows.append(
                    (
                        stu,
                        None,
                        "free",
                        "run",
                        start,
                        distance,
                        duration,
                        round(duration / 60 / distance, 2),
                        is_valid,
                        fail_reason,
                    )
                )

        # Task completions: Class A 9/12, Class B 7/12, includes one abnormal task run.
        for task in tasks:
            target_students = [s for s in students if s.class_id == task.class_id]
            limit = 9 if task.class_id == classes[0].id else 7
            if task.type == "test":
                limit = 8
            for idx, stu in enumerate(target_students[:limit]):
                start = now_utc() - timedelta(hours=2, minutes=idx * 4)
                distance = 3.2 if task.type == "run" else None
                duration = 1620 if task.type == "run" else 600
                activity_rows.append(
                    (
                        stu,
                        task,
                        "task",
                        task.type,
                        start,
                        distance,
                        duration,
                        8.4 if task.type == "run" else None,
                        idx != limit - 1,
                        None if idx != limit - 1 else "Route left allowed area",
                    )
                )

        for stu, task, source, act_type, start, distance, duration, pace, ok, reason in activity_rows:
            act = models.Activity(
                user_id=stu.id,
                type=act_type,
                source=source,
                status="approved" if ok else "pending_review",
                started_at=start,
                ended_at=start + timedelta(seconds=duration or 600),
                is_valid=ok,
                fail_reason=reason,
                face_verified=True,
                face_liveness_pass=ok,
                face_match_score=92.5 if ok else 61.2,
                face_fail_code=None if ok else "ROUTE_ABNORMAL",
                task_id=task.id if task else None,
            )
            db.add(act)
            db.flush()
            if act_type == "run":
                metrics = models.ActivityMetrics(
                    activity_id=act.id,
                    distance=distance,
                    duration=duration,
                    pace=str(pace),
                    trajectory=build_track(loop=not ok),
                    checkpoints=json.dumps(
                        [
                            {"name": "Start", "passed": True},
                            {"name": "Playground", "passed": ok},
                            {"name": "Finish", "passed": ok},
                        ],
                        ensure_ascii=False,
                    ),
                    step_count=int((distance or 2.0) * 1350),
                    qualified=ok,
                    teacher_score=88.0 if ok else None,
                    teacher_comment="Stable rhythm and complete trajectory" if ok else None,
                    scored_at=now_utc() if ok else None,
                    scored_by=teacher.id if ok else None,
                )
            else:
                metrics = models.ActivityMetrics(
                    activity_id=act.id,
                    duration=duration,
                    count=45,
                    qualified=ok,
                    score=91,
                    score_detail=json.dumps({"posture": 92, "rhythm": 89}),
                    teacher_score=91.0,
                    teacher_comment="Good completion quality",
                    scored_at=now_utc(),
                    scored_by=teacher.id,
                    exercise_type="sit_up",
                    analysis_status="success",
                )
            db.add(metrics)

        for stu in [students[5], students[8], students[16]]:
            req_type = "leave" if stu.health_status == "leave" else "injury"
            db.add(
                models.HealthRequest(
                    student_id=stu.id,
                    type=req_type,
                    reason=stu.abnormal_reason or "Promo special situation",
                    attachments=json.dumps(["/uploads/demo/medical-proof.jpg"]),
                    status="pending",
                    start_date=now_utc(),
                    end_date=now_utc() + timedelta(days=2),
                    created_at=now_utc() - timedelta(hours=3),
                )
            )
            create_notification(
                db,
                teacher.id,
                "Pending special situation review",
                f"{stu.name} submitted a {req_type} request.",
                "health_request",
                {"demo_video": True, "student_id": stu.id},
                unread=True,
            )

        for title, body, ntype in [
            ("System maintenance notice", "Tonight 23:00 demo server maintenance window.", "system"),
            ("Class completion alert", "Class A completion rate has reached 75%.", "analytics"),
            ("Route abnormality marked", "One abnormal trajectory has entered pending review.", "alert"),
        ]:
            create_notification(
                db,
                teacher.id,
                title,
                body,
                ntype,
                {"demo_video": True},
                unread=True,
            )

        group, _ = get_or_create(
            db,
            models.RunGroup,
            name=f"{DEMO_PREFIX} Morning Run Club",
            defaults={
                "description": "Promo run group activity demo.",
                "avatar": "/static/home-run-group.png",
                "creator_id": students[0].id,
                "total_mileage": 1288.6,
                "member_count": 18,
                "rank": 1,
            },
        )
        group.creator_id = students[0].id
        group.total_mileage = 1288.6
        group.member_count = 18
        for stu in students[:18]:
            get_or_create(
                db,
                models.RunGroupMember,
                group_id=group.id,
                user_id=stu.id,
                defaults={"role": "creator" if stu.id == students[0].id else "member"},
            )
        rg_activity, _ = get_or_create(
            db,
            models.RunGroupActivity,
            group_id=group.id,
            title=f"{DEMO_PREFIX} Campus Night Run",
            defaults={
                "description": "Promo video run group event.",
                "cover_image": "/static/home/hero-bg.png",
                "activity_time": now_utc() + timedelta(days=2, hours=3),
                "location": "Campus Playground",
                "distance": 5.0,
                "total_quota": 60,
                "apply_count": 16,
                "status": "upcoming",
                "created_by": students[0].id,
            },
        )
        rg_activity.apply_count = 16
        for stu in students[:16]:
            get_or_create(
                db,
                models.RunGroupActivityApplication,
                activity_id=rg_activity.id,
                user_id=stu.id,
                defaults={"status": "applied"},
            )

        db.commit()
        print("\nPromo demo data is ready.")
        print("\nRecording accounts:")
        print(f"  Teacher: {TEACHER_PHONE} / {TEACHER_PASSWORD}")
        print(f"  Student A: {STUDENT_PHONE_START} / {STUDENT_PASSWORD}")
        print(f"  Student B: {STUDENT_PHONE_START + 1} / {STUDENT_PASSWORD}")
        print("\nRecommended recording path:")
        print("  1. Teacher logs in -> management/dashboard/tasks/notifications.")
        print("  2. Student A logs in -> sees task, notifications, run history.")
        print("  3. Student B logs in -> alternate class/notification view.")
        print("\nSafe reset command:")
        print("  python scripts/seed_demo_video.py --reset")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Seed promo video demo data.")
    parser.add_argument("--reset", action="store_true", help="Remove old promo data first.")
    args = parser.parse_args()
    seed_demo_data(reset=args.reset)


if __name__ == "__main__":
    main()
