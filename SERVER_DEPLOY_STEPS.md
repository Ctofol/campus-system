# 服务器快速部署步骤

## 🚀 5分钟快速部署

### 前提条件
- 已连接到阿里云服务器（Ubuntu 22.04）
- 服务器IP: 172.27.207.64
- 已安装Docker和Docker Compose

---

## 步骤1: 克隆项目到服务器

```bash
# 方法A: 使用Git克隆（推荐）
cd ~
git clone https://github.com/Ctofol/campus-system.git
cd campus-system
```

或

```bash
# 方法B: 从本地上传
# 在本地Windows PowerShell运行:
scp -r D:\PC\Document\HBuilderProjects\campus-system root@172.27.207.64:~/

# 然后在服务器上:
cd ~/campus-system
```

---

## 步骤2: 配置环境变量

```bash
# 复制环境变量模板
cp .env.production .env

# 编辑配置文件
nano .env
```

修改以下内容（重要！）:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_strong_password_here  # 改成强密码
POSTGRES_DB=campus_db
```

保存并退出（Ctrl+X, 然后Y, 然后Enter）

---

## 步骤3: 运行部署脚本

```bash
# 给脚本执行权限
chmod +x deploy.sh

# 运行部署脚本
bash deploy.sh
```

脚本会自动完成：
- ✅ 检查Docker环境
- ✅ 构建镜像
- ✅ 启动服务
- ✅ 测试连接

---

## 步骤4: 初始化数据库

```bash
# 创建管理员账号
docker compose exec backend python create_admin.py

# 创建测试用户（可选）
docker compose exec backend python create_test_user.py
```

---

## 步骤5: 验证部署

```bash
# 检查服务状态
docker compose ps

# 应该看到两个容器都在运行:
# campus-backend    Up
# campus-db         Up

# 测试API
curl http://localhost:8000/

# 查看API文档（在浏览器访问）
# http://172.27.207.64:8000/docs
```

---

## 🔧 配置防火墙（重要！）

```bash
# 开放后端API端口
sudo ufw allow 8000/tcp

# 如果使用Nginx反向代理
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 重新加载防火墙
sudo ufw reload

# 查看防火墙状态
sudo ufw status
```

---

## 🌐 配置Nginx反向代理（可选但推荐）

### 1. 安装Nginx

```bash
sudo apt update
sudo apt install -y nginx
```

### 2. 创建配置文件

```bash
sudo nano /etc/nginx/sites-available/campus-system
```

粘贴以下内容:

```nginx
server {
    listen 80;
    server_name 172.27.207.64;  # 或你的域名

    # 后端API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 增加超时时间（用于文件上传）
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }

    # 直接访问根路径也转发到API
    location / {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 上传文件访问
    location /uploads/ {
        alias /root/campus-system/backend/uploads/;
        autoindex off;
    }

    # 增加上传文件大小限制
    client_max_body_size 100M;
}
```

### 3. 启用配置

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/campus-system /etc/nginx/sites-enabled/

# 删除默认配置（可选）
sudo rm /etc/nginx/sites-enabled/default

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 4. 测试Nginx

```bash
# 测试API（通过Nginx）
curl http://172.27.207.64/

# 在浏览器访问
# http://172.27.207.64/docs
```

---

## 📱 前端配置

### 修改前端API地址

前端需要修改API基础URL为服务器地址：

在 `fronted/main.js` 或相关配置文件中:

```javascript
// 开发环境
// const API_BASE_URL = 'http://localhost:8000'

// 生产环境（使用Nginx）
const API_BASE_URL = 'http://172.27.207.64/api'

// 或使用域名
// const API_BASE_URL = 'https://your-domain.com/api'
```

---

## 🔍 常用管理命令

### 查看日志

```bash
# 查看后端日志
docker compose logs backend

# 实时查看日志
docker compose logs -f backend

