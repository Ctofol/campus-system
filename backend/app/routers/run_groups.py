"""
Run Group Router (跑团联盟)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List
from datetime import datetime, timedelta

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/run-group", tags=["run-groups"])


# ==================== 跑团管理 ====================

@router.post("/create", response_model=schemas.RunGroupOut)
async def create_run_group(
    group_in: schemas.RunGroupCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """创建跑团"""
    # 检查跑团名称是否已存在
    existing = db.query(models.RunGroup).filter(models.RunGroup.name == group_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="跑团名称已存在")
    
    # 检查用户是否已加入其他跑团
    existing_membership = db.query(models.RunGroupMember).filter(
        models.RunGroupMember.user_id == current_user.id
    ).first()
    
    if existing_membership:
        # 自动退出原跑团
        old_group = existing_membership.group
        old_group.member_count = max(0, old_group.member_count - 1)
        db.delete(existing_membership)
    
    # 创建跑团
    new_group = models.RunGroup(
        **group_in.dict(),
        creator_id=current_user.id
    )
    db.add(new_group)
    db.flush()
    
    # 创建者自动成为成员
    member = models.RunGroupMember(
        group_id=new_group.id,
        user_id=current_user.id,
        role="creator"
    )
    db.add(member)
    db.commit()
    db.refresh(new_group)
    
    return new_group


@router.post("/join")
async def join_run_group(
    group_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """加入跑团"""
    # 检查跑团是否存在
    group = db.query(models.RunGroup).filter(models.RunGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="跑团不存在")
    
    # 检查是否已加入当前跑团
    existing = db.query(models.RunGroupMember).filter(
        models.RunGroupMember.group_id == group_id,
        models.RunGroupMember.user_id == current_user.id
    ).first()
    
    if existing:
        return {"joinStatus": False, "message": "您已经是该跑团成员"}
    
    # 检查是否已加入其他跑团
    other_membership = db.query(models.RunGroupMember).filter(
        models.RunGroupMember.user_id == current_user.id
    ).first()
    
    if other_membership:
        # 自动退出原跑团
        old_group = other_membership.group
        old_group.member_count = max(0, old_group.member_count - 1)
        db.delete(other_membership)
    
    # 加入新跑团
    member = models.RunGroupMember(
        group_id=group_id,
        user_id=current_user.id
    )
    db.add(member)
    
    # 更新跑团成员数
    group.member_count += 1
    db.commit()
    
    return {"joinStatus": True, "message": "加入成功"}


@router.get("/my", response_model=schemas.RunGroupDetailOut)
async def get_my_run_group(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """查询当前用户所属跑团"""
    # 查询用户加入的跑团
    member = db.query(models.RunGroupMember).filter(
        models.RunGroupMember.user_id == current_user.id
    ).first()
    
    if not member:
        # 返回null而不是抛出404错误，让前端决定如何处理
        return None
    
    group = member.group
    
    # 计算本月活动数
    now = datetime.utcnow()
    month_activity_count = db.query(models.RunGroupActivity).filter(
        models.RunGroupActivity.group_id == group.id,
        extract('year', models.RunGroupActivity.created_at) == now.year,
        extract('month', models.RunGroupActivity.created_at) == now.month
    ).count()
    
    # 计算排名（按总里程）
    rank_query = db.query(
        models.RunGroup.id,
        func.row_number().over(order_by=models.RunGroup.total_mileage.desc()).label('rank')
    ).subquery()
    
    rank_result = db.query(rank_query.c.rank).filter(rank_query.c.id == group.id).first()
    group.rank = rank_result[0] if rank_result else None
    
    result = schemas.RunGroupDetailOut(
        **group.__dict__,
        month_activity_count=month_activity_count
    )
    
    return result


@router.get("/list", response_model=List[schemas.RunGroupOut])
async def get_run_groups(
    page: int = 1,
    size: int = 20,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """获取跑团列表（用于加入跑团）"""
    groups = db.query(models.RunGroup).order_by(
        models.RunGroup.total_mileage.desc()
    ).offset((page - 1) * size).limit(size).all()
    
    return groups


# ==================== 活动管理 ====================

@router.get("/activity/list", response_model=schemas.RunGroupActivityListResponse)
async def get_activities(
    page: int = 1,
    size: int = 10,
    status: str = None,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """查询最新活动列表"""
    query = db.query(models.RunGroupActivity)
    
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


@router.post("/activity/create", response_model=schemas.RunGroupActivityOut)
async def create_activity(
    activity_in: schemas.RunGroupActivityCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """创建活动（跑团管理员）"""
    # 检查是否是跑团成员
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
    
    return new_activity


@router.post("/activity/apply")
async def apply_activity(
    activity_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """活动报名"""
    # 检查活动是否存在
    activity = db.query(models.RunGroupActivity).filter(
        models.RunGroupActivity.id == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    
    # 检查是否已报名
    existing = db.query(models.RunGroupActivityApplication).filter(
        models.RunGroupActivityApplication.activity_id == activity_id,
        models.RunGroupActivityApplication.user_id == current_user.id
    ).first()
    
    if existing:
        return {"applyStatus": False, "message": "您已报名该活动"}
    
    # 检查名额
    if activity.apply_count >= activity.total_quota:
        return {"applyStatus": False, "message": "活动名额已满"}
    
    # 报名
    application = models.RunGroupActivityApplication(
        activity_id=activity_id,
        user_id=current_user.id
    )
    db.add(application)
    
    # 更新报名人数
    activity.apply_count += 1
    db.commit()
    
    return {"applyStatus": True, "message": "报名成功"}


@router.get("/activity/{activity_id}", response_model=schemas.RunGroupActivityOut)
async def get_activity_detail(
    activity_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """获取活动详情"""
    activity = db.query(models.RunGroupActivity).filter(
        models.RunGroupActivity.id == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    
    return activity


# ==================== 排行榜 ====================

@router.post("/leave")
async def leave_run_group(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """退出跑团"""
    # 查询用户当前加入的跑团
    member = db.query(models.RunGroupMember).filter(
        models.RunGroupMember.user_id == current_user.id
    ).first()
    
    if not member:
        return {"success": False, "message": "您还未加入任何跑团"}
    
    # 获取跑团
    group = member.group
    
    # 如果是创建者且跑团还有其他成员，需要先转让
    if member.role == "creator" and group.member_count > 1:
        # 查找其他成员
        other_members = db.query(models.RunGroupMember).filter(
            models.RunGroupMember.group_id == group.id,
            models.RunGroupMember.user_id != current_user.id
        ).all()
        
        if other_members:
            # 自动将创建者权限转让给第一个成员
            other_members[0].role = "creator"
    
    # 删除成员记录
    db.delete(member)
    
    # 更新跑团成员数
    group.member_count = max(0, group.member_count - 1)
    
    # 如果跑团没有成员了，删除跑团
    if group.member_count == 0:
        db.delete(group)
    
    db.commit()
    
    return {"success": True, "message": "退出成功"}


@router.post("/activity/cancel")
async def cancel_activity_application(
    activity_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """取消活动报名"""
    # 检查活动是否存在
    activity = db.query(models.RunGroupActivity).filter(
        models.RunGroupActivity.id == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    
    # 检查活动状态
    if activity.status == "ongoing" or activity.status == "finished":
        raise HTTPException(status_code=400, detail="活动已开始或已结束，无法取消报名")
    
    # 查询报名记录
    application = db.query(models.RunGroupActivityApplication).filter(
        models.RunGroupActivityApplication.activity_id == activity_id,
        models.RunGroupActivityApplication.user_id == current_user.id
    ).first()
    
    if not application:
        return {"success": False, "message": "您还未报名该活动"}
    
    # 删除报名记录
    db.delete(application)
    
    # 更新报名人数（不小于0）
    if activity.apply_count > 0:
        activity.apply_count -= 1
    
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
    """获取跑团成员列表"""
    # 检查跑团是否存在
    group = db.query(models.RunGroup).filter(models.RunGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="跑团不存在")
    
    # 查询成员列表
    members = db.query(models.RunGroupMember).filter(
        models.RunGroupMember.group_id == group_id
    ).order_by(
        models.RunGroupMember.joined_at.asc()
    ).offset((page - 1) * size).limit(size).all()
    
    # 构建返回数据
    result = []
    for member in members:
        result.append(schemas.RunGroupMemberOut(
            id=member.id,
            user_id=member.user_id,
            user_name=member.user.name,
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
    """获取指定跑团的活动列表"""
    # 检查跑团是否存在
    group = db.query(models.RunGroup).filter(models.RunGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="跑团不存在")
    
    # 查询活动列表
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
    """跑团排行榜"""
    # 按总里程排序
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
