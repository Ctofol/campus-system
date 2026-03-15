# -*- coding: utf-8 -*-
"""
校园运行模拟 - 自动化灌数脚本
用于压力测试与视觉验收：生成班级、学生档案、学生账号、跑步记录、教师及管辖关系。
用法:
  cd backend && python scripts/seed_mock_data.py           # 追加模拟数据
  cd backend && python scripts/seed_mock_data.py --clear  # 先清空非管理员数据再模拟
"""
import os
import sys
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import SessionLocal, engine
from app import models
from app.auth import get_password_hash


def ensure_activity_metrics_columns():
    """为旧库补全 activity_metrics 缺失列（如 step_count），避免 INSERT 报错。"""
    if "sqlite" not in str(engine.url):
        return
    with engine.connect() as conn:
        try:
            r = conn.execute(text("PRAGMA table_info(activity_metrics)"))
            cols = [row[1] for row in r]
        except Exception:
            return
        for col in ["step_count"]:
            if col not in cols:
                try:
                    conn.execute(text(f"ALTER TABLE activity_metrics ADD COLUMN {col} INTEGER"))
                    conn.commit()
                except Exception:
                    pass


def ensure_health_requests_columns():
    """为旧库补全 health_requests 缺失列（start_date, end_date），避免查询报错。"""
    if "sqlite" not in str(engine.url):
        return
    with engine.connect() as conn:
        try:
            r = conn.execute(text("PRAGMA table_info(health_requests)"))
            cols = [row[1] for row in r]
        except Exception:
            return
        for col in ["start_date", "end_date"]:
            if col not in cols:
                try:
                    conn.execute(text(f"ALTER TABLE health_requests ADD COLUMN {col} TEXT"))
                    conn.commit()
                except Exception:
                    pass


# 随机姓氏与名字用字，便于生成中文姓名
SURNAMES = "李王张刘陈杨赵黄周吴徐孙胡朱高林何郭马罗梁宋郑谢韩唐冯于董萧程曹袁邓许傅沈曾彭吕苏卢蒋蔡贾丁魏薛叶阎余潘杜戴夏钟汪田任姜范方石姚谭廖邹熊金陆郝孔白崔康毛邱秦江史顾侯邵孟龙万段漕钱汤尹黎易常武乔贺赖龚文"
NAME_CHARS = "伟芳娜敏静丽强磊军洋勇艳杰涛明超秀英华慧巧美琳云飞鑫浩宇凯嘉俊哲晨轩博文"

# 5 个班级，3 个专业
CLASSES_CONFIG = [
    {"name": "信息安全1区", "major": "信息安全"},
    {"name": "信息安全2区", "major": "信息安全"},
    {"name": "网络安全1区", "major": "网络安全"},
    {"name": "数警1区", "major": "数警"},
    {"name": "数警2区", "major": "数警"},
]

# 教师及其管辖班级（班级名称）
TEACHER_CLASSES = [
    {"name": "教师A", "phone": "13800010001", "classes": ["信息安全1区", "网络安全1区"]},
    {"name": "教师B", "phone": "13800010002", "classes": ["数警2区"]},
]

# 无效跑步原因（异常数据）
INVALID_REASONS = [
    "人脸比对失败",
    "配速过快（疑似骑车）",
    "里程不足（男生需≥2km）",
]


def make_name():
    return random.choice(SURNAMES) + "".join(random.choices(NAME_CHARS, k=2))


def clear_non_admin(db):
    """清空非管理员数据（保留 role=admin 的用户）"""
    # 顺序依赖外键
    db.query(models.ActivityMetrics).delete()
    db.query(models.ActivityReview).delete()
    db.query(models.Activity).delete()
    db.query(models.TeacherClass).delete()
    db.query(models.HealthRequest).delete()
    db.query(models.Task).delete()
    # User: 删除学生和教师，保留 admin
    db.query(models.User).filter(models.User.role.in_(["student", "teacher"])).delete(synchronize_session=False)
    db.query(models.StudentProfile).delete()
    db.query(models.Class).delete()
    db.commit()


def ensure_classes(db):
    """创建 5 个班级，返回 name -> Class 映射"""
    name_to_class = {}
    for cfg in CLASSES_CONFIG:
        c = db.query(models.Class).filter(models.Class.name == cfg["name"]).first()
        if not c:
            c = models.Class(name=cfg["name"])
            db.add(c)
            db.flush()
        name_to_class[cfg["name"]] = c
    db.commit()
    return name_to_class


