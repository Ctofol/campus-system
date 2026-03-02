# 项目清理和上传检查清单

## ✅ 已完成的清理

### 1. .gitignore 优化
- ✅ 添加了数据库文件忽略（*.db, *.sqlite）
- ✅ 添加了日志文件忽略
- ✅ 添加了环境变量文件忽略
- ✅ 添加了临时文件忽略
- ✅ 添加了.kiro目录忽略

### 2. 文档整理
- ✅ 更新了主README.md
- ✅ 保留了所有修复文档（作为开发记录）
- ✅ 保留了API文档

### 3. 代码检查
- ✅ 所有功能代码已更新
- ✅ 权限配置已完善
- ✅ 错误处理已优化

## 📋 上传前检查清单

### 必须检查的项目

- [ ] **敏感信息检查**
  - [ ] 数据库密码（backend/app/database.py）
  - [ ] API密钥（manifest.json中的地图key）
  - [ ] 小程序AppID（如果是私有的）
  
- [ ] **文件大小检查**
  - [ ] backend/uploads/ 目录（应该被.gitignore忽略）
  - [ ] backend/campus_sports.db（应该被忽略）
  - [ ] fronted/unpackage/ 目录（应该被忽略）
  
- [ ] **依赖文件检查**
  - [ ] backend/requirements.txt 是否完整
  - [ ] fronted/package.json 是否存在（如果有）

### 可选检查项目

- [ ] 删除测试脚本
  - [ ] backend/create_test_user.py
  - [ ] backend/list_users.py
  - [ ] backend/clean_global_tasks.py
  - [ ] backend/delete_global_tasks_auto.py
  
- [ ] 删除临时文档
  - [ ] WECHAT_CONSOLE_TEST.js
  - [ ] 各种修复文档（或移到docs目录）

## 🔒 敏感信息处理

### 需要修改的文件

#### 1. backend/app/database.py
```python
# 修改前
DATABASE_URL = "postgresql://postgres:Chen20070509@localhost:5432/campus_db"

# 修改后（使用环境变量）
import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./campus_sports.db")
```

#### 2. fronted/manifest.json
```json
// 如果地图key是私有的，可以考虑：
"sdkConfigs": {
  "maps": {
    "tencent": {
      "key": "YOUR_KEY_HERE"  // 提示用户替换
    }
  }
}
```

#### 3. fronted/utils/request.js
```javascript
// 确保默认使用localhost
let baseUrl = 'http://127.0.0.1:8000';
```

## 📦 推荐的文件结构

### 保留的文件
```
✅ 源代码文件（.py, .vue, .js）
✅ 配置文件（manifest.json, pages.json, requirements.txt）
✅ 文档文件（README.md, API_DOCUMENTATION.md）
✅ Docker配置（docker-compose.yml, Dockerfile）
✅ Git配置（.gitignore）
```

### 忽略的文件
```
❌ 数据库文件（*.db）
❌ 虚拟环境（.venv/）
❌ 编译输出（unpackage/）
❌ 上传文件（uploads/*）
❌ IDE配置（.idea/, .vscode/）
❌ 缓存文件（__pycache__/）
```

## 🚀 Git 操作步骤

### 1. 初始化Git（如果还没有）
```bash
git init
```

### 2. 添加远程仓库
```bash
git remote add origin git@github.com:Ctofol/campus-system.git
```

### 3. 检查状态
```bash
git status
```

### 4. 添加文件
```bash
git add .
```

### 5. 提交
```bash
git commit -m "Initial commit: Campus Sports Health System"
```

### 6. 推送
```bash
# 首次推送
git push -u origin master

# 或者如果远程已有内容
git push -u origin master --force
```

## 📝 推荐的提交信息

### 首次提交
```
Initial commit: Campus Sports Health System

Features:
- Student running tracking with GPS
- Physical fitness testing with AI scoring
- Online course learning system
- Running group activities
- Teacher management dashboard
- Admin user management

Tech Stack:
- Frontend: Uni-app (Vue 3)
- Backend: FastAPI (Python)
- Database: PostgreSQL/SQLite
```

### 后续提交
```
Update: [功能名称]
Fix: [修复的问题]
Docs: [文档更新]
Refactor: [代码重构]
```

## ⚠️ 注意事项

1. **不要上传敏感信息**
   - 数据库密码
   - API密钥
   - 用户数据

2. **不要上传大文件**
   - 数据库文件
   - 上传的视频/图片
   - 编译输出

3. **检查.gitignore**
   - 确保所有不需要的文件都被忽略
   - 可以用 `git status` 检查

4. **测试克隆**
   - 推送后，在另一个目录克隆测试
   - 确保项目可以正常运行

## 🔧 快速清理命令

### Windows
```batch
# 删除Python缓存
for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"

# 删除数据库文件
del /s *.db

# 删除编译输出
rd /s /q fronted\unpackage
```

### Linux/Mac
```bash
# 删除Python缓存
find . -type d -name "__pycache__" -exec rm -rf {} +

# 删除数据库文件
find . -name "*.db" -delete

# 删除编译输出
rm -rf fronted/unpackage
```

## ✅ 最终检查

推送前最后确认：
- [ ] 所有敏感信息已移除或替换
- [ ] .gitignore 配置正确
- [ ] README.md 完整且准确
- [ ] 代码可以正常运行
- [ ] 没有包含大文件
- [ ] 提交信息清晰明确
