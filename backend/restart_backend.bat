@echo off
echo ================================================
echo 重启后端服务
echo ================================================
echo.

echo 正在停止现有服务...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo 正在启动后端服务...
echo 服务地址: http://0.0.0.0:8000
echo 访问地址: http://192.168.0.216:8000
echo.
echo 按 Ctrl+C 停止服务
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
