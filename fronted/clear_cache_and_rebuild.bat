@echo off
echo ========================================
echo 清除缓存并重新编译
echo ========================================
echo.

echo [1/3] 删除 unpackage 文件夹...
if exist unpackage (
    rmdir /s /q unpackage
    echo 已删除 unpackage 文件夹
) else (
    echo unpackage 文件夹不存在
)
echo.

echo [2/3] 检查后端服务状态...
curl -s http://127.0.0.1:8000/common/captcha >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ 后端服务正常运行
) else (
    echo ✗ 后端服务未运行或无法访问
    echo   请先启动后端服务
)
echo.

echo [3/3] 完成！
echo.
echo 接下来请：
echo 1. 在 HBuilderX 中重新运行到微信开发者工具
echo 2. 在微信开发者工具中：
echo    - 点击"详情" - "本地设置"
echo    - 确保勾选"不校验合法域名..."
echo 3. 如果还是不行，在微信开发者工具中：
echo    - 点击"工具" - "清除缓存" - "清除全部缓存"
echo.
pause
