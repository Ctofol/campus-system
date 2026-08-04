"""
Run Group Router (璺戝洟鑱旂洘)
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
import json
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import datetime, timedelta

from .. import models, schemas, auth
from ..database import get_db
from ..services.notification_service import create_notification, create_notifications
from ..services.audit_service import record_audit

router = APIRouter(prefix="/run-group", tags=["run-groups"])


def _build_group_detail(db: Session, group: models.RunGroup, role: Optional[str] = None):
    now = datetime.utcnow()
    month_activity_count = db.query(models.RunGroupActivity).filter(
        models.RunGroupActivity.group_id == group.id,
        extract('year', models.RunGroupActivity.created_at) == now.year,
        extract('month', models.RunGroupActivity.created_at) == now.month
    ).count()

    rank_query = db.query(
        models.RunGroup.id,
        func.row_number().over(order_by=models.RunGroup.total_mileage.desc()).label('rank')
    ).subquery()
    rank_result = db.query(rank_query.c.rank).filter(rank_query.c.id == group.id).first()
    group.rank = rank_result[0] if rank_result else None

    payload = {
        **group.__dict__,
        "month_activity_count": month_activity_count
    }
    if role is not None:
        payload["role"] = role
        return schemas.RunGroupMembershipOut(**payload)
    return schemas.RunGroupDetailOut(**payload)


# ==================== 璺戝洟绠＄悊 ====================

@router.post("/create", response_model=schemas.RunGroupOut)
async def create_run_group(
    group_in: schemas.RunGroupCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Create a run group."""
    group_name = (group_in.name or "").strip()
    if not group_name:
        raise HTTPException(status_code=400, detail="跑团名称不能为空")

    existing = db.query(models.RunGroup).filter(models.RunGroup.name == group_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="跑团名称已存在")

    new_group = models.RunGroup(
        **group_in.dict(),
        name=group_name,
        creator_id=current_user.id
    )
    db.add(new_group)
    db.flush()

    member = models.RunGroupMember(
        group_id=new_group.id,
        user_id=current_user.id,
        role="creator"
    )
    db.add(member)
    db.commit()
    db.refresh(new_group)

    return new_group


