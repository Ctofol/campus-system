#!/bin/bash

# 校园运动健康系统 - Docker 快速部署脚本
# 使用方法: bash deploy.sh

set -e

echo "========================================="
echo "  校园运动健康系统 - Docker 部署"
echo "========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}提示: 建议使用 sudo 运行此脚本${NC}"
    echo "继续执行可能需要输入密码..."
    echo ""
fi

# 1. 检查Docker是否安装
echo "📋 [1/8] 检查Docker环境..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装${NC}"
    echo "请先安装Docker: https://docs.docker.com/engine/install/"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose 未安装${NC}"
    echo "请先安装Docker Compose"
    exit 1
fi

echo -e "${GREEN}✅ Docker 环境正常${NC}"
docker --version
docker compose version
echo ""

# 2. 检查环境变量文件
echo "📋 [2/8] 检查环境配置..."
if [ ! -f .env ]; then
    if [ -f .env.production ]; then
        echo "复制 .env.production 到 .env"
        cp .env.production .env
        echo -e "${YELLOW}⚠️  请编辑 .env 文件，修改数据库密码等配置${NC}"
        echo "运行: nano .env"
        read -p "按回车继续..."
    else
        echo -e "${RED}❌ 未找到 .env 或 .env.production 文件${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✅ 环境配置文件存在${NC}"
echo ""

# 3. 检查必要的目录
echo "📋 [3/8] 创建必要的目录..."
mkdir -p backend/uploads
mkdir -p backups
echo -e "${GREEN}✅ 目录创建完成${NC}"
echo ""

# 4. 停止旧容器（如果存在）
echo "📋 [4/8] 停止旧容器..."
if docker compose ps | grep -q "Up"; then
    echo "发现运行中的容器，正在停止..."
    docker compose down
    echo -e "${GREEN}✅ 旧容器已停止${NC}"
else
    echo "没有运行中的容器"
fi
echo ""

# 5. 构建镜像
echo "📋 [5/8] 构建Docker镜像..."
echo "这可能需要几分钟时间..."
docker compose build backend
echo -e "${GREEN}✅ 镜像构建完成${NC}"
echo ""

# 6. 启动服务
echo "📋 [6/8] 启动服务..."
docker compose up -d backend db
echo -e "${GREEN}✅ 服务启动完成${NC}"
echo ""

# 7. 等待服务就绪
echo "📋 [7/8] 等待服务就绪..."
echo "等待数据库启动..."
sleep 10

# 检查容器状态
if docker compose ps | grep -q "campus-backend.*Up"; then
    echo -e "${GREEN}✅ 后端服务运行中${NC}"
else
    echo -e "${RED}❌ 后端服务启动失败${NC}"
    echo "查看日志: docker compose logs backend"
    exit 1
fi

if docker compose ps | grep -q "campus-db.*Up"; then
    echo -e "${GREEN}✅ 数据库服务运行中${NC}"
else
    echo -e "${RED}❌ 数据库服务启动失败${NC}"
    echo "查看日志: docker compose logs db"
    exit 1
fi
echo ""

# 8. 测试API
echo "📋 [8/8] 测试API连接..."
sleep 5
if curl -s http://localhost:8000/ > /dev/null; then
    echo -e "${GREEN}✅ API 连接成功${NC}"
else
    echo -e "${YELLOW}⚠️  API 暂时无法访问，可能还在启动中${NC}"
    echo "请稍后访问: http://localhost:8000/docs"
fi
echo ""

# 显示部署信息
echo "========================================="
echo -e "${GREEN}🎉 部署完成！${NC}"
echo "========================================="
echo ""
echo "📊 服务状态:"
docker compose ps
echo ""
echo "🌐 访问地址:"
echo "  - API文档: http://localhost:8000/docs"
echo "  - API接口: http://localhost:8000/"
echo ""
echo "📝 常用命令:"
echo "  - 查看日志: docker compose logs -f backend"
echo "  - 停止服务: docker compose stop"
echo "  - 重启服务: docker compose restart"
echo "  - 进入容器: docker compose exec backend bash"
echo ""
echo "🔧 初始化数据库:"
echo "  docker compose exec backend python create_admin.py"
echo "  docker compose exec backend python create_test_user.py"
echo ""
echo "📖 详细文档: 查看 DOCKER_DEPLOY_GUIDE.md"
echo ""
echo -e "${GREEN}部署成功！${NC}"
