# Docker 部署指南

## 📋 部署前准备

### 1. 服务器要求

- 操作系统: Ubuntu 22.04 LTS（推荐）或其他Linux发行版
- 内存: 至少 2GB RAM
- 磁盘: 至少 20GB 可用空间
- 已安装: Docker 和 Docker Compose

### 2. 安装 Docker（如果未安装）

```bash
# 更新包索引
sudo apt update

# 安装必要的包
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# 添加 Docker 官方 GPG 密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加 Docker 仓库
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
docker compose version
```

### 3. 配置 Docker 权限（可选）

```bash
# 将当前用户添加到 docker 组
sudo usermod -aG docker $USER

# 重新登录或运行
newgrp docker

# 测试
docker ps
```

## 🚀 快速部署步骤

### 方法1：从GitHub克隆（推荐）

```bash
# 1. 克隆项目
git clone git@github.com:Ctofol/campus-system.git
cd campus-system

# 2. 配置环境变量
cp .env.production .env
nano .env  # 修改数据库密码等配置

# 3. 启动服务（仅后端+数据库）
docker compose up -d backend db

# 4. 查看日志
docker compose logs -f backend

# 5. 检查服务状态
docker compose ps
```

### 方法2：手动上传文件

```bash
# 1. 在本地打包项目（排除不必要的文件）
# 在本地Windows上运行：
tar -czf campus-system.tar.gz --exclude=backend/.venv --exclude=backend/__pycache__ --exclude=backend/uploads --exclude=backend/*.db --exclude=fronted/unpackage --exclude=fronted/node_modules --exclude=.git backend/ docker-compose.yml .env.production

# 2. 上传到服务器
scp campus-system.tar.gz root@your_server_ip:/root/

# 3. 在服务器上解压
ssh root@your_server_ip
cd /root
tar -xzf campus-system.tar.gz
cd campus-system

# 4. 配置环境变量
cp .env.production .env
nano .env

# 5. 启动服务
docker compose up -d backend db
```

## ⚙️ 配置说明

### 1. 环境变量配置 (.env)

```bash
# 编辑 .env 文件
nano .env
```

修改以下内容：

```env
# 数据库配置 - 请修改为强密码
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=campus_db

# 后端端口（默认8000）
BACKEND_PORT=8000

# 前端端口（如果部署H5，默认8080）
FRONTEND_PORT=8080
```

### 2. 端口说明

- `8000`: 后端API服务
- `5432`: PostgreSQL数据库（仅容器内部访问）
- `8080`: 前端H5服务（可选）

### 3. 防火墙配置

```bash
# 开放后端端口
sudo ufw allow 8000/tcp

# 如果部署前端H5
sudo ufw allow 8080/tcp

# 如果使用Nginx反向代理
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 重新加载防火墙
sudo ufw reload
```

## 🔧 Docker Compose 命令

### 启动服务

```bash
# 启动所有服务
docker compose up -d

# 仅启动后端和数据库
docker compose up -d backend db

# 查看启动日志
docker compose logs -f
```

### 停止服务

```bash
# 停止所有服务
docker compose stop

# 停止并删除容器
docker compose down

# 停止并删除容器和数据卷（⚠️ 会删除数据库数据）
docker compose down -v
```

### 查看状态

```bash
# 查看运行中的容器
docker compose ps

# 查看日志
docker compose logs backend
docker compose logs db

# 实时查看日志
docker compose logs -f backend
```

### 重启服务

```bash
# 重启所有服务
docker compose restart

# 仅重启后端
docker compose restart backend
```

### 更新服务

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker compose up -d --build
```

## 📊 数据库管理

### 初始化数据库

```bash
# 进入后端容器
docker compose exec backend bash

# 创建管理员账号
python create_admin.py

# 创建测试用户
python create_test_user.py

# 退出容器
exit
```

### 数据库备份

```bash
# 备份数据库
docker compose exec db pg_dump -U postgres campus_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复数据库
docker compose exec -T db psql -U postgres campus_db < backup_20260302_120000.sql
```

### 访问数据库

```bash
# 进入数据库容器
docker compose exec db psql -U postgres -d campus_db

# 查看表
\dt

