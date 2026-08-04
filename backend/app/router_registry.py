"""应用路由注册表。

集中注册可让业务路由渐进迁入 modules/，同时保持 main.py 与公开路径稳定。
"""

from fastapi import FastAPI

from .routers.activity import router as activity_router
from .routers.admin import router as admin_router
from .routers.ai_assistant import router as ai_assistant_router
from .routers.auth import router as auth_router
from .routers.common import router as common_router
from .routers.courses import router as courses_router
from .routers.feedback_diagnose import router as feedback_diagnose_router
from .routers.medal import router as medal_router
from .routers.notifications import router as notifications_router
from .routers.notification_campaigns import manage_router as notification_manage_router, teacher_router as notification_teacher_router
from .routers.run_groups import router as run_groups_router
from .routers.student import router as student_router
from .routers.system import router as system_router
from .routers.teacher import router as teacher_router
from .routers.upload import router as upload_router
from .routers.user import router as user_router


def register_routers(app: FastAPI) -> None:
    """按原有顺序注册全部公开路由。"""

    app.include_router(auth_router)
    app.include_router(common_router)
    app.include_router(system_router)
    app.include_router(user_router)
    app.include_router(student_router)
    app.include_router(teacher_router)
    app.include_router(activity_router)
    app.include_router(notifications_router)
    app.include_router(notification_manage_router)
    app.include_router(notification_teacher_router)
    app.include_router(courses_router)
    app.include_router(upload_router)
    app.include_router(run_groups_router)
    app.include_router(admin_router)
    app.include_router(feedback_diagnose_router)
    app.include_router(medal_router)
    app.include_router(ai_assistant_router)