@router.put("/{group_id}", response_model=schemas.RunGroupDetailOut)
async def update_run_group(
    group_id: int,
    group_in: schemas.RunGroupUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Update basic info for a run group created by the current user."""
    member = db.query(models.RunGroupMember).filter(
        models.RunGroupMember.group_id == group_id,
        models.RunGroupMember.user_id == current_user.id
    ).first()

    if not member or not member.group:
        raise HTTPException(status_code=404, detail="您未加入该跑团")

    if member.role != "creator":
        raise HTTPException(status_code=403, detail="只有跑团创建者可以修改跑团资料")

    group = member.group

    if group_in.name is not None:
        group_name = group_in.name.strip()
        if not group_name:
            raise HTTPException(status_code=400, detail="跑团名称不能为空")
        existing = db.query(models.RunGroup).filter(
            models.RunGroup.name == group_name,
            models.RunGroup.id != group_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="跑团名称已存在")
        group.name = group_name

    if group_in.description is not None:
        group.description = group_in.description.strip() or None

    if group_in.avatar is not None:
        group.avatar = group_in.avatar.strip() or None

    db.commit()
    db.refresh(group)
    return _build_group_detail(db, group, member.role)


@router.post("/join")
async def join_run_group(
    group_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Join a run group without replacing existing memberships."""
    group = db.query(models.RunGroup).filter(
        models.RunGroup.id == group_id,
        models.RunGroup.status == "active",
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="跑团不存在")

    existing = db.query(models.RunGroupMember).filter(
        models.RunGroupMember.group_id == group_id,
        models.RunGroupMember.user_id == current_user.id
    ).first()

    if existing:
        return {"joinStatus": False, "message": "您已加入该跑团"}

    member = models.RunGroupMember(
        group_id=group_id,
        user_id=current_user.id
    )
    db.add(member)

    group.member_count = (group.member_count or 0) + 1
    db.commit()

    return {"joinStatus": True, "message": "加入成功"}


@router.get("/my", response_model=schemas.RunGroupDetailOut)
async def get_my_run_group(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Return the first joined run group for backward compatibility."""
    member = db.query(models.RunGroupMember).filter(
        models.RunGroupMember.user_id == current_user.id,
        models.RunGroupMember.group.has(models.RunGroup.status == "active"),
    ).order_by(models.RunGroupMember.joined_at.asc()).first()

    if not member:
        return Response(status_code=204)

    return _build_group_detail(db, member.group)


@router.get("/my-groups", response_model=List[schemas.RunGroupMembershipOut])
async def get_my_run_groups(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Return all run groups joined by the current user."""
    memberships = db.query(models.RunGroupMember).filter(
        models.RunGroupMember.user_id == current_user.id,
        models.RunGroupMember.group.has(models.RunGroup.status == "active"),
    ).order_by(models.RunGroupMember.joined_at.asc()).all()

    return [_build_group_detail(db, membership.group, membership.role) for membership in memberships]


@router.get("/list", response_model=List[schemas.RunGroupOut])
async def get_run_groups(
    page: int = 1,
    size: int = 20,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """List available run groups."""
    # 鍙繑鍥炴湁鏈夋晥鎴愬憳鏁扮殑璺戝洟锛岃繃婊ょ┖璺戝洟
    groups = db.query(models.RunGroup).filter(
        models.RunGroup.member_count >= 1,
        models.RunGroup.name.isnot(None),
        models.RunGroup.name != "",
        models.RunGroup.status == "active",
    ).order_by(
        models.RunGroup.total_mileage.desc()
    ).offset((page - 1) * size).limit(size).all()

    return groups


# ==================== 娲诲姩绠＄悊 ====================

@router.get("/activity/list")
async def get_activities(
    page: int = 1,
    size: int = 10,
    status: str = None,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """List recent run group activities."""
    query = db.query(models.RunGroupActivity).join(models.RunGroup).filter(
        models.RunGroup.status == "active"
    )

    if status:
        query = query.filter(models.RunGroupActivity.status == status)

    total = query.count()
    activities = query.order_by(
        models.RunGroupActivity.activity_time.desc()
    ).offset((page - 1) * size).limit(size).all()

    items = [schemas.RunGroupActivityOut.model_validate(a).model_dump(mode="json") for a in activities]
    return Response(
        content=json.dumps({"items": items, "total": total, "page": page, "size": size}, ensure_ascii=False, allow_nan=False),
        media_type="application/json"
    )


@router.post("/activity/create", response_model=schemas.RunGroupActivityOut)
async def create_activity(
    activity_in: schemas.RunGroupActivityCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Create a run group activity."""
    # 妫€鏌ユ槸鍚︽槸璺戝洟鎴愬憳
    member = db.query(models.RunGroupMember).filter(
        models.RunGroupMember.group_id == activity_in.group_id,
        models.RunGroupMember.user_id == current_user.id
    ).first()

    if not member or member.role not in ['creator', 'admin']:
        raise HTTPException(status_code=403, detail="只有跑团管理员可以创建活动")

    new_activity = models.RunGroupActivity(
        **activity_in.dict(),
        created_by=current_user.id
    )
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)

    members = (
        db.query(models.RunGroupMember.user_id)
        .filter(models.RunGroupMember.group_id == activity_in.group_id)
        .all()
    )
    create_notifications(
        db,
        [row.user_id for row in members if row.user_id != current_user.id],
        "跑团发布新活动",
        f"跑团发布了活动「{new_activity.title}」，快去查看报名信息。",
        "run_group_activity",
        {"activity_id": new_activity.id, "group_id": activity_in.group_id},
        sender_user_id=current_user.id,
        source_type="run_group_activity",
        source_id=new_activity.id,
        action_type="run_group_activity",
        action_data={"activity_id": new_activity.id, "group_id": activity_in.group_id},
        event_key_factory=lambda uid: f"run_group_activity:{new_activity.id}",
    )
    db.commit()

    return new_activity


@router.post("/activity/apply")
async def apply_activity(
    activity_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """娲诲姩鎶ュ悕"""
    # 妫€鏌ユ椿鍔ㄦ槸鍚﹀瓨鍦?
    activity = db.query(models.RunGroupActivity).filter(
        models.RunGroupActivity.id == activity_id
    ).first()

    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    if activity.group.status != "active" or activity.status != "upcoming":
        return {"applyStatus": False, "message": "活动当前不可报名"}

    # 妫€鏌ユ槸鍚﹀凡鎶ュ悕
    existing = db.query(models.RunGroupActivityApplication).filter(
        models.RunGroupActivityApplication.activity_id == activity_id,
        models.RunGroupActivityApplication.user_id == current_user.id
    ).first()

    if existing:
        return {"applyStatus": False, "message": "您已报名该活动"}

    updated = db.query(models.RunGroupActivity).filter(
        models.RunGroupActivity.id == activity_id,
        models.RunGroupActivity.status == "upcoming",
        models.RunGroupActivity.apply_count < models.RunGroupActivity.total_quota,
    ).update(
        {models.RunGroupActivity.apply_count: models.RunGroupActivity.apply_count + 1},
        synchronize_session=False,
    )
    if updated != 1:
        db.rollback()
        return {"applyStatus": False, "message": "活动名额已满"}

    application = models.RunGroupActivityApplication(
        activity_id=activity_id,
        user_id=current_user.id
    )
    db.add(application)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        return {"applyStatus": False, "message": "您已报名该活动"}
    db.refresh(activity)
    if activity.created_by and activity.created_by != current_user.id:
        create_notification(
            db,
            activity.created_by,
            "活动报名提醒",
            f"{current_user.display_name or '有成员'}报名了活动「{activity.title}」。",
            "run_group_apply",
            {"activity_id": activity.id, "user_id": current_user.id},
            sender_user_id=current_user.id,
            source_type="run_group_apply",
            source_id=application.id,
            action_type="run_group_activity",
            action_data={"activity_id": activity.id, "group_id": activity.group_id},
            event_key=f"run_group_apply:{activity.id}:{current_user.id}",
        )
    db.commit()

    return {"applyStatus": True, "message": "报名成功"}


@router.get("/activity/{activity_id}", response_model=schemas.RunGroupActivityOut)
async def get_activity_detail(
    activity_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """鑾峰彇娲诲姩璇︽儏"""
    activity = db.query(models.RunGroupActivity).filter(
        models.RunGroupActivity.id == activity_id
    ).first()

    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")

    return activity


# ==================== 鎺掕姒?====================

@router.post("/leave")
async def leave_run_group(
    group_id: Optional[int] = None,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Leave a specific run group."""
    query = db.query(models.RunGroupMember).filter(
        models.RunGroupMember.user_id == current_user.id
    )
    if group_id is not None:
        query = query.filter(models.RunGroupMember.group_id == group_id)
    member = query.first()

    if not member:
        return {"success": False, "message": "您未加入该跑团"}

    group = member.group

    if member.role == "creator" and group.member_count > 1:
        other_members = db.query(models.RunGroupMember).filter(
            models.RunGroupMember.group_id == group.id,
            models.RunGroupMember.user_id != current_user.id
        ).order_by(models.RunGroupMember.joined_at.asc()).all()
        if other_members:
            other_members[0].role = "creator"

    db.delete(member)
    group.member_count = max(0, (group.member_count or 0) - 1)

    if group.member_count == 0:
        group.status = "dissolved"
        group.archived_at = datetime.utcnow()

    db.commit()

    return {"success": True, "message": "退出成功"}


@router.delete("/current")
async def delete_current_run_group(
    group_id: Optional[int] = None,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """解散跑团但保留成员、活动和报名历史。"""
    query = db.query(models.RunGroupMember).filter(
        models.RunGroupMember.user_id == current_user.id
    )
    if group_id is not None:
        query = query.filter(models.RunGroupMember.group_id == group_id)
    member = query.first()

    if not member or not member.group:
        raise HTTPException(status_code=404, detail="您未加入该跑团")

    if member.role != "creator":
        raise HTTPException(status_code=403, detail="只有跑团创建者可以删除跑团")

    group = member.group
    if group.status != "active":
        raise HTTPException(status_code=409, detail="跑团已解散")
    now = datetime.utcnow()
    group.status = "dissolved"
    group.archived_at = now
    db.query(models.RunGroupActivity).filter(
        models.RunGroupActivity.group_id == group.id,
        models.RunGroupActivity.status.in_(["upcoming", "ongoing"]),
    ).update({models.RunGroupActivity.status: "finished"}, synchronize_session=False)
    record_audit(
        db,
        actor=current_user,
        action="run_group.dissolve",
        resource_type="run_group",
        resource_id=group.id,
        detail={"member_count": group.member_count},
    )
    db.commit()

    return {"success": True, "message": "跑团已解散，历史记录已保留"}


@router.post("/activity/cancel")
async def cancel_activity_application(
    activity_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """鍙栨秷娲诲姩鎶ュ悕"""
    # 妫€鏌ユ椿鍔ㄦ槸鍚﹀瓨鍦?
    activity = db.query(models.RunGroupActivity).filter(
        models.RunGroupActivity.id == activity_id
    ).first()

    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")

    # 妫€鏌ユ椿鍔ㄧ姸鎬?
    if activity.status == "ongoing" or activity.status == "finished":
        raise HTTPException(status_code=400, detail="活动已开始或已结束，无法取消报名")

    # 鏌ヨ鎶ュ悕璁板綍
    application = db.query(models.RunGroupActivityApplication).filter(
        models.RunGroupActivityApplication.activity_id == activity_id,
        models.RunGroupActivityApplication.user_id == current_user.id
    ).first()

    if not application:
        return {"success": False, "message": "您还未报名该活动"}

    db.delete(application)
    db.query(models.RunGroupActivity).filter(
        models.RunGroupActivity.id == activity_id,
        models.RunGroupActivity.apply_count > 0,
    ).update(
        {models.RunGroupActivity.apply_count: models.RunGroupActivity.apply_count - 1},
        synchronize_session=False,
    )

    db.commit()

    return {"success": True, "message": "取消报名成功"}


@router.get("/members/{group_id}", response_model=List[schemas.RunGroupMemberOut])
async def get_group_members(
    group_id: int,
    page: int = 1,
    size: int = 20,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """鑾峰彇璺戝洟鎴愬憳鍒楄〃"""
    # 妫€鏌ヨ窇鍥㈡槸鍚﹀瓨鍦?
    group = db.query(models.RunGroup).filter(models.RunGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="跑团不存在")

    # 鏌ヨ鎴愬憳鍒楄〃
    members = db.query(models.RunGroupMember).filter(
        models.RunGroupMember.group_id == group_id
    ).order_by(
        models.RunGroupMember.joined_at.asc()
    ).offset((page - 1) * size).limit(size).all()

    # 鏋勫缓杩斿洖鏁版嵁
    result = []
    for member in members:
        result.append(schemas.RunGroupMemberOut(
            id=member.id,
            user_id=member.user_id,
            user_name=member.user.display_name,
            role=member.role,
            total_mileage=member.total_mileage,
            joined_at=member.joined_at
        ))

    return result


@router.get("/activities/{group_id}", response_model=schemas.RunGroupActivityListResponse)
async def get_group_activities(
    group_id: int,
    page: int = 1,
    size: int = 10,
    status: str = None,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """List activities for a specific run group."""
    # 妫€鏌ヨ窇鍥㈡槸鍚﹀瓨鍦?
    group = db.query(models.RunGroup).filter(models.RunGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="跑团不存在")

    # 鏌ヨ娲诲姩鍒楄〃
    query = db.query(models.RunGroupActivity).filter(
        models.RunGroupActivity.group_id == group_id
    )

    if status:
        query = query.filter(models.RunGroupActivity.status == status)

    total = query.count()
    activities = query.order_by(
        models.RunGroupActivity.activity_time.desc()
    ).offset((page - 1) * size).limit(size).all()

    return {
        "items": activities,
        "total": total,
        "page": page,
        "size": size
    }


@router.get("/rank", response_model=List[schemas.RunGroupRankOut])
async def get_run_group_rank(
    type: str = "mileage",
    limit: int = 50,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get the run group ranking list."""
    # 鎸夋€婚噷绋嬫帓搴?
    groups = db.query(models.RunGroup).order_by(
        models.RunGroup.total_mileage.desc()
    ).limit(limit).all()

    result = []
    for idx, group in enumerate(groups, 1):
        result.append(schemas.RunGroupRankOut(
            group_id=group.id,
            group_name=group.name,
            total_mileage=group.total_mileage,
            rank=idx,
            member_count=group.member_count
        ))

    return result


