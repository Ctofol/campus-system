# 本地开发

## 环境

- Python 3.10–3.12（AI 依赖对更新版本 Python 的支持可能滞后）
- Node.js 18+
- HBuilderX（运行学生/教师端时需要）
- SQLite（默认）或 PostgreSQL

## 安装

```powershell
python -m venv backend/.venv
backend/.venv/Scripts/Activate.ps1
python -m pip install -r backend/requirements-dev.txt

cd admin/frontend
npm install
```

## 统一命令

从仓库根目录执行：

```powershell
.\scripts\dev-backend.ps1
.\scripts\dev-admin.ps1
.\scripts\test-backend.ps1
.\scripts\check.ps1
.\scripts\migrate.ps1
```

学生/教师端仍使用 HBuilderX 单独打开 `fronted/`。不要打开仓库根目录或 `admin/` 作为 uni-app 项目。

## 验证原则

- 后端改动至少执行 `python -m pytest`。
- 管理端改动至少执行 `npm run build`。
- 数据库结构改动必须新增 Alembic revision。
- 修复缺陷时，先增加能够复现问题的回归测试。

当前 Ruff 基线覆盖配置、启动、路由注册、迁移及新增基础设施。旧业务模块的历史告警应按业务域渐进清理，避免为一次性通过格式检查而混入行为变更。

## 本地数据

数据库、上传文件、日志与 `.env` 不应提交。测试使用独立数据库，禁止让自动化测试连接生产数据库。
