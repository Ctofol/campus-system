@echo off
echo ========================================
echo 一键修复并重启后端服务
echo ========================================
echo.

REM 检查是否在 backend 目录
if not exist "app\main.py" (
    echo 错误: 请在 backend 目录下运行此脚本
    pause
    exit /b 1
)

echo 1. 停止现有后端进程...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo    正在停止进程 %%a
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 >nul

echo.
echo 2. 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo    错误: 未找到 Python
    pause
    exit /b 1
)
echo    ✓ Python 已安装

echo.
echo 3. 检查依赖...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo    正在安装依赖...
    pip install -r requirements.txt
)
echo    ✓ 依赖已安装

echo.
echo 4. 测试后端配置...
python -c "from app import main; print('✓ 配置正确')" 2>nul
if errorlevel 1 (
    echo    警告: 配置可能有问题，但继续启动...
)

echo.
echo 5. 启动后端服务...
echo    访问地址:
echo    - 本地: http://127.0.0.1:8000
echo    - 文档: http://127.0.0.1:8000/docs
echo    - 网络: http://192.168.0.216:8000
echo.
echo    按 Ctrl+C 停止服务
echo ========================================
echo.

start "后端服务" python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo 6. 等待服务启动...
timeout /t 3 >nul

echo.
echo 7. 测试服务状态...
python check_backend.py

echo.
echo ========================================
echo 修复完成！
echo ========================================
echo.
echo 下一步:
echo 1. 在浏览器按 Ctrl+Shift+R 刷新页面
echo 2. 或清除缓存后重新访问
echo.
pause