def seed_profiles(db, name_to_class):
    """为每个班级生成 10-15 名档案，男女比例均衡。返回 list of (StudentProfile, Class)"""
    profiles_with_class = []
    student_idx = 1
    for cfg in CLASSES_CONFIG:
        cls = name_to_class[cfg["name"]]
        n = random.randint(10, 15)
        for i in range(n):
            student_id = f"20{random.randint(24, 25)}{student_idx:04d}"
            student_idx += 1
            gender = "male" if random.random() < 0.5 else "female"
            profile = models.StudentProfile(
                student_id=student_id,
                full_name=make_name(),
                gender=gender,
                class_name=cfg["name"],
                major=cfg["major"],
                is_activated=False,
            )
            db.add(profile)
            db.flush()
            profiles_with_class.append((profile, cls))
    db.commit()
    return profiles_with_class


def activate_students(db, profiles_with_class):
    """70% 档案激活为 User，并关联 Class。返回已激活的 (User, StudentProfile) 列表"""
    random.shuffle(profiles_with_class)
    n_activate = max(1, int(len(profiles_with_class) * 0.7))
    activated = []
    phone_base = 13800100000
    used_phones = set()
    for i, (profile, cls) in enumerate(profiles_with_class):
        if i >= n_activate:
            break
        while True:
            phone = str(phone_base + random.randint(0, 99999))
            if phone not in used_phones and not db.query(models.User).filter(models.User.phone == phone).first():
                used_phones.add(phone)
                break
        user = models.User(
            phone=phone,
            name=profile.full_name,
            password_hash=get_password_hash("123456"),
            role="student",
            student_id=profile.student_id,
            gender=profile.gender,
            class_id=cls.id,
            major=profile.major,
        )
        db.add(user)
        db.flush()
        profile.is_activated = True
        activated.append((user, profile))
    db.commit()
    return activated


def seed_run_activities(db, activated):
    """
    为已激活学生每人生成 5-40 条跑步记录。
    达标组：部分人 >20 次，少数 40 次；未达标组：部分人 5-15 次。
    异常：在全体记录中随机标记 5-8 条为无效，并赋予指定原因。
    """
    base_time = datetime.utcnow() - timedelta(days=120)
    # 先规划每人条数，再汇总出所有 (user, profile, run_idx)，从中抽 5-8 条作无效
    plan = []
    for user, profile in activated:
        num_runs = random.choices(
            [random.randint(5, 15), random.randint(16, 25), random.randint(26, 40)],
            weights=[35, 45, 20],
            k=1,
        )[0]
        num_runs = max(5, min(40, num_runs))
        for idx in range(num_runs):
            plan.append((user, profile, idx))
    n_invalid = min(random.randint(5, 8), len(plan))
    invalid_slots = set(random.sample(range(len(plan)), n_invalid))
    reason_by_pos = {}
    for i, pos in enumerate(sorted(invalid_slots)):
        reason_by_pos[pos] = INVALID_REASONS[i % len(INVALID_REASONS)]

    total_activities = 0
    invalid_count = 0
    for pos, (user, profile, idx) in enumerate(plan):
        is_invalid = pos in invalid_slots
        if is_invalid:
            invalid_count += 1
            reason = reason_by_pos.get(pos, INVALID_REASONS[0])
            if "里程不足" in reason:
                distance = 1.5
                pace = "6.5"
                duration_sec = 600
            elif "配速" in reason:
                distance = 2.5
                pace = "2.8"
                duration_sec = 420
            else:
                distance = 2.0 if profile.gender == "male" else 1.2
                pace = "5.5"
                duration_sec = 720
            is_valid = False
            face_verified = "人脸" not in reason
        else:
            distance = round(random.uniform(2.0, 4.0), 2) if profile.gender == "male" else round(random.uniform(1.2, 3.0), 2)
            pace_val = round(random.uniform(4.0, 7.0), 1)
            pace = str(pace_val)
            duration_sec = int(distance * pace_val * 60)
            reason = None
            is_valid = True
            face_verified = True

        day_offset = random.randint(0, 100)
        start = base_time + timedelta(days=day_offset, minutes=random.randint(0, 600))
        end = start + timedelta(seconds=duration_sec)

        act = models.Activity(
            user_id=user.id,
            type="run",
            source=random.choice(["free", "task"]),
            status="finished",
            started_at=start,
            ended_at=end,
            is_valid=is_valid,
            fail_reason=reason,
            face_verified=face_verified,
        )
        db.add(act)
        db.flush()
        metrics = models.ActivityMetrics(
            activity_id=act.id,
            distance=distance,
            duration=duration_sec,
            pace=pace,
            qualified=is_valid,
        )
        db.add(metrics)
        total_activities += 1

    db.commit()
    return total_activities, invalid_count


