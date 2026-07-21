import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib import request as urlrequest

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from .. import models
from .score_service import sunshine_run_filter


DISCLAIMER = "AI建议仅用于体育教学与训练参考，不作为医疗诊断；如身体不适请及时联系老师或校医。"
_LOCAL_ENV_LOADED = False


def _load_local_env() -> None:
    """Load ignored local .env files without adding a runtime dependency."""
    global _LOCAL_ENV_LOADED
    if _LOCAL_ENV_LOADED:
        return
    _LOCAL_ENV_LOADED = True

    backend_dir = Path(__file__).resolve().parents[2]
    project_dir = backend_dir.parent
    for env_path in (backend_dir / ".env", project_dir / ".env"):
        if not env_path.exists():
            continue
        try:
            for raw_line in env_path.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
        except OSError:
            continue


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _duration_text(seconds: Any) -> str:
    total = max(0, _safe_int(seconds))
    minutes = total // 60
    if minutes < 60:
        return f"{minutes}分钟"
    return f"{minutes // 60}小时{minutes % 60}分钟"


def _normalize_distance_km(distance: Any) -> float:
    value = _safe_float(distance)
    return value / 1000.0 if value > 100 else value


def _pace_min_per_km(distance_km: float, duration_sec: int, raw_pace: Any = None) -> Optional[float]:
    if raw_pace not in (None, ""):
        try:
            return float(str(raw_pace).replace("'", ".").replace('"', ""))
        except ValueError:
            pass
    if distance_km > 0 and duration_sec > 0:
        return duration_sec / 60.0 / distance_km
    return None


