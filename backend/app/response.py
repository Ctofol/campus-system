from typing import Any, Optional

from fastapi import status
from fastapi.responses import JSONResponse


class APIResponse:
    """Small helper for endpoints that want a consistent JSON envelope."""

    @staticmethod
    def success(
        data: Any = None,
        msg: str = "ok",
        code: int = status.HTTP_200_OK,
    ) -> dict:
        return {
            "code": code,
            "msg": msg,
            "data": data,
        }

    @staticmethod
    def error(
        msg: str = "error",
        code: int = status.HTTP_400_BAD_REQUEST,
        data: Any = None,
    ) -> dict:
        return {
            "code": code,
            "msg": msg,
            "data": data,
        }

    @staticmethod
    def json_success(
        data: Any = None,
        msg: str = "ok",
        code: int = status.HTTP_200_OK,
        status_code: Optional[int] = None,
    ) -> JSONResponse:
        body = APIResponse.success(data=data, msg=msg, code=code)
        return JSONResponse(status_code=status_code or code, content=body)

    @staticmethod
    def json_error(
        msg: str = "error",
        code: int = status.HTTP_400_BAD_REQUEST,
        data: Any = None,
        status_code: Optional[int] = None,
    ) -> JSONResponse:
        body = APIResponse.error(msg=msg, code=code, data=data)
        return JSONResponse(status_code=status_code or code, content=body)
