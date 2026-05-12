# -*- coding: utf-8 -*-
"""
空白库一次性搭建：建全表 → 补历史缺列（幂等）→ 首个管理员 → 默认体育选科。

适用：新建 PostgreSQL / SQLite 库、或表已被清空需从零恢复结构并可登录管理端。

用法（与线上 API 使用相同的 SQLALCHEMY_DATABASE_URL）：
  cd backend
  python setup_database.py

Docker（WORKDIR=/app）：
  docker compose exec campus-backend python /app/setup_database.py

环境变量（可选）：
  ADMIN_PHONE     默认 admin
  ADMIN_PASSWORD  默认 admin123
  ADMIN_NAME      默认 管理员
  SKIP_ADMIN=1    不创建/不检查管理员（仅结构）
"""
from __future__ import annotations

import os
import re
import sys

_BACKEND_ROOT = os.path.dirname(os.path.abspath(__file__))
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)


def _mask_database_url(url: str) -> str:
    if not url:
        return "(empty)"
    return re.sub(r"(postgresql[+a-z]*://)([^:]+):([^@]+)@", r"\1\2:***@", url, flags=re.I)


def _ensure_admin() -> None:
    if os.environ.get("SKIP_ADMIN", "").strip() in ("1", "true", "yes"):
        print(">>> Step 3: SKIP_ADMIN=1，跳过管理员创建。")
        return

    from app.database import SessionLocal
    from app import models, auth

    phone = os.environ.get("ADMIN_PHONE", "admin").strip() or "admin"
    password = os.environ.get("ADMIN_PASSWORD", "admin123")
    name = os.environ.get("ADMIN_NAME", "管理员").strip() or "管理员"

    db = SessionLocal()
    try:
        u = db.query(models.User).filter(models.User.phone == phone).first()
        if u:
            if u.role != "admin":
                u.role = "admin"
                db.commit()
                print(f">>> Step 3: 已将用户 {phone} 设为管理员。")
            else:
                print(f">>> Step 3: 管理员已存在 ({phone})，跳过创建。")
            return

        db.add(
            models.User(
                phone=phone,
                name=name,
                password_hash=auth.get_password_hash(password),
                role="admin",
            )
        )
        db.commit()
        print(f">>> Step 3: 已创建管理员 phone={phone!r} name={name!r}")
        print("!!! 请在首次登录后立即修改默认密码（勿在生产长期使用默认口令）。")
    finally:
        db.close()


def _ensure_default_subject_options() -> None:
    """与 app.routers.admin.DEFAULT_SUBJECT_NAMES 对齐，避免首屏选科库为空。"""
    from app.database import SessionLocal
    from app import models

    names = ["篮球", "羽毛球", "乒乓球", "游泳", "网球", "跆拳道"]
    db = SessionLocal()
    try:
        if db.query(models.SubjectOption).first() is not None:
            print(">>> Step 4: subject_options 已有数据，跳过默认选科。")
            return
        for i, n in enumerate(names):
            db.add(models.SubjectOption(name=n, sort_order=i))
        db.commit()
        print(f">>> Step 4: 已写入默认选科 {len(names)} 条。")
    finally:
        db.close()


def main() -> int:
    from app.database import engine, Base, SQLALCHEMY_DATABASE_URL

    print("=== campus-system 数据库一次性搭建 ===")
    print(">>> 连接:", _mask_database_url(SQLALCHEMY_DATABASE_URL))

    print(">>> Step 1: 根据 models 创建全部缺失的表 (metadata.create_all) …")
    Base.metadata.create_all(bind=engine)

    print(">>> Step 2: 执行 db_update_production（补列，幂等；新库多为 [skip]）…")
    from db_update_production import upgrade_database

    upgrade_database()

    _ensure_admin()
    _ensure_default_subject_options()

    print("\n[done] 搭建完成。请启动 API 后用管理员账号登录管理端验证。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
