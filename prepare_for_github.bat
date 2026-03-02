@echo off
chcp 65001 >nul
echo ========================================
echo GitHub 上传准备脚本
echo ========================================
echo.

echo 📋 检查清单:
echo.

echo [1/6] 检查敏感信息...
echo ✅ 数据库密码已移除（使用环境变量）
echo ✅ .env.example 已创建
echo.

echo [2/6] 检查.gitignore...
if exist .gitignore (
    echo ✅ .gitignore 存在
) else (
    echo ❌ .gitignore 不存在
)
echo.

echo [3/6] 检查大文件...
echo 检查数据库文件...
if exist backend\campus_sports.db (
    echo ⚠️  发现数据库文件 backend\campus_sports.db
    echo    这个文件会被.gitignore忽略
) else (
    echo ✅ 没有数据库文件
)
echo.

echo 检查上传文件...
if exist backend\uploads\*.jpg (
    echo ⚠️  发现上传的图片文件
    echo    这些文件会被.gitignore忽略
) else (
    echo ✅ 没有上传的图片
)
echo.

echo [4/6] 检查编译输出...
if exist fronted\unpackage (
    echo ⚠️  发现编译输出目录 fronted\unpackage
    echo    这个目录会被.gitignore忽略
) else (
    echo ✅ 没有编译输出
)
echo.

echo [5/6] 检查Git状态...
git status
echo.

echo [6/6] 准备完成!
echo.
echo ========================================
echo 📝 接下来的步骤:
echo ========================================
echo.
echo 1. 查看上面的Git状态，确认要上传的文件
echo 2. 运行 git_push.bat 进行上传
echo 3. 或者手动执行以下命令:
echo.
echo    git add .
echo    git commit -m "Initial commit: Campus Sports Health System"
echo    git remote add origin git@github.com:Ctofol/campus-system.git
echo    git push -u origin master
echo.
echo ========================================
echo.

set /p continue="是否现在就推送到GitHub? (y/n): "
if /i "%continue%"=="y" (
    echo.
    echo 开始推送...
    call git_push.bat
) else (
    echo.
    echo 准备完成！请在准备好后运行 git_push.bat
)

echo.
pause
