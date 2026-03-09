@echo off
echo ========================================
echo   Campus Sports System - GitHub Push
echo ========================================
echo.

REM 检查Git状态
echo [1/5] Checking Git status...
git status
echo.

REM 添加所有更改
echo [2/5] Adding all changes...
git add .
echo.

REM 提交更改
echo [3/5] Committing changes...
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg=Update: Campus Sports System

git commit -m "%commit_msg%"
echo.

REM 推送到GitHub
echo [4/5] Pushing to GitHub...
echo.
echo Please make sure you have:
echo 1. Created a GitHub repository
echo 2. Set remote origin: git remote add origin https://github.com/YOUR_USERNAME/campus-sports-system.git
echo.
pause

git push -u origin main
echo.

REM 完成
echo [5/5] Done!
echo.
echo ========================================
echo   Successfully pushed to GitHub!
echo ========================================
echo.
echo Next steps:
echo 1. Visit your GitHub repository
echo 2. Deploy to server: 101.37.24.171
echo 3. Follow GITHUB_DEPLOYMENT_GUIDE.md
echo.
pause