def seed_teachers(db):
    """创建 2 名教师并绑定管辖班级。"""
    teachers = []
    for tc in TEACHER_CLASSES:
        u = db.query(models.User).filter(models.User.phone == tc["phone"]).first()
        if not u:
            u = models.User(
                phone=tc["phone"],
                name=tc["name"],
                password_hash=get_password_hash("123456"),
                role="teacher",
            )
            db.add(u)
            db.flush()
        db.query(models.TeacherClass).filter(models.TeacherClass.teacher_id == u.id).delete(synchronize_session=False)
        for class_name in tc["classes"]:
            db.add(models.TeacherClass(teacher_id=u.id, class_name=class_name))
        teachers.append(u)
    db.commit()
    return teachers


def seed_recent_runs_and_scores(db, activated, teachers):
    """
    为「近期」和「今日」补真实数据：最近 7 天内及今日的达标跑步，并给部分记录打教师分。
    使工作台「今日打卡」「达标率」「本周趋势」和「教师打分趋势」有数可看。
    """
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    week_ago = now - timedelta(days=7)
    teacher_by_id = {t.id: t for t in teachers}

    added = 0
    scored = 0
    # 每个学生最近 7 天 1～3 次、今日 0 或 1 次
    for user, profile in activated:
        n_week = random.randint(1, 3)
        for _ in range(n_week):
            day_back = random.randint(0, 6)
            start = (today_start - timedelta(days=day_back)) + timedelta(minutes=random.randint(60, 600))
            duration_sec = random.randint(1200, 2400)
            distance = round(duration_sec / 60 / random.uniform(5.5, 6.5), 2)
            if profile.gender == "female" and distance > 2.5:
                distance = round(min(distance, 2.2), 2)
            pace_val = round(duration_sec / 60 / distance, 1)
            pace = str(pace_val)
            end = start + timedelta(seconds=duration_sec)

            act = models.Activity(
                user_id=user.id,
                type="run",
                source="free",
                status="finished",
                started_at=start,
                ended_at=end,
                is_valid=True,
                fail_reason=None,
                face_verified=True,
            )
            db.add(act)
            db.flush()
            metrics = models.ActivityMetrics(
                activity_id=act.id,
                distance=distance,
                duration=duration_sec,
                pace=pace,
                qualified=True,
            )
            db.add(metrics)
            added += 1
            # 部分记录打教师分（随机选一个管辖该班的教师）
            if teacher_by_id and random.random() < 0.35:
                cls = db.query(models.Class).filter(models.Class.id == user.class_id).first()
                if cls:
                    tc = db.query(models.TeacherClass).filter(
                        models.TeacherClass.class_name == cls.name
                    ).first()
                    if tc and tc.teacher_id in teacher_by_id:
                        score_val = round(random.uniform(75, 98), 1)
                        metrics.teacher_score = score_val
                        metrics.scored_by = tc.teacher_id
                        metrics.scored_at = now - timedelta(days=random.randint(0, 5))
                        scored += 1

        # 约一半学生有「今日」1 次
        if random.random() < 0.5:
            start = today_start + timedelta(minutes=random.randint(120, 480))
            duration_sec = random.randint(1200, 2000)
            distance = round(duration_sec / 60 / random.uniform(5.5, 6.5), 2)
            if profile.gender == "female" and distance > 2.2:
                distance = round(min(distance, 2.0), 2)
            pace_val = round(duration_sec / 60 / distance, 1)
            end = start + timedelta(seconds=duration_sec)
            act = models.Activity(
                user_id=user.id,
                type="run",
                source="free",
                status="finished",
                started_at=start,
                ended_at=end,
                is_valid=True,
                fail_reason=None,
                face_verified=True,
            )
            db.add(act)
            db.flush()
            db.add(models.ActivityMetrics(
                activity_id=act.id,
                distance=distance,
                duration=duration_sec,
                pace=str(pace_val),
                qualified=True,
            ))
            added += 1

    # 给部分学生更新平时分（与教师打分一致的计算来源之一）
    for user in [u for u, _ in activated]:
        metrics_with_score = db.query(models.ActivityMetrics).join(
            models.Activity
        ).filter(
            models.Activity.user_id == user.id,
            models.ActivityMetrics.teacher_score.isnot(None),
        ).all()
        if metrics_with_score:
            avg = sum(m.teacher_score for m in metrics_with_score) / len(metrics_with_score)
            user.regular_score = round(avg, 1)

    db.commit()
    return added, scored


