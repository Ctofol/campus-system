import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from . import models, database
from .routers.teacher import router as teacher_router
from .routers.courses import router as courses_router
from .routers.student import router as student_router
from .routers.upload import router as upload_router
from .routers.run_groups import router as run_groups_router
from .routers.admin import router as admin_router
from .routers.common import router as common_router
from .routers.auth import router as auth_router
from .routers.user import router as user_router
from .routers.activity import router as activity_router

# 初始化数据库表
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Campus Sports Health System API")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# 挂载静态文件目录（必须在路由注册之前）
# 开发环境: 使用项目目录下的 uploads 文件夹
# 生产环境(Docker): 使用 /app/uploads
if os.path.exists("/app/uploads"):
    uploads_dir = "/app/uploads"
else:
    # 本地开发模式，使用相对路径
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    uploads_dir = os.path.join(backend_dir, "uploads")

if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# 引入模块化路由
app.include_router(auth_router)
app.include_router(common_router)
app.include_router(user_router)
app.include_router(student_router)
app.include_router(teacher_router)
app.include_router(activity_router)
app.include_router(courses_router)
app.include_router(upload_router)
app.include_router(run_groups_router)
app.include_router(admin_router)

# 挂载管理端前端静态文件
admin_frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "admin", "frontend", "dist")
if os.path.exists(admin_frontend_path):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import RedirectResponse
    
    @app.get("/admin", include_in_schema=False)
    async def admin_index():
        return RedirectResponse(url="/admin/")
    
    @app.get("/admin/", include_in_schema=False)
    async def admin_spa_fallback():
        from fastapi.responses import FileResponse
        return FileResponse(os.path.join(admin_frontend_path, "index.html"))
    
    app.mount("/admin", StaticFiles(directory=admin_frontend_path), name="admin")

@app.get("/")
async def root():
    return {"message": "Welcome to Campus Sports Health System API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