# 退出
\q
```

## 🌐 Nginx 反向代理（推荐）

### 1. 安装 Nginx

```bash
sudo apt update
sudo apt install -y nginx
```

### 2. 配置反向代理

创建配置文件：

```bash
sudo nano /etc/nginx/sites-available/campus-system
```

添加以下内容：

```nginx
server {
    listen 80;
    server_name your_domain.com;  # 修改为你的域名或IP

    # 后端API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 前端H5（如果部署）
    location / {
        proxy_pass http://localhost:8080/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 上传文件访问
    location /uploads/ {
        alias /root/campus-system/backend/uploads/;
        autoindex off;
    }
}
```

### 3. 启用配置

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/campus-system /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

### 4. 配置HTTPS（可选，使用Let's Encrypt）

```bash
# 安装Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your_domain.com

# 自动续期
sudo certbot renew --dry-run
```

## 🔍 故障排查

### 1. 查看容器日志

```bash
# 后端日志
docker compose logs backend

# 数据库日志
docker compose logs db

# 实时日志
docker compose logs -f
```

### 2. 进入容器调试

```bash
# 进入后端容器
docker compose exec backend bash

# 进入数据库容器
docker compose exec db bash
```

### 3. 检查网络连接

```bash
# 检查容器网络
docker network ls
docker network inspect campus-system_campus-network

# 测试后端连接
curl http://localhost:8000/docs
```

### 4. 常见问题

#### 问题1: 端口被占用

```bash
# 查看端口占用
sudo lsof -i :8000
sudo lsof -i :5432

# 停止占用端口的进程
sudo kill -9 <PID>
```

#### 问题2: 数据库连接失败

```bash
# 检查数据库容器状态
docker compose ps db

# 查看数据库日志
docker compose logs db

# 重启数据库
docker compose restart db
```

#### 问题3: 容器启动失败

```bash
# 查看详细错误
docker compose logs backend

# 重新构建
docker compose build --no-cache backend
docker compose up -d backend
```

#### 问题4: 磁盘空间不足

```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的容器
docker container prune

# 清理未使用的卷
docker volume prune
```

## 📈 性能优化

### 1. 限制容器资源

修改 `docker-compose.yml`：

```yaml
services:
  backend:
    # ... 其他配置
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 2. 使用生产级WSGI服务器

修改 `backend/Dockerfile`：

```dockerfile
# 安装gunicorn
RUN pip install gunicorn

# 使用gunicorn启动
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### 3. 配置日志轮转

```bash
# 限制Docker日志大小
sudo nano /etc/docker/daemon.json
```

添加：

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

重启Docker：

```bash
sudo systemctl restart docker
```

## 🔐 安全建议

1. **修改默认密码**: 务必修改 `.env` 中的数据库密码
2. **限制数据库访问**: 不要暴露5432端口到公网
3. **使用HTTPS**: 配置SSL证书
4. **定期备份**: 设置自动备份脚本
5. **更新系统**: 定期更新系统和Docker镜像
6. **防火墙**: 只开放必要的端口

## 📝 监控和日志

### 1. 设置日志收集

```bash
# 创建日志目录
mkdir -p /var/log/campus-system

# 收集日志
docker compose logs > /var/log/campus-system/app.log
```

### 2. 设置定时任务

```bash
# 编辑crontab
crontab -e

# 添加每天备份任务
0 2 * * * cd /root/campus-system && docker compose exec db pg_dump -U postgres campus_db > /root/backups/campus_db_$(date +\%Y\%m\%d).sql

# 添加日志清理任务
0 3 * * * find /var/log/campus-system -name "*.log" -mtime +7 -delete
```

## 🎯 验证部署

### 1. 检查服务状态

```bash
# 查看容器状态
docker compose ps

# 应该看到：
# campus-backend    running
# campus-db         running
```

### 2. 测试API

```bash
# 测试健康检查
curl http://localhost:8000/

# 访问API文档
curl http://localhost:8000/docs

# 或在浏览器访问
# http://your_server_ip:8000/docs
```

### 3. 测试数据库连接

```bash
docker compose exec backend python -c "from app.database import engine; print('Database connected!' if engine else 'Failed')"
```

## 📞 获取帮助

如果遇到问题：

1. 查看日志: `docker compose logs -f`
2. 检查配置: `docker compose config`
3. 查看文档: `README.md`
4. 提交Issue: https://github.com/Ctofol/campus-system/issues

## ✅ 部署完成检查清单

- [ ] Docker和Docker Compose已安装
- [ ] 项目文件已上传到服务器
- [ ] .env文件已配置（数据库密码已修改）
- [ ] 容器已成功启动（docker compose ps）
- [ ] 后端API可访问（http://server_ip:8000/docs）
- [ ] 数据库已初始化（创建管理员账号）
- [ ] 防火墙已配置
- [ ] Nginx反向代理已配置（可选）
- [ ] SSL证书已配置（可选）
- [ ] 备份脚本已设置

---

**部署成功后，你的API将在以下地址可用:**
- API文档: `http://your_server_ip:8000/docs`
- API接口: `http://your_server_ip:8000/api/...`

**祝部署顺利！** 🚀
