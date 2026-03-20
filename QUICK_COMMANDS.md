# 快速命令参考

## 🚀 GitHub推送

### Windows
```bash
push_to_github.bat
```

### Linux/Mac
```bash
chmod +x push_to_github.sh
./push_to_github.sh
```

### 手动推送
```bash
git add .
git commit -m "Update: Campus Sports System"
git push origin main
```

## 🖥️ 服务器操作

### 连接服务器
```bash
ssh root@101.37.24.171
```

### 更新代码
```bash
cd /var/www/campus-sports-system
git pull origin main
sudo systemctl restart campus-backend
```

### 查看日志
```bash
# 后端日志
sudo journalctl -u campus-backend -f

# Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 重启服务
```bash
# 重启后端
sudo systemctl restart campus-backend

# 重启Nginx
sudo systemctl restart nginx

# 查看状态
sudo systemctl status campus-backend
sudo systemctl status nginx
```

## 💻 本地开发

### 启动后端
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### 启动前端
```bash
# 使用HBuilderX运行
# 或命令行
cd fronted
npm run dev:h5
```

### 创建测试数据
```bash
cd backend
python create_admin.py
python create_teacher.py
python create_test_data.py
```

## 🔧 数据库操作

### 备份数据库
```bash
cp backend/campus_sports.db backend/campus_sports.db.backup
```

### 重置数据库
```bash
rm backend/campus_sports.db
python create_admin.py
python create_test_data.py
```

### 查看用户
```bash
python list_users.py
```

## 📦 部署相关

### 上传H5文件
```bash
scp -r fronted/unpackage/dist/build/h5/* root@101.37.24.171:/var/www/campus-sports-system/fronted/dist/
```

### 测试API
```bash
curl http://101.37.24.171:8000/docs
curl http://101.37.24.171:8000/common/captcha
```

### 检查端口
```bash
netstat -tulpn | grep 8000
```

## 🔍 故障排查

### 后端无法启动
```bash
# 检查日志
sudo journalctl -u campus-backend -n 50

# 手动启动测试
cd /var/www/campus-sports-system/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Nginx配置错误
```bash
# 测试配置
sudo nginx -t

# 查看错误日志
sudo tail -f /var/log/nginx/error.log
```

### 权限问题
```bash
# 修改文件权限
sudo chown -R www-data:www-data /var/www/campus-sports-system
sudo chmod -R 755 /var/www/campus-sports-system
```

## 📊 监控命令

### 系统资源
```bash
# CPU和内存
htop

# 磁盘空间
df -h

# 网络连接
netstat -tulpn
```

### 进程管理
```bash
# 查看Python进程
ps aux | grep python

# 查看Nginx进程
ps aux | grep nginx
```

## 🔐 安全相关

### 防火墙
```bash
# 查看规则
sudo ufw status

# 允许端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw allow 8080/tcp
sudo ufw allow 8090/tcp
```

### SSL证书（Let's Encrypt）
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## 📝 Git常用命令

### 查看状态
```bash
git status
git log --oneline -10
```

### 分支管理
```bash
git branch
git checkout -b feature/new-feature
git merge feature/new-feature
```

### 撤销更改
```bash
git checkout -- filename
git reset --hard HEAD
```

## 🎯 快速访问

- 前端: http://101.37.24.171
- API文档: http://101.37.24.171:8000/docs
- 服务器: ssh root@101.37.24.171

---

**保存此文件以便快速查找常用命令！**
