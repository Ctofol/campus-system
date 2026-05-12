"""学生账号专业字段与行政班所属专业对齐（major_id + major_name）。"""
from sqlalchemy.orm import Session

from .. import models


def sync_student_majors_from_class(db: Session) -> None:
    """
    按学生所在行政班（classes.major_id）写回 users.major_id、users.major_name。
    用于：模拟灌数后纠偏、历史导入仅有 class_id 无专业、管理端列表展示「专业」列。
    """
    students = (
        db.query(models.User)
        .filter(models.User.role == "student", models.User.class_id.isnot(None))
        .all()
    )
    for u in students:
        cls = db.query(models.Class).filter(models.Class.id == u.class_id).first()
        if not cls or not cls.major_id:
            continue
        mj = db.query(models.Major).filter(models.Major.id == cls.major_id).first()
        if not mj:
            continue
        need_id = u.major_id != cls.major_id
        need_name = (u.major_name or "").strip() != (mj.name or "").strip()
        if need_id or need_name:
            u.major_id = cls.major_id
            u.major_name = mj.name
    db.commit()
