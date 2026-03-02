"""
统一API响应格式模块
提供标准化的响应格式和错误处理
"""
from typing import Any, Optional
from fastapi import status
from fastapi.responses import JSONResponse


class APIResponse:
    """统一API响应格式"""
    
    @staticmethod
    def success(
        data: Any = None,
        msg: str = "操作成功",
        code: int = 200
    ) -> dict:
        """
        成功响应
        
        Args:
            data: 业务数据
            msg: 提示信息
            code: 状态码
          