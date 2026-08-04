"""系统健康检查接口。"""

import os
import shutil

from fastapi import APIRouter, Response, status
from sqlalchemy import text

from .. import config, database


router = APIRouter(prefix="/system", tags=["system"])


@router.get("/health")
def health_check(response: Response):
    """返回服务、数据库、存储和 AI 配置状态，不泄露内部路径或密钥。"""

    checks = {"database": "ok"}
    try:
        with database.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        checks["database"] = "unavailable"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "degraded", "checks": checks}

    upload_root = "/app/uploads" if os.path.exists("/app/uploads") else os.path.join(database.PROJECT_ROOT, "uploads")
    try:
        os.makedirs(upload_root, exist_ok=True)
        usage = shutil.disk_usage(upload_root)
        checks["storage"] = "ok" if usage.free >= 512 * 1024 * 1024 else "low_space"
        storage = {"free_mb": usage.free // (1024 * 1024)}
    except OSError:
        checks["storage"] = "unavailable"
        storage = {}

    if config.FACE_PROVIDER == "none":
        checks["face_verification"] = "disabled"
    elif config.FACE_PROVIDER == "tencent":
        checks["face_verification"] = "configured" if config.TENCENT_SECRET_ID and config.TENCENT_SECRET_KEY else "misconfigured"
    else:
        checks["face_verification"] = "configured"

    status_value = "ok" if all(value in {"ok", "disabled", "configured"} for value in checks.values()) else "degraded"
    if status_value == "degraded":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {"status": status_value, "checks": checks, "storage": storage}
