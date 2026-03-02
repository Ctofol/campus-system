@echo off
echo ========================================
echo Git 提交和推送脚本
echo ========================================
echo.

echo [1/5] 检查Git状态...
git status
echo.

echo [2/5] 添加所有更改...
git add .
echo.

echo [3/5] 提交更改...
set /p commit_msg="请输入提交信息: "
if "%commit_msg%"=="" set commit_msg=Update project files
git commit -m "%commit_msg%"
echo.

echo [4/5] 检查远程仓库...
git remote -v
echo.

echo 如果还没有添加远程仓库，请运行:
echo git remote add origin git@github.com:Ctofol/campus-system.git
echo.

set /p push_confirm="是否推送到GitHub? (y/n): "
if /i "%push_confirm%"=="y" (
    echo [5/5] 推送到GitHub...
    git push -u origin master
    echo.
    echo ✅ 推送成功!
) else (
    echo ❌ 取消推送
)

echo.
echo 完成!
pause
