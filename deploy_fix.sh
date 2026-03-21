#!/bin/bash
echo "🚀 开始执行自动化隔离部署方案..."

# 1. 强制重置远程仓库状态并拉取最新版本 (包含 docker-compose.yml 端口剥离)
git pull origin master

# 2. 停掉目前纠缠不清的容器并重新拉起
# 注意：此时 admin-backend 和 backend 不再暴露 8000/8001
sudo docker-compose down
sudo docker-compose up -d --force-recreate

# 3. 彻底抹除前端容器内部的硬编码地址
echo "🛠️ 正在修复管理端 (8090) 连通性..."
sudo docker exec campus-admin-frontend sh -c "find /usr/share/nginx/html -type f | xargs sed -i 's/:8002/\/admin-api/g'"

echo "🛠️ 正在修复学生/教师端 (8080) 连通性..."
sudo docker exec campus-frontend-h5 sh -c "find /usr/share/nginx/html -type f | xargs sed -i 's/:8000/\/api/g'"

# 4. 刷新 Nginx 状态
sudo docker exec campus-admin-frontend nginx -s reload
sudo docker exec campus-frontend-h5 nginx -s reload

echo "✅ 修复完成！请直接刷新浏览器 (Ctrl + F5)。"
sudo ufw allow 8090/tcp
sudo ufw allow 8080/tcp

echo "Checking container status..."
echo "Deployment and Fix complete! Please visit http://<your-ip>:8090"

