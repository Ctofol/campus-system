#!/bin/bash

# 快速部署脚本
# 使用方法: bash quick_deploy.sh

echo "========================================="
echo "校园运动健康系统 - 快速部署"
echo "========================================="
echo ""

# 检查是否在正确的目录
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

echo "1. 拉取最新代码..."
git pull origin master

if [ $? -ne 0 ]; then
    echo "❌ Git拉取失败"
    exit 1
fi

echo "✅ 代码更新成功"
echo ""

echo "2. 停止所有容器..."
docker-compose down

echo ""

echo "3. 重新构建镜像..."
docker-compose build

if [ $? -ne 0 ]; then
    echo "❌ 构建失败"
    exit 1
fi

echo "✅ 构建成功"
echo ""

echo "4. 启动所有容器..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "❌ 启动失败"
    exit 1
fi

echo "✅ 启动成功"
echo ""

echo "5. 等待服务启动..."
sleep 5

echo ""
echo "6. 检查容器状态..."
docker-compose ps

echo ""
echo "========================================="
echo "部署完成！"
echo "========================================="
echo ""
echo "后端地址: http://120.26.17.147:8000"
echo "前端地址: http://120.26.17.147"
echo ""
echo "查看后端日志: docker-compose logs -f backend"
echo "查看前端日志: docker-compose logs -f fronted"
echo ""
echo "测试API: bash test_video_api.sh"
echo ""
