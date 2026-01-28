# Campus Sports Health MVP Backend

## 1. 环境准备
- Python 3.8+
- PostgreSQL 数据库

## 2. 安装依赖
在 `backend` 目录下执行：
```bash
pip install -r requirements.txt
```

## 3. 数据库配置
1. 确保 PostgreSQL 服务已启动。
2. 创建一个名为 `campus_db` 的数据库（或者你喜欢的其他名字）。
3. 修改 `backend/app/database.py` 中的 `SQLALCHEMY_DATABASE_URL`：
   ```python
   # 格式: postgresql://username:password@host:port/dbname
   SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@localhost/campus_db"
   ```
   请将 `username`, `password` 等替换为你的实际数据库配置。

## 4. 运行服务
在 `backend` 目录下执行：
```bash
uvicorn app.main:app --reload
```

## 5. 接口文档
启动服务后，访问以下地址查看自动生成的 API 文档：
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## 6. 数据库初始化
服务启动时会自动检测并创建所有数据表（如果不存在）。无需手动执行 SQL 脚本。
