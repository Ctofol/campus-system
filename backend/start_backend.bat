@echo off
echo ========================================
echo 启动翊晨运动后端服务
echo ========================================
echo.

REM 检查是否在 backend 目录
if not exist "app\main.py" (
    echo 错误: 请在 backend 目录下运行此脚本
    echo 当前目录: %CD%
    pause
    exit /b 1
)

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo 1. 检查虚拟环境...
if exist ".venv\Scripts\activate.bat" (
    echo    找到虚拟环境，正在激活...
    call .venv\Scripts\activate.bat
) else (
    echo    未找到虚拟环境，使用全局 Python
)

echo.
echo 2. 检查依赖...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo    缺少依赖，正在安装...
    pip install -r requirements.txt
)

echo.
echo 3. 检查端口占用...
netstat -ano | findstr :8000 >nul 2>&1
if not errorlevel 1 (
    echo    警告: 端口 8000 已被占用
    echo    正在尝试关闭占用进程...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 >nul
)

echo.
echo 4. 启动后端服务...
echo    访问地址: http://127.0.0.1:8000
echo    API 文档: http://127.0.0.1:8000/docs
echo    网络访问: http://192.168.0.216:8000
echo.
echo    按 Ctrl+C 停止服务
echo ========================================
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
