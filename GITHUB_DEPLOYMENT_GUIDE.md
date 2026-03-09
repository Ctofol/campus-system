# GitHub部署指南

## 服务器信息
- **公网IP**: 101.37.24.171
- **后端端口**: 8000
- **前端**: H5已打包

## 一、准备GitHub仓库

### 1. 创建GitHub仓库
1. 登录 GitHub
2. 点击右上角 "+" → "New repository"
3. 仓库名称：`campus-sports-system`
4. 描述：`校园运动健康系统 - Campus Sports Health System`
5. 选择 Public 或 Private
6. 不要勾选 "Initialize this repository with a README"
7. 点击 "Create repository"

### 2. 本地初始化Git（如果还没有）
```bash
cd D:\PC\Document\HBuilderProjects\campus-system
git init
git add .
git commit -m "Initial commit: Campus Sports Health System"
```

### 3. 关联远程仓库
```bash
# 替换 YOUR_USERNAME 为你的GitHub用户名
git remote add origin https://github.com/YOUR_USERNAME/campus-sports-system.git
git branch -M main
git push -u origin main
```

## 二、服务器部署步骤

### 1. 连接服务器
```bash
ssh root@101.37.24.171
```

### 2. 安装必要软件
```bash
# 更新系统
apt update && apt upgrade -y

# 安装Python 3.10+
apt install python3 python3-pip python3-venv -y

# 安装Git
apt install git -y

# 安装Nginx
apt install nginx -y

# 安装Node.js（如果需要）
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install nodejs -y
```

### 3. 克隆项目
```bash
cd /var/www
git clone https://github.com/YOUR_USERNAME/campus-sports-system.git
cd campus-sports-system
```

### 4. 部署后端

#### 创建虚拟环境
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

#### 安装依赖
```bash
pip install -r requirements.txt
```

#### 创建必要目录
```bash
mkdir -p uploads
```

#### 创建systemd服务
```bash
nano /etc/systemd/system/campus-backend.service
```

内容：
```ini
[Unit]
Description=Campus Sports Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/campus-sports-system/backend
Environment="PATH=/var/www/campus-sports-system/backend/venv/bin"
ExecStart=/var/www/campus-sports-system/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 启动后端服务
```bash
systemctl daemon-reload
systemctl enable campus-backend
systemctl start campus-backend
systemctl status campus-backend
```

### 5. 部署前端（H5）

#### 上传H5打包文件
将HBuilderX打包的H5文件上传到服务器：
```bash
# 在本地
scp -r fronted/unpackage/dist/build/h5/* root@101.37.24.171:/var/www/campus-sports-system/fronted/dist/
```

#### 配置Nginx
```bash
nano /etc/nginx/sites-available/campus-sports
```

内容：
```nginx
server {
    listen 80;
    server_name 101.37.24.171;

    # 前端H5
    location / {
        root /var/www/campus-sports-system/fronted/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 后端直接访问（用于开发）
    location /auth/ {
        proxy_pass http://127.0.0.1:8000/auth/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /common/ {
        proxy_pass http://127.0.0.1:8000/common/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /activity/ {
        proxy_pass http://127.0.0.1:8000/activity/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /teacher/ {
        proxy_pass http://127.0.0.1:8000/teacher/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /student/ {
        proxy_pass http://127.0.0.1:8000/student/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /courses/ {
        proxy_pass http://127.0.0.1:8000/courses/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /run-group/ {
        proxy_pass http://127.0.0.1:8000/run-group/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /upload/ {
        proxy_pass http://127.0.0.1:8000/upload/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        client_max_body_size 100M;
    }

    location /uploads/ {
        alias /var/www/campus-sports-system/backend/uploads/;
    }
}
```

#### 启用站点
```bash
ln -s /etc/nginx/sites-available/campus-sports /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### 6. 配置防火墙
```bash
# 允许HTTP和HTTPS
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp
ufw enable
```

### 7. 初始化数据库
```bash
cd /var/www/campus-sports-system/backend
source venv/bin/activate

# 创建管理员
python create_admin.py

# 创建测试教师
python create_teacher.py

# 创建测试数据
python create_test_data.py
```

## 三、访问系统

### 前端H5
```
http://101.37.24.171
```

### 后端API文档
```
http://101.37.24.171:8000/docs
```

### 测试账号
- 学生：13800138000 / 123456
- 教师：13900139000 / 123456
- 管理员：admin / admin123

## 四、更新部署

### 更新代码
```bash
cd /var/www/campus-sports-system
git pull origin main
```

### 重启后端
```bash
systemctl restart campus-backend
```

### 更新前端
```bash
# 在本地重新打包后上传
scp -r fronted/unpackage/dist/build/h5/* root@101.37.24.171:/var/www/campus-sports-system/fronted/dist/
```

## 五、监控和日志

### 查看后端日志
```bash
journalctl -u campus-backend -f
```

### 查看Nginx日志
```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 查看服务状态
```bash
systemctl status campus-backend
systemctl status nginx
```

## 六、故障排查

### 后端无法启动
```bash
# 检查端口占用
netstat -tulpn | grep 8000

# 检查Python环境
source venv/bin/activate
python -c "import fastapi; print(fastapi.__version__)"

# 手动启动测试
cd /var/www/campus-sports-system/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 前端无法访问
```bash
# 检查Nginx配置
nginx -t

# 检查文件权限
ls -la /var/www/campus-sports-system/fronted/dist/

# 重启Nginx
systemctl restart nginx
```

### 数据库问题
```bash
# 备份数据库
cp backend/campus_sports.db backend/campus_sports.db.backup

# 重置数据库（谨慎！）
rm backend/campus_sports.db
python create_admin.py
python create_test_data.py
```

## 七、安全建议

1. **修改默认密码**：部署后立即修改所有测试账号密码
2. **配置HTTPS**：使用Let's Encrypt配置SSL证书
3. **限制访问**：配置防火墙规则，只开放必要端口
4. **定期备份**：设置定时任务备份数据库
5. **更新系统**：定期更新系统和依赖包

## 八、备份脚本

创建自动备份脚本：
```bash
nano /root/backup_campus.sh
```

内容：
```bash
#!/bin/bash
BACKUP_DIR="/root/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
cp /var/www/campus-sports-system/backend/campus_sports.db \
   $BACKUP_DIR/campus_sports_$DATE.db

# 备份上传文件
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz \
   /var/www/campus-sports-system/backend/uploads/

# 删除7天前的备份
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

设置定时任务：
```bash
chmod +x /root/backup_campus.sh
crontab -e
```

添加：
```
0 2 * * * /root/backup_campus.sh >> /var/log/campus_backup.log 2>&1
```

---

**部署完成！系统现在可以通过 http://101.37.24.171 访问。**
