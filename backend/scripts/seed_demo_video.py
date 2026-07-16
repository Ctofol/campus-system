#!/usr/bin/env python3
"""
为产品宣传视频生成一套稳定的中文演示数据。

Run from backend directory:
  python scripts/seed_demo_video.py --reset

The script only touches demo-scoped rows:
  - phone numbers starting with 1880000
  - student numbers starting with DEMO
  - titles/names starting with [演示] or legacy [PROMO]
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


DEMO_PREFIX = "[演示]"
LEGACY_PREFIXES = ["[PROMO]"]
TEACHER_PHONE = "18800000001"
TEACHER_PASSWORD = "DemoTeacher123"
STUDENT_PASSWORD = "DemoStudent123"
STUDENT_PHONE_START = 18800000101

MAJOR_NAME = f"{DEMO_PREFIX} 智慧体育"
CLASS_NAMES = [f"{DEMO_PREFIX} 体育一班", f"{DEMO_PREFIX} 体育二班"]
LEGACY_MAJOR_NAMES = ["[PROMO] Digital Sports"]
LEGACY_CLASS_NAMES = ["[PROMO] Class A", "[PROMO] Class B"]

STUDENT_NAMES = [
    "陈雨",
    "李明",
    "王欣",
    "赵睿",
    "刘洋",
    "孙悦",
    "周然",
    "吴昊",
    "徐晴",
    "何帆",
    "高远",
    "林溪",
    "邓磊",
    "秦墨",
    "唐一",
    "方宁",
    "沈柯",
    "江南",
    "马俊",
    "郭晨",
    "夏安",
    "宋祺",
    "袁博",
    "韩露",
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

    demo_task_query = db.query(models.Task).filter(models.Task.title.like(f"{DEMO_PREFIX}%"))
    for prefix in LEGACY_PREFIXES:
        demo_task_query = demo_task_query.union(
            db.query(models.Task).filter(models.Task.title.like(f"{prefix}%"))
        )
    demo_tasks = demo_task_query.all()
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
    for prefix in LEGACY_PREFIXES:
        demo_group_ids.extend(
            row.id
            for row in db.query(models.RunGroup.id)
            .filter(models.RunGroup.name.like(f"{prefix}%"))
            .all()
        )
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
        .filter(models.Class.name.in_(CLASS_NAMES + LEGACY_CLASS_NAMES))
        .all()
    ]
    if demo_class_ids:
        db.query(models.SunshineRunRule).filter(
            models.SunshineRunRule.class_id.in_(demo_class_ids)
        ).delete(synchronize_session=False)
        db.query(models.Class).filter(models.Class.id.in_(demo_class_ids)).delete(
            synchronize_session=False
        )
    db.query(models.Major).filter(
        models.Major.name.in_([MAJOR_NAME] + LEGACY_MAJOR_NAMES)
    ).delete(synchronize_session=False)
    db.commit()


def seed_demo_data(reset=False):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if reset:
            print("正在清理旧的宣传视频演示数据...")
            reset_demo_data(db)

        print("正在创建中文演示账号和业务数据...")
        major, _ = get_or_create(db, models.Major, name=MAJOR_NAME)

        teacher, _ = get_or_create(
            db,
            models.User,
            phone=TEACHER_PHONE,
            defaults={
                "name": "陈老师",
                "role": "teacher",
                "password_hash": auth.get_password_hash(TEACHER_PASSWORD),
                "signature": "让每一次训练都有数据支撑",
            },
        )
        teacher.name = "陈老师"
        teacher.signature = "让每一次训练都有数据支撑"
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

        for subject in ["跑步", "体能训练", "篮球"]:
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
                    "subject": "跑步",
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
                    "subject": "跑步",
                    "gender": gender,
                    "group_name": ["晨跑一组", "耐力二组", "活力三组"][idx % 3],
                    "weekly_run_goal_km": 8.0,
                    "regular_score": 80 + (idx % 12),
                },
            )
            student.password_hash = auth.get_password_hash(STUDENT_PASSWORD)
            student.student_id = student_no
            student.class_id = class_obj.id
            student.major_id = major.id
            student.major_name = major.name
            student.subject = "跑步"
            student.gender = gender
            student.group_name = ["晨跑一组", "耐力二组", "活力三组"][idx % 3]
            student.weekly_run_goal_km = 8.0
            student.regular_score = 80 + (idx % 12)
            if idx in (5, 16):
                student.health_status = "leave"
                student.abnormal_reason = "因校队训练冲突申请请假"
            elif idx in (8, 19):
                student.health_status = "injured"
                student.abnormal_reason = "脚踝不适，申请暂缓跑步"
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
            ("校园 3 公里节奏跑", "run", classes[0], 3.0, 1500, None, 8),
            ("本周耐力提升跑", "run", classes[1], 2.5, 1200, None, 7),
            ("核心力量体能测试", "test", classes[0], None, None, 40, 10),
        ]
        tasks = []
        for title, task_type, cls, min_distance, min_duration, min_count, days in task_specs:
            task, _ = get_or_create(
                db,
                models.Task,
                title=f"{DEMO_PREFIX} {title}",
                defaults={
                    "type": task_type,
                    "description": "宣传视频演示任务数据，用于展示教师发布与学生完成流程。",
                    "min_distance": min_distance,
                    "min_duration": min_duration,
                    "min_count": min_count,
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
                    "新训练任务",
                    f"陈老师发布了任务「{task.title}」，请在截止时间前完成。",
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
                fail_reason = None if is_valid else "配速异常，需教师复核"
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
                        None if idx != limit - 1 else "运动轨迹偏离指定区域",
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
                            {"name": "操场打卡点", "passed": ok},
                            {"name": "终点", "passed": ok},
                        ],
                        ensure_ascii=False,
                    ),
                    step_count=int((distance or 2.0) * 1350),
                    qualified=ok,
                    teacher_score=88.0 if ok else None,
                    teacher_comment="节奏稳定，轨迹完整" if ok else None,
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
                    score_detail=json.dumps({"动作规范": 92, "完成节奏": 89}, ensure_ascii=False),
                    teacher_score=91.0,
                    teacher_comment="动作完成质量较好",
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
                    reason=stu.abnormal_reason or "演示用特殊情况申请",
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
                "待处理特殊情况申请",
                f"{stu.name} 提交了{'请假' if req_type == 'leave' else '伤病'}申请，请及时审核。",
                "health_request",
                {"demo_video": True, "student_id": stu.id},
                unread=True,
            )

        for title, body, ntype in [
            ("系统维护通知", "今晚 23:00 将进行演示服务器例行维护。", "system"),
            ("班级完成率提醒", "体育一班任务完成率已达到 75%，请关注未完成学生。", "analytics"),
            ("异常轨迹提醒", "有一条运动轨迹进入待审核列表，请及时复核。", "alert"),
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
            name=f"{DEMO_PREFIX} 晨跑训练营",
            defaults={
                "description": "宣传视频跑团活动演示数据。",
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
            title=f"{DEMO_PREFIX} 校园夜跑活动",
            defaults={
                "description": "面向全校学生的夜跑打卡活动，展示跑团报名与活动通知流程。",
                "cover_image": "/static/home/hero-bg.png",
                "activity_time": now_utc() + timedelta(days=2, hours=3),
                "location": "学校田径场",
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
        print("\n中文宣传视频演示数据已准备完成。")
        print("\n录制账号：")
        print(f"  教师：{TEACHER_PHONE} / {TEACHER_PASSWORD}")
        print(f"  学生 A：{STUDENT_PHONE_START} / {STUDENT_PASSWORD}")
        print(f"  学生 B：{STUDENT_PHONE_START + 1} / {STUDENT_PASSWORD}")
        print("\n推荐录制路径：")
        print("  1. 教师登录 -> 工作台 / 综合管理 / 任务 / 通知。")
        print("  2. 学生 A 登录 -> 查看任务、通知和运动记录。")
        print("  3. 学生 B 登录 -> 展示另一个班级或通知视角。")
        print("\n安全重置命令：")
        print("  python scripts/seed_demo_video.py --reset")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="生成中文宣传视频演示数据。")
    parser.add_argument("--reset", action="store_true", help="先清理旧的演示数据。")
    args = parser.parse_args()
    seed_demo_data(reset=args.reset)


if __name__ == "__main__":
    main()
