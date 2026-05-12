# -*- coding: utf-8 -*-
"""创建测试用管理员账号（若不存在）。供自动化测试或本地开发使用。"""
import os
import sys

# 让 backend 根目录在 path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import SessionLocal, engine
from app import models, auth

ADMIN_PHONE = os.environ.get("ADMIN_PHONE", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
ADMIN_NAME = "管理员"


def ensure_schema():
    """确保表存在且必要列存在（兼容旧库缺列）"""
    models.Base.metadata.create_all(bind=engine)
    if "sqlite" not in str(engine.url):
        return
    # SQLite: 若 users 表缺 major 列则添加
    with engine.connect() as conn:
        r = conn.execute(text("PRAGMA table_info(users)"))
        cols = [row[1] for row in r]
        if "major" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN major VARCHAR"))
            conn.commit()


def main():
    ensure_schema()
    db = SessionLocal()
    try:
        u = db.query(models.User).filter(models.User.phone == ADMIN_PHONE).first()
        if u:
            if u.role != "admin":
                u.role = "admin"
                db.commit()
                print(f"已将用户 {ADMIN_PHONE} 设为管理员")
            else:
                print(f"管理员已存在: {ADMIN_PHONE}")
            return 0
        pw_hash = auth.get_password_hash(ADMIN_PASSWORD)
        admin = models.User(
            phone=ADMIN_PHONE,
            name=ADMIN_NAME,
            password_hash=pw_hash,
            role="admin",
        )
        db.add(admin)
        db.commit()
        print(f"已创建管理员: {ADMIN_PHONE} / {ADMIN_PASSWORD}")
        return 0
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        db.rollback()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
