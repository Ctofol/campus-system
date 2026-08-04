"""上线前环境自检：只读检查，不修改数据库、文件或配置。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# 支持从 backend 目录通过 ``python scripts/preflight.py`` 直接执行。
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import text

from app import config, database


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    production = config.APP_ENV == "production"

    try:
        config.validate_runtime_config(strict=production)
    except ValueError as exc:
        errors.append(str(exc))

    if not production:
        warnings.append("APP_ENV 不是 production；正式上线前请设置为 production")
    if config.ACCESS_TOKEN_EXPIRE_MINUTES > 60 * 24 * 14:
        warnings.append("登录有效期超过 14 天；请确认这符合学校账号安全要求")

    try:
        with database.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        errors.append("数据库连接不可用")

    upload_root = "/app/uploads" if os.path.exists("/app/uploads") else os.path.join(database.PROJECT_ROOT, "uploads")
    if not os.path.isdir(upload_root):
        errors.append("上传目录不存在或不可访问")
    elif not os.access(upload_root, os.W_OK):
        errors.append("上传目录不可写")

    for item in warnings:
        print(f"[WARN] {item}")
    for item in errors:
        print(f"[ERROR] {item}")
    if errors:
        return 1
    print("[OK] 上线前基础检查通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
