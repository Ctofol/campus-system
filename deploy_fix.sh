#!/bin/bash
# 校园系统管理端一键修复与重部署脚本
echo "Checking directory..."
PRJ_DIR="/var/www/campus-system"
if [ ! -d "$PRJ_DIR" ]; then
    PRJ_DIR="/var/www/campus-sports-system"
fi
cd "$PRJ_DIR" || exit

echo "Pulling latest changes from GitHub..."
git pull origin master

echo "Syncing Docker Compose services (admin-backend, admin-frontend)..."
# 使用 --build 确保前端 dist 和 Nginx 配置被更新到镜像中
docker-compose up -d --build admin-backend admin-frontend

echo "Ensuring Firewall ports (8090 for Admin, 8080 for Student)..."
sudo ufw allow 8090/tcp
sudo ufw allow 8080/tcp

echo "Checking container status..."
docker ps | grep campus-admin

echo "Deployment and Fix complete! Please visit http://<your-ip>:8090"

