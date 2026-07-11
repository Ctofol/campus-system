from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import func

from .. import models, schemas, auth, database

router = APIRouter(prefix="/medals", tags=["medals"])

get_db = database.get_db

# Medal definitions: key -> (name, description, icon_path)
MEDAL_DEFS = [
    ("run_5k", "5公里跑者", "累计跑步里程达5km", "/static/medals/5k距离勋章.png"),
    ("run_10k", "10公里跑者", "累计跑步里程达10km", "/static/medals/10k距离勋章.png"),
    ("run_21k", "半程马拉松", "累计跑步里程达21km", "/static/medals/21k距离勋章.png"),
    ("run_42k", "全程马拉松", "累计跑步里程达42km", "/static/medals/42k距离勋章.png"),
    ("streak_100", "百日坚持", "累计打卡天数达100天", "/static/medals/打卡100天勋章.png"),
    ("test_perfect", "体测达人", "单次体测AI评分满分", "/static/medals/奖杯图标.png"),
]


def _ensure_medals_exist(db: Session):
    for key, name, desc, icon in MEDAL_DEFS:
        existing = db.query(models.Medal).filter(models.Medal.key == key).first()
        if not existing:
            db.add(models.Medal(key=key, name=name, description=desc, icon_path=icon))
    db.commit()


def _get_user_stats(db: Session, user_id: int):
    # Total valid run distance (km)
    total_distance = db.query(func.sum(models.ActivityMetrics.distance)).join(
        models.Activity
    ).filter(
        models.Activity.user_id == user_id,
        models.Activity.type == "run",
        models.Activity.is_valid == True,
    ).scalar() or 0.0

    # Total unique active days
    active_days = db.query(
        func.count(func.date(models.Activity.started_at))
    ).filter(
        models.Activity.user_id == user_id,
        models.Activity.is_valid == True,
    ).scalar() or 0

    # Best test score
    best_score = db.query(func.max(models.ActivityMetrics.score)).join(
        models.Activity
    ).filter(
        models.Activity.user_id == user_id,
        models.Activity.type == "test",
        models.ActivityMetrics.score.isnot(None),
    ).scalar() or 0

    return {
        "total_distance": round(total_distance, 2),
        "active_days": active_days,
        "best_score": best_score,
    }


def _check_and_award(db: Session, user_id: int) -> list[str]:
    stats = _get_user_stats(db, user_id)
    earned_keys = []

    medal_checks = {
        "run_5k": stats["total_distance"] >= 5,
        "run_10k": stats["total_distance"] >= 10,
        "run_21k": stats["total_distance"] >= 21,
        "run_42k": stats["total_distance"] >= 42,
        "streak_100": stats["active_days"] >= 100,
        "test_perfect": stats["best_score"] >= 100,
    }

    for key, condition in medal_checks.items():
        if not condition:
            continue
        medal = db.query(models.Medal).filter(models.Medal.key == key).first()
        if not medal:
            continue
        exists = db.query(models.UserMedal).filter(
            models.UserMedal.user_id == user_id,
            models.UserMedal.medal_id == medal.id,
        ).first()
        if not exists:
            db.add(models.UserMedal(user_id=user_id, medal_id=medal.id, earned_at=datetime.utcnow()))
            earned_keys.append(key)

    if earned_keys:
        db.commit()
    return earned_keys


@router.get("", response_model=schemas.MedalListOut)
def get_medals(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    _ensure_medals_exist(db)

    all_medals = db.query(models.Medal).all()
    user_medals = db.query(models.UserMedal).filter(
        models.UserMedal.user_id == current_user.id
    ).all()
    earned_map = {um.medal_id: um.earned_at for um in user_medals}

    items = []
    for m in all_medals:
        items.append(schemas.MedalOut(
            id=m.id,
            key=m.key,
            name=m.name,
            description=m.description,
            icon_path=m.icon_path,
            earned=m.id in earned_map,
            earned_at=earned_map.get(m.id),
        ))

    return schemas.MedalListOut(
        medals=items,
        earned_count=len(earned_map),
        total_count=len(all_medals),
    )


@router.post("/check")
def check_medals(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    _ensure_medals_exist(db)
    new_keys = _check_and_award(db, current_user.id)
    return {"new_medals": new_keys}