# 查看最近100行
docker compose logs --tail=100 backend
```

### 重启服务

```bash
# 重启所有服务
docker compose restart

# 仅重启后端
docker compose restart backend
```

### 停止服务

```bash
# 停止服务
docker compose stop

# 停止并删除容器
docker compose down
```

### 更新代码

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker compose up -d --build backend
```

### 进入容器

```bash
# 进入后端容器
docker compose exec backend bash

# 进入数据库容器
docker compose exec db bash

# 在容器内执行命令
docker compose exec backend python create_admin.py
```

---

## 💾 数据库管理

### 备份数据库

```bash
# 创建备份目录
mkdir -p ~/backups

# 备份数据库
docker compose exec db pg_dump -U postgres campus_db > ~/backups/campus_db_$(date +%Y%m%d_%H%M%S).sql

# 查看备份文件
ls -lh ~/backups/
```

### 恢复数据库

```bash
# 恢复数据库
docker compose exec -T db psql -U postgres campus_db < ~/backups/campus_db_20260302_120000.sql
```

### 设置自动备份

```bash
# 编辑定时任务
crontab -e

# 添加每天凌晨2点备份
0 2 * * * cd ~/campus-system && docker compose exec db pg_dump -U postgres campus_db > ~/backups/campus_db_$(date +\%Y\%m\%d).sql

# 添加清理30天前的备份
0 3 * * * find ~/backups -name "campus_db_*.sql" -mtime +30 -delete
```

---

## 🔐 安全建议

1. **修改数据库密码**: 在 `.env` 中使用强密码
2. **限制数据库端口**: 不要暴露5432端口到公网
3. **使用HTTPS**: 配置SSL证书（Let's Encrypt）
4. **定期备份**: 设置自动备份脚本
5. **更新系统**: 定期运行 `sudo apt update && sudo apt upgrade`
6. **监控日志**: 定期检查应用日志

---

## 🐛 故障排查

### 问题1: 容器无法启动

```bash
# 查看详细日志
docker compose logs backend

# 检查端口占用
sudo lsof -i :8000

# 重新构建
docker compose build --no-cache backend
docker compose up -d backend
```

### 问题2: 数据库连接失败

```bash
# 检查数据库状态
docker compose ps db

# 查看数据库日志
docker compose logs db

# 重启数据库
docker compose restart db
```

### 问题3: API无法访问

```bash
# 检查防火墙
sudo ufw status

# 检查Nginx状态
sudo systemctl status nginx

# 测试本地连接
curl http://localhost:8000/

# 查看Nginx日志
sudo tail -f /var/log/nginx/error.log
```

### 问题4: 磁盘空间不足

```bash
# 查看磁盘使用
df -h

# 清理Docker
docker system prune -a

# 清理日志
sudo journalctl --vacuum-time=7d
```

---

## ✅ 部署检查清单

完成以下检查确保部署成功:

- [ ] Docker和Docker Compose已安装
- [ ] 项目代码已克隆到服务器
- [ ] .env文件已配置（数据库密码已修改）
- [ ] 部署脚本运行成功
- [ ] 容器状态正常（docker compose ps）
- [ ] API可以访问（curl http://localhost:8000/）
- [ ] 数据库已初始化（创建管理员账号）
- [ ] 防火墙已配置（开放8000端口）
- [ ] Nginx已配置（可选）
- [ ] 自动备份已设置（可选）

---

## 📞 获取帮助

如果遇到问题:

1. 查看详细文档: `DOCKER_DEPLOY_GUIDE.md`
2. 查看日志: `docker compose logs -f`
3. 提交Issue: https://github.com/Ctofol/campus-system/issues

---

## 🎯 部署成功后

你的API将在以下地址可用:

- **直接访问**: http://172.27.207.64:8000/docs
- **通过Nginx**: http://172.27.207.64/docs

测试账号:
- 学生: 13800138000 / 123456
- 教师: 13800138001 / 123456

**祝部署顺利！** 🚀
