@echo off
chcp 65001 >nul
echo =========================================
echo 测试视频播放API
echo =========================================
echo.

set SERVER=http://120.26.17.147:8000

echo 1. 测试登录...
curl -X POST "%SERVER%/auth/login" -H "Content-Type: application/json" -d "{\"phone\":\"13800000001\",\"password\":\"123456\"}" > login_response.txt
echo 登录响应已保存到 login_response.txt
echo.

echo 2. 请手动从 login_response.txt 中复制 access_token
echo 然后运行以下命令测试API（替换 YOUR_TOKEN）:
echo.
echo curl -X GET "%SERVER%/courses/?page=1&size=10" -H "Authorization: Bearer YOUR_TOKEN"
echo.
echo curl -X GET "%SERVER%/courses/content/1" -H "Authorization: Bearer YOUR_TOKEN"
echo.
echo curl -X GET "%SERVER%/courses/content/1/progress" -H "Authorization: Bearer YOUR_TOKEN"
echo.
echo curl -X POST "%SERVER%/courses/content/1/progress?last_position=120&completed=false" -H "Authorization: Bearer YOUR_TOKEN"
echo.

pause