def seed_tasks_and_completions(db, activated, teachers, name_to_class):
    """
    教师发布跑步/体测任务（截止日期在本周或未来），并为部分学生生成本周内完成记录，使「进行中任务」「任务完成率」有数。
    """
    now = datetime.utcnow()
    week_start = now - timedelta(days=now.weekday())
    week_start = datetime(week_start.year, week_start.month, week_start.day)
    tasks_created = 0
    completions_added = 0

    for teacher in teachers:
        tc_rows = db.query(models.TeacherClass).filter(
            models.TeacherClass.teacher_id == teacher.id
        ).all()
        class_names = [r.class_name for r in tc_rows]
        if not class_names:
            continue
        class_ids = [name_to_class[n].id for n in class_names if n in name_to_class]
        if not class_ids:
            continue

        # 每师 2～3 个任务：跑步 + 可选体测
        for _ in range(random.randint(2, 3)):
            is_run = random.choice([True, True, False])  # 多数为跑步
            deadline = now + timedelta(days=random.randint(3, 14))
            class_id = random.choice(class_ids)
            if is_run:
                t = models.Task(
                    title="阳光跑达标任务" if random.random() < 0.6 else "周末跑步打卡",
                    type="run",
                    min_distance=2.0,
                    min_duration=25,
                    min_count=None,
                    deadline=deadline,
                    description="完成至少 2km，约 25 分钟。",
                    target_group="all",
                    class_id=class_id,
                    created_by=teacher.id,
                )
            else:
                t = models.Task(
                    title="体测任务-仰卧起坐/引体",
                    type="test",
                    min_distance=None,
                    min_duration=None,
                    min_count=random.randint(20, 40),
                    deadline=deadline,
                    description="完成规定次数。",
                    target_group="all",
                    class_id=class_id,
                    created_by=teacher.id,
                )
            db.add(t)
            db.flush()
            tasks_created += 1

            # 为该任务班级内部分学生生成「本周内」完成记录
            students_in_class = [u for u, _ in activated if u.class_id == class_id]
            n_complete = min(random.randint(2, 6), len(students_in_class))
            if n_complete == 0:
                continue
            chosen = random.sample(students_in_class, n_complete)
            for user in chosen:
                # 本周内某时刻
                day_offset = random.randint(0, now.weekday() if now.weekday() > 0 else 1)
                start = week_start + timedelta(days=day_offset, minutes=random.randint(60, 600))
                if is_run:
                    duration_sec = random.randint(1500, 2400)
                    distance = round(duration_sec / 60 / 6.0, 2)
                    pace_val = round(duration_sec / 60 / distance, 1)
                    end = start + timedelta(seconds=duration_sec)
                    act = models.Activity(
                        user_id=user.id,
                        type="run",
                        source="task",
                        status="finished",
                        started_at=start,
                        ended_at=end,
                        is_valid=True,
                        face_verified=True,
                    )
                    db.add(act)
                    db.flush()
                    db.add(models.ActivityMetrics(
                        activity_id=act.id,
                        distance=distance,
                        duration=duration_sec,
                        pace=str(pace_val),
                        qualified=True,
                    ))
                else:
                    count = t.min_count or 25
                    end = start + timedelta(minutes=15)
                    act = models.Activity(
                        user_id=user.id,
                        type="test",
                        source="task",
                        status="finished",
                        started_at=start,
                        ended_at=end,
                        is_valid=True,
                        face_verified=True,
                    )
                    db.add(act)
                    db.flush()
                    db.add(models.ActivityMetrics(
                        activity_id=act.id,
                        duration=900,
                        count=count,
                        qualified=True,
                    ))
                completions_added += 1

    db.commit()
    return tasks_created, completions_added


