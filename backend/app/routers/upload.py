"""
文件上传路由模块
处理视频和图片文件上传
"""
import os
import uuid
import shutil
from datetime import datetime
from typing import List
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


def validate_file(file: UploadFile) -> str:
    """
    验证上传文件的类型和大小
    
    Args:
        file: 上传的文件
        
    Returns:
        str: 文件类型 ("video" 或 "image")
        
    Raises:
        HTTPException: 验证失败时抛出异常
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")
    
    # 获取文件扩展名
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    # 验证文件类型和大小
    if file_ext in ALLOWED_VIDEO_EXTENSIONS:
        if file.content_type not in ALLOWED_VIDEO_MIMES:
            raise HTTPException(status_code=400, detail="视频文件Content-Type不匹配")
        if file.size and file.size > MAX_VIDEO_SIZE:
            raise HTTPException(status_code=400, detail=f"视频文件大小不能超过{MAX_VIDEO_SIZE // (1024*1024)}MB")
        return "video"
    elif file_ext in ALLOWED_IMAGE_EXTENSIONS:
        if file.content_type not in ALLOWED_IMAGE_MIMES:
            raise HTTPException(status_code=400, detail="图片文件Content-Type不匹配")
        if file.size and file.size > MAX_IMAGE_SIZE:
            raise HTTPException(status_code=400, detail=f"图片文件大小不能超过{MAX_IMAGE_SIZE // (1024*1024)}MB")
        return "image"
    else:
        raise HTTPException(status_code=400, detail="不支持的文件类型，仅支持MP4视频和JPG/PNG图片")


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
        # 验证文件
        file_type = validate_file(file)
        
        # 创建按月份分组的目录
        current_date = datetime.now()
        month_dir = current_date.strftime("%Y%m")
        upload_dir = os.path.join("uploads", month_dir)
        
        # 确保目录存在
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成唯一文件名
        file_ext = os.path.splitext(file.filename)[1].lower()
        unique_filename = f"{uuid.uuid4()}{file_ext}"
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