def _llm_chat(messages: List[Dict[str, str]]) -> Optional[str]:
    _load_local_env()
    api_key = os.getenv("LLM_API_KEY", "").strip()
    api_base = os.getenv("LLM_API_BASE", "").strip().rstrip("/")
    model = os.getenv("LLM_MODEL", "deepseek-v4-flash").strip()
    if not api_key or not api_base:
        return None

    url = api_base
    if not url.endswith("/chat/completions"):
        url = f"{url}/chat/completions"

    body = json.dumps(
        {"model": model, "messages": messages, "temperature": 0.35},
        ensure_ascii=False,
    ).encode("utf-8")
    req = urlrequest.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlrequest.urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        return payload["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def get_ai_status() -> Dict[str, Any]:
    _load_local_env()
    return {
        "enabled": True,
        "mode": "llm" if os.getenv("LLM_API_KEY") and os.getenv("LLM_API_BASE") else "local_demo",
        "model": os.getenv("LLM_MODEL", "local-rule-engine"),
        "features": ["campus_qa", "run_report", "test_feedback", "teacher_briefing"],
    }


def campus_qa(db: Session, user: models.User, question: str) -> Dict[str, Any]:
    q = (question or "").strip()
    courses = (
        db.query(models.Course)
        .filter(models.Course.is_public.is_(True))
        .order_by(models.Course.created_at.desc())
        .limit(5)
        .all()
    )
    course_titles = "、".join([c.title for c in courses]) or "暂无公开课程"

    llm_answer = _llm_chat(
        [
            {
                "role": "system",
                "content": (
                    "你是校园运动健康系统的AI体育助手。只回答阳光跑、体测、课程学习、"
                    "健康报备、跑团活动、教师体育管理相关问题。不要编造学校通知。"
                    "不要做医疗诊断。回答使用简洁中文，给出可执行建议。"
                ),
            },
            {
                "role": "user",
                "content": f"用户角色：{user.role}\n公开课程：{course_titles}\n问题：{q}",
            },
        ]
    )
    if llm_answer:
        return {
            "mode": "llm",
            "answer": llm_answer,
            "suggestions": [],
            "references": ["系统业务规则", "公开课程数据"],
            "disclaimer": DISCLAIMER,
        }

    if any(word in q for word in ["阳光跑", "跑步", "打卡", "配速", "轨迹"]):
        answer = "阳光跑会重点核验距离、时长、配速、轨迹和身份信息。建议在室外开阔区域开启定位，跑完后确认记录已上传。"
        suggestions = ["运动前检查定位权限", "保持连续记录", "结束后查看是否达标"]
    elif any(word in q for word in ["体测", "仰卧", "俯卧", "跳绳", "视频"]):
        answer = "体测需要选择项目并上传清晰视频。AI识别结果用于辅助判断，最终成绩仍以教师审核为准。"
        suggestions = ["保持全身入镜", "固定拍摄角度", "动作优先标准再追求次数"]
    elif any(word in q for word in ["课程", "学习", "视频"]):
        answer = f"课程模块支持体育课程学习和进度记录。当前可参考课程：{course_titles}。"
        suggestions = ["先完成教师指定课程", "学习后结合运动任务练习"]
    elif any(word in q for word in ["请假", "伤病", "报备"]):
        answer = "请假或伤病可以通过健康报备提交原因和附件，等待教师审批。身体不适时不要强行运动。"
        suggestions = ["上传清晰证明材料", "说明起止时间", "及时关注审批状态"]
    else:
        answer = "我可以回答阳光跑、体测、课程学习、健康报备、跑团活动和教师管理相关问题。"
        suggestions = ["可以问：阳光跑怎样算有效？", "可以问：体测视频怎么拍？"]

    return {
        "mode": "local_demo",
        "answer": answer,
        "suggestions": suggestions,
        "references": ["系统业务规则"],
        "disclaimer": DISCLAIMER,
    }


def build_run_report(
    db: Session,
    user: models.User,
    activity_id: Optional[int] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    payload = payload or {}
    activity = None
    if activity_id:
        activity = (
            db.query(models.Activity)
            .filter(models.Activity.id == activity_id, models.Activity.user_id == user.id)
            .first()
        )

    metrics = activity.metrics if activity and activity.metrics else None
    distance_km = _normalize_distance_km(
        getattr(metrics, "distance", None) if metrics else payload.get("distance_km")
    )
    duration_sec = _safe_int(getattr(metrics, "duration", None) if metrics else payload.get("duration_sec"))
    pace = _pace_min_per_km(distance_km, duration_sec, getattr(metrics, "pace", None) if metrics else payload.get("pace"))
    qualified = bool(activity.is_valid if activity else payload.get("qualified", False))

    recent = (
        db.query(models.Activity)
        .join(models.ActivityMetrics, models.ActivityMetrics.activity_id == models.Activity.id)
        .filter(models.Activity.user_id == user.id, models.Activity.type == "run")
        .order_by(models.Activity.started_at.desc())
        .limit(5)
        .all()
    )
    recent_km = sum(_normalize_distance_km(a.metrics.distance) for a in recent if a.metrics)

    intensity = "轻松恢复"
    if pace and pace <= 5.5:
        intensity = "高强度"
    elif pace and pace <= 7.0:
        intensity = "稳定有氧"
    elif distance_km >= 3:
        intensity = "耐力积累"

    suggestions = []
    if distance_km < 2:
        suggestions.append("下一次优先把连续运动距离提升到 2 公里以上。")
    if pace and pace < 4:
        suggestions.append("本次配速偏快，建议补充热身和拉伸，避免受伤。")
    if pace and pace > 9:
        suggestions.append("可以采用慢跑和快走交替，先把运动连续性建立起来。")
    if not suggestions:
        suggestions.append("保持当前节奏，每周 2-3 次稳定训练即可形成积累。")
    if recent_km:
        suggestions.append(f"最近 {len(recent)} 次累计约 {recent_km:.1f} 公里，注意安排恢复日。")

    return {
        "mode": "local_demo",
        "title": "AI运动报告",
        "summary": f"本次完成 {distance_km:.2f} 公里，用时 {_duration_text(duration_sec)}，属于{intensity}训练。{'已满足目标。' if qualified else '暂未完全达标。'}",
        "metrics": {
            "distance_km": round(distance_km, 2),
            "duration_sec": duration_sec,
            "pace_min_per_km": round(pace, 2) if pace else None,
            "qualified": qualified,
        },
        "suggestions": suggestions[:3],
        "disclaimer": DISCLAIMER,
    }


def build_test_feedback(db: Session, user: models.User, payload: Dict[str, Any]) -> Dict[str, Any]:
    project = payload.get("project") or payload.get("exercise_type") or "体测项目"
    count = _safe_int(payload.get("count"))
    score = payload.get("score")
    qualified = bool(payload.get("qualified", count > 0))

    suggestions = ["保持全身入镜，方便AI和老师复核。", "训练时优先保证动作标准，再逐步增加次数。"]
    if count <= 0:
        suggestions.insert(0, "本次没有识别到有效次数，建议检查拍摄角度后重新提交。")
    elif qualified:
        suggestions.insert(0, "本次完成度不错，可以继续加强核心稳定性训练。")
    else:
        suggestions.insert(0, "建议采用少量多组方式训练，先把动作质量稳定下来。")

    return {
        "mode": "local_demo",
        "title": "AI体测反馈",
        "summary": f"{project} 本次记录 {count} 次，{'达到基础要求' if qualified else '暂未达到基础要求'}。",
        "score": score,
        "suggestions": suggestions[:3],
        "disclaimer": "AI体测反馈用于辅助教学，最终成绩以教师审核为准。",
    }


def _managed_student_ids(db: Session, teacher: models.User) -> List[int]:
    subjects = [
        r.subject_name
        for r in db.query(models.TeacherSubject).filter(models.TeacherSubject.teacher_id == teacher.id).all()
    ]
    direct_class_ids = [
        r.id for r in db.query(models.Class).filter(models.Class.teacher_id == teacher.id).all()
    ]
    class_names = [
        r.class_name
        for r in db.query(models.TeacherClass).filter(models.TeacherClass.teacher_id == teacher.id).all()
    ]
    bound_class_ids = []
    if class_names:
        bound_class_ids = [
            r.id for r in db.query(models.Class).filter(models.Class.name.in_(class_names)).all()
        ]
    explicit_ids = [
        r[0]
        for r in db.query(models.TeacherStudent.student_user_id)
        .filter(models.TeacherStudent.teacher_id == teacher.id)
        .all()
    ]

    conditions = []
    if subjects:
        conditions.append(models.User.subject.in_(subjects))
    all_class_ids = list(set(direct_class_ids + bound_class_ids))
    if all_class_ids:
        conditions.append(models.User.class_id.in_(all_class_ids))
    if explicit_ids:
        conditions.append(models.User.id.in_(explicit_ids))
    if not conditions:
        return []
    rows = db.query(models.User.id).filter(models.User.role == "student").filter(or_(*conditions)).all()
    return [r[0] for r in rows]


def build_teacher_briefing(db: Session, teacher: models.User) -> Dict[str, Any]:
    student_ids = _managed_student_ids(db, teacher)
    if not student_ids:
        return {
            "mode": "local_demo",
            "title": "AI班级简报",
            "summary": "当前教师账号还没有绑定可管理学生，暂无法生成班级运动简报。",
            "alerts": [],
            "actions": ["先在管理端绑定班级、选科或学员。"],
            "disclaimer": DISCLAIMER,
        }

    today = datetime.utcnow().date()
    today_start = datetime(today.year, today.month, today.day)
    week_start = today_start - timedelta(days=today_start.weekday())

    today_runs = (
        db.query(models.Activity)
        .filter(models.Activity.user_id.in_(student_ids), models.Activity.started_at >= today_start)
        .filter(sunshine_run_filter())
        .count()
    )
    valid_week_runs = (
        db.query(models.Activity)
        .filter(
            models.Activity.user_id.in_(student_ids),
            models.Activity.started_at >= week_start,
            models.Activity.is_valid.is_(True),
        )
        .filter(sunshine_run_filter())
        .count()
    )
    pending_health = (
        db.query(models.HealthRequest)
        .filter(models.HealthRequest.student_id.in_(student_ids), models.HealthRequest.status == "pending")
        .count()
    )
    invalid_runs = (
        db.query(models.Activity)
        .filter(
            models.Activity.user_id.in_(student_ids),
            models.Activity.started_at >= week_start,
            models.Activity.is_valid.is_(False),
            models.Activity.fail_reason.isnot(None),
        )
        .filter(sunshine_run_filter())
        .count()
    )
    distance_sum = (
        db.query(func.sum(models.ActivityMetrics.distance))
        .join(models.Activity, models.Activity.id == models.ActivityMetrics.activity_id)
        .filter(models.Activity.user_id.in_(student_ids), models.Activity.started_at >= week_start)
        .scalar()
        or 0
    )
    distance_km = _normalize_distance_km(distance_sum)

    alerts = []
    if pending_health:
        alerts.append(f"有 {pending_health} 条健康报备待处理。")
    if invalid_runs:
        alerts.append(f"本周有 {invalid_runs} 条运动记录未达标或待核实。")
    if today_runs == 0:
        alerts.append("今日暂未产生阳光跑记录，可以提醒学生按计划完成。")
    if not alerts:
        alerts.append("当前班级运动状态平稳，暂无高优先级风险。")

    return {
        "mode": "local_demo",
        "title": "AI班级简报",
        "summary": f"当前管辖 {len(student_ids)} 名学生，今日阳光跑 {today_runs} 人次，本周有效运动 {valid_week_runs} 人次，累计里程约 {distance_km:.1f} 公里。",
        "alerts": alerts[:3],
        "actions": ["优先处理健康报备和异常记录。", "对连续未完成训练的学生单独提醒。", "将本周完成情况同步到课堂或跑团活动中。"],
        "disclaimer": "AI简报用于教学管理辅助，具体处理请结合教师判断。",
    }
