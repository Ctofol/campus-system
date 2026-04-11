#!/bin/bash

# --- Production Data Initialization Script ---

echo "🚀 Starting data initialization for Campus System..."

# 1. 确保容器正在运行
if [ "$(docker ps -q -f name=campus-backend)" ]; then
    echo "✅ Backend container is running. Proceeding..."
else
    echo "❌ Error: campus-backend container is NOT running. Build it first with 'docker-compose up -d'."
    exit 1
fi

# 2. 执行数据库迁移与种子填充
echo "📥 Running database seed (seed.py)..."
docker exec -it campus-backend python seed.py

# 3. 如果管理端也需要单独初始化 (如果有 init_admin.py)
# docker exec -it campus-admin-backend python init_admin.py

echo "🌟 Data initialization completed! Access your site at https://campus.gzyichenai.com"
