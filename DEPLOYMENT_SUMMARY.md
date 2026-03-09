# 部署总结 - 快速参考

## 📋 已完成的配置

### ✅ 前端配置
- **API地址已更新**: `http://101.37.24.171:8000`
- **文件位置**: `fronted/utils/request.js`
- **H5已打包**: 使用HBuilderX打包完成

### ✅ 后端配置
- **CORS已配置**: 允许所有来源访问
- **端口**: 8000
- **文件位置**: `backend/app/main.py`

### ✅ 文档已创建
- `README.md` - 项目说明（已更新服务器地址）
- `GITHUB_DEPLOYMENT_GUIDE.md` - 完整部署指南
- `push_to_github.bat` - Windows推送脚本
- `push_to_github.sh` - Linux/Mac推送脚本

## 🚀 推送到GitHub步骤

### 方法1：使用脚本（推荐）

**Windows:**
```bash
push_to_github.bat
```

**Linux/Mac:**
```bash
chmod +x push_to_github.sh
./push_to_github.sh
```

### 方法2：手动推送

```bash
# 1. 初始化Git（如果还没有）
git init

# 2. 添加所有文件
git add .

# 3. 提交
git commit -m "Initial commit: Campus Sports System v1.0"

# 4. 添加远程仓库（替换YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/campus-sports-system.git

# 5. 推送
git branch -M main
git push -u origin main
```

## 🌐 服务器部署步骤

### 1. 连接服务器
```bash
ssh root@101.37.24.171
```

### 2. 克隆项目
```bash
cd /var/www
git clone https://github.com/YOUR_USERNAME/campus-sports-system.git
cd campus-sports-system
```

### 3. 部署后端
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python create_admin.py
python create_test_data.py
```

### 4. 配置systemd服务
```bash
sudo nano /etc/systemd/system/campus-backend.service
```

粘贴配置（见 GITHUB_DEPLOYMENT_GUIDE.md）

```bash
sudo systemctl daemon-reload
sudo systemctl enable campus-backend
sudo systemctl start campus-backend
```

### 5. 上传H5文件
```bash
# 在本地执行
scp -r fronted/unpackage/dist/build/h5/* root@101.37.24.171:/var/www/campus-sports-system/fronted/dist/
```

### 6. 配置Nginx
```bash
sudo nano /etc/nginx/sites-available/campus-sports
```

粘贴配置（见 GITHUB_DEPLOYMENT_GUIDE.md）

```bash
sudo ln -s /etc/nginx/sites-available/campus-sports /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. 配置防火墙
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw enable
```

## 🔍 验证部署

### 检查后端
```bash
# 查看服务状态
sudo systemctl status campus-backend

# 查看日志
sudo journalctl -u campus-backend -f

# 测试API
curl http://101.37.24.171:8000/docs
```

### 检查前端
```bash
# 访问H5
http://101.37.24.171

# 检查Nginx
sudo systemctl status nginx
sudo nginx -t
```

## 📱 访问地址

- **前端H5**: http://101.37.24.171
- **API文档**: http://101.37.24.171:8000/docs
- **后端API**: http://101.37.24.171:8000

## 🔑 测试账号

| 角色 | 账号 | 密码 |
|------|------|------|
| 学生 | 13800138000 | 123456 |
| 教师 | 13900139000 | 123456 |
| 管理员 | admin | admin123 |

## 📊 项目统计

- **代码行数**: ~15,000+
- **文件数量**: ~44个（清理后）
- **功能模块**: 8个主要模块
- **支持平台**: H5、微信小程序、APP

## 🎯 下一步

1. ✅ 推送代码到GitHub
2. ⏳ 部署到服务器 (101.37.24.171)
3. ⏳ 配置域名（可选）
4. ⏳ 配置HTTPS（可选）
5. ⏳ 性能优化
6. ⏳ 监控和日志

## 📞 技术支持

如遇问题，请查看：
- [完整部署指南](./GITHUB_DEPLOYMENT_GUIDE.md)
- [系统功能指南](./SYSTEM_FEATURES_GUIDE.md)
- [API文档](./backend/API_DOCUMENTATION.md)

---

**准备就绪！现在可以推送到GitHub并部署到服务器了。**
