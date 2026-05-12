"""
文件上传路由模块
处理视频和图片文件上传
"""
import os
import uuid
import shutil
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from .. import auth, database

router = APIRouter(prefix="/upload", tags=["upload"])

# 文件大小限制（字节）
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB
MAX_IMAGE_SIZE = 5 * 1024 * 1024    # 5MB

# 允许的文件类型
ALLOWED_VIDEO_EXTENSIONS = {".mp4"}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_VIDEO_MIMES = {"video/mp4"}
ALLOWED_IMAGE_MIMES = {"image/jpeg", "image/jpg", "image/png"}


def _mime_ok_for_video(content_type: Optional[str]) -> bool:
    """小程序 / 部分客户端上传时 Content-Type 常为 octet-stream 或缺省，在扩展名已校验的前提下放宽匹配。"""
    if not content_type:
        return True
    main = content_type.split(";")[0].strip().lower()
    if main in ALLOWED_VIDEO_MIMES:
        return True
    if main == "application/octet-stream":
        return True
    return main.startswith("video/")


def _mime_ok_for_image(content_type: Optional[str]) -> bool:
    if not content_type:
        return True
    main = content_type.split(";")[0].strip().lower()
    if main in ALLOWED_IMAGE_MIMES or main == "image/jpg":
        return True
    if main == "application/octet-stream":
        return True
    return main.startswith("image/")


def _infer_store_ext_when_missing(
    file: UploadFile, file_ext: str
) -> tuple[str, str] | None:
    """
    微信小程序等客户端 multipart 里常见「无后缀临时文件名」，按 Content-Type 推断存储后缀。
    返回 (file_type, store_ext) 或 None 表示不能由此路径识别。
    """
    if file_ext:
        return None
    ct = (file.content_type or "").split(";")[0].strip().lower()
    if _mime_ok_for_video(file.content_type):
        # 仅对常见「实为 MP4 容器」的上传放宽；其它 video/* 避免误标成 .mp4
        if ct in ("", "application/octet-stream", "video/mp4") or ct == "video/mpeg":
            if file.size and file.size > MAX_VIDEO_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"视频文件大小不能超过{MAX_VIDEO_SIZE // (1024*1024)}MB",
                )
            return ("video", ".mp4")
        raise HTTPException(
            status_code=400,
            detail="请上传 MP4 视频（当前为无后缀或非 MP4 类型流）",
        )
    if _mime_ok_for_image(file.content_type):
        if file.size and file.size > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"图片文件大小不能超过{MAX_IMAGE_SIZE // (1024*1024)}MB",
            )
        if ct == "image/png":
            return ("image", ".png")
        if ct in ("image/jpeg", "image/jpg", "application/octet-stream", ""):
            return ("image", ".jpg")
        raise HTTPException(
            status_code=400,
            detail="无后缀图片请使用 JPG 或 PNG（不支持该 MIME 推断）",
        )
    return None


def validate_file(file: UploadFile) -> tuple[str, str]:
    """
    校验上传并返回存储用扩展名（带点），兼容无后缀文件名。

    Returns:
        (file_type, store_ext)  file_type 为 "video" | "image"，store_ext 如 ".mp4"、".jpg"
    """
    raw_name = (file.filename or "").strip()
    file_ext = os.path.splitext(raw_name)[1].lower()

    inferred = _infer_store_ext_when_missing(file, file_ext)
    if inferred is not None:
        return inferred

    if not raw_name:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    if file_ext in ALLOWED_VIDEO_EXTENSIONS:
        if not _mime_ok_for_video(file.content_type):
            raise HTTPException(status_code=400, detail="视频文件Content-Type不匹配")
        if file.size and file.size > MAX_VIDEO_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"视频文件大小不能超过{MAX_VIDEO_SIZE // (1024*1024)}MB",
            )
        return ("video", ".mp4")
    if file_ext in ALLOWED_IMAGE_EXTENSIONS:
        if not _mime_ok_for_image(file.content_type):
            raise HTTPException(status_code=400, detail="图片文件Content-Type不匹配")
        if file.size and file.size > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"图片文件大小不能超过{MAX_IMAGE_SIZE // (1024*1024)}MB",
            )
        return ("image", file_ext)
    raise HTTPException(
        status_code=400,
        detail="不支持的文件类型，仅支持MP4视频和JPG/PNG图片",
    )


@router.post("/file")
async def upload_file(
    file: UploadFile = File(...),
    current_user = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """
    上传文件接口
    
    Args:
        file: 上传的文件
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        dict: 包含文件URL、类型和大小的响应
    """
    try:
        # 验证文件，得到存储后缀（兼容微信临时文件无 .mp4 后缀）
        file_type, store_ext = validate_file(file)
        
        # 创建按月份分组的目录
        # 开发环境: 使用项目目录下的 uploads 文件夹
        # 生产环境(Docker): 使用 /app/uploads
        current_date = datetime.now()
        month_dir = current_date.strftime("%Y%m")
        if os.path.exists("/app/uploads"):
            upload_dir = os.path.join("/app/uploads", month_dir)
        else:
            # 本地开发模式，使用相对路径
            upload_dir = os.path.join("uploads", month_dir)
        
        # 确保目录存在
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4()}{store_ext}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        
        # 返回文件信息
        return {
            "url": f"/uploads/{month_dir}/{unique_filename}",
            "type": file_type,
            "size": file_size,
            "original_filename": file.filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")