def seed_pending_review_activities(db, activated, name_to_class, teachers):
    """
    生成少量待教师审批/打分的活动（status=pending_review），用于演示“运动待审批”列表。
    """
    if not activated:
        return 0
    now = datetime.utcnow()
    # 从教师A管辖班级里挑 1~3 个学生，生成待审批跑步/体测
    teacher_ids = [t.id for t in teachers] if teachers else []
    candidates = [u for u, _ in activated]
    n = min(random.randint(1, 3), len(candidates))
    chosen = random.sample(candidates, n)
    added = 0
    for user in chosen:
        is_run = random.random() < 0.7
        start = now - timedelta(hours=random.randint(1, 20))
        if is_run:
            duration_sec = random.randint(1400, 2200)
            distance = round(duration_sec / 60 / random.uniform(5.5, 6.8), 2)
            pace_val = round(duration_sec / 60 / distance, 1)
            end = start + timedelta(seconds=duration_sec)
            act = models.Activity(
                user_id=user.id,
                type="run",
                source="task",
                status="pending_review",
                started_at=start,
                ended_at=end,
                is_valid=True,
                face_verified=True,
            )
            db.add(act)
            db.flush()
            db.add(models.ActivityMetrics(
                activity_id=act.id,
                distance=distance,
                duration=duration_sec,
                pace=str(pace_val),
                qualified=True,
            ))
        else:
            end = start + timedelta(minutes=15)
            act = models.Activity(
                user_id=user.id,
                type="test",
                source="task",
                status="pending_review",
                started_at=start,
                ended_at=end,
                is_valid=True,
                face_verified=True,
            )
            db.add(act)
            db.flush()
            db.add(models.ActivityMetrics(
                activity_id=act.id,
                duration=900,
                count=random.randint(20, 40),
                qualified=True,
            ))
        added += 1
    db.commit()
    return added


def seed_health_requests_pending(db, activated):
    """若干条待处理请假/报伤，使「请假待处理」有数。"""
    if not activated:
        return 0
    n = min(random.randint(2, 5), len(activated))
    chosen = random.sample(activated, n)
    now = datetime.utcnow()
    added = 0
    for user, profile in chosen:
        leave = models.HealthRequest(
            student_id=user.id,
            type=random.choice(["leave", "injury"]),
            reason="身体不适请假" if random.random() < 0.6 else "运动扭伤需休息",
            status="pending",
            start_date=now + timedelta(days=1),
            end_date=now + timedelta(days=3),
        )
        db.add(leave)
        added += 1
    db.commit()
    return added


def main():
    import argparse
    parser = argparse.ArgumentParser(description="校园运行模拟数据脚本")
    parser.add_argument("--clear", action="store_true", help="执行前清空现有非管理员数据")
    args = parser.parse_args()

    ensure_activity_metrics_columns()
    ensure_health_requests_columns()
    db = SessionLocal()
    try:
        if args.clear:
            print("正在清空非管理员数据...")
            clear_non_admin(db)
            print("清空完成。")

        print("创建班级...")
        name_to_class = ensure_classes(db)
        print("生成学生档案...")
        profiles_with_class = seed_profiles(db, name_to_class)
        n_students = len(profiles_with_class)
        print("激活 70% 学生账号...")
        activated = activate_students(db, profiles_with_class)
        n_activated = len(activated)

        print("生成跑步记录（含部分异常）...")
        total_runs, invalid_count = seed_run_activities(db, activated)
        print("创建教师及管辖班级...")
        teachers = seed_teachers(db)
        print("生成近期/今日阳光跑及教师打分...")
        recent_added, scored_count = seed_recent_runs_and_scores(db, activated, teachers)
        print("发布任务及任务完成记录...")
        tasks_created, completions_added = seed_tasks_and_completions(
            db, activated, teachers, name_to_class
        )
        print("生成待审批运动记录（用于教师端审批列表）...")
        pending_acts = seed_pending_review_activities(db, activated, name_to_class, teachers)
        print("生成待处理请假...")
        pending_leave = seed_health_requests_pending(db, activated)

        print("\n" + "=" * 50)
        print("已成功模拟 {} 名学生，{} 条跑步记录，{} 个异常案例。".format(
            n_activated, total_runs, invalid_count
        ))
        print("近期/今日跑步: +{} 条，教师打分: {} 条，任务: {} 个，任务完成: {} 条，待处理请假: {} 条。".format(
            recent_added, scored_count, tasks_created, completions_added, pending_leave
        ))
        print("待审批运动记录: {} 条。".format(pending_acts))
        print("班级数: {}，档案总数: {}（其中未激活 {} 人）".format(
            len(CLASSES_CONFIG), n_students, n_students - n_activated
        ))
        print("教师默认密码: 123456；学生账号密码: 123456")
        print("=" * 50)
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
