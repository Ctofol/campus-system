# GitHub 上传指南

## 📋 上传前准备

### 1. 已完成的清理工作 ✅

- ✅ 移除了数据库密码（改用环境变量）
- ✅ 优化了.gitignore配置
- ✅ 更新了README.md
- ✅ 创建了.env.example示例文件
- ✅ 添加了详细的项目文档

### 2. 当前项目状态

**仓库信息**:
- 仓库名: `campus-system`
- 用户名: `Ctofol`
- SSH地址: `git@github.com:Ctofol/campus-system.git`

**项目大小**: 约 50-100MB（不包含数据库和上传文件）

## 🚀 快速上传步骤

### 方法1：使用提供的脚本（推荐）

1. 双击运行 `git_push.bat`
2. 输入提交信息（或直接回车使用默认信息）
3. 确认推送（输入 y）

### 方法2：手动命令行操作

```bash
# 1. 检查Git状态
git status

# 2. 添加所有文件
git add .

# 3. 提交
git commit -m "Initial commit: Campus Sports Health System"

# 4. 添加远程仓库（如果还没有）
git remote add origin git@github.com:Ctofol/campus-system.git

# 5. 推送到GitHub
git push -u origin master
```

## ⚠️ 重要提示

### 如果远程仓库已有内容

如果GitHub上已经有README或其他文件，需要先拉取：

```bash
# 方法1：合并远程内容
git pull origin master --allow-unrelated-histories
git push -u origin master

# 方法2：强制推送（会覆盖远程内容）
git push -u origin master --force
```

### 如果遇到SSH密钥问题

1. 检查SSH密钥是否已添加到GitHub:
   ```bash
   ssh -T git@github.com
   ```

2. 如果没有SSH密钥，生成一个:
   ```bash
   ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
   ```

3. 将公钥添加到GitHub:
   - 复制 `~/.ssh/id_rsa.pub` 的内容
   - 在GitHub: Settings → SSH and GPG keys → New SSH key

### 如果使用HTTPS而不是SSH

```bash
# 使用HTTPS地址
git remote add origin https://github.com/Ctofol/campus-system.git
git push -u origin master
```

## 📝 推荐的提交信息

```
Initial commit: Campus Sports Health System

完整的校园运动健康管理系统，包含以下功能：

学生端:
- 跑步打卡（GPS轨迹、配速分析、步数统计）
- 体能测试（视频上传、AI评分）
- 在线课程学习
- 跑团活动

教师端:
- 数据看板和统计
- 任务管理
- 学生活动审批
- 课程管理

管理员端:
- 用户管理
- 班级管理
- 系统配置

技术栈:
- 前端: Uni-app (Vue 3)
- 后端: FastAPI (Python)
- 数据库: PostgreSQL/SQLite
- 地图: 腾讯地图API
```

## 🔍 上传后验证

### 1. 检查GitHub仓库

访问: https://github.com/Ctofol/campus-system

确认:
- [ ] 所有文件都已上传
- [ ] README.md 正确显示
- [ ] 没有敏感信息泄露
- [ ] .gitignore 正常工作

### 2. 测试克隆

在另一个目录测试克隆:

```bash
# 克隆仓库
git clone git@github.com:Ctofol/campus-system.git test-clone
cd test-clone

# 检查文件
ls -la

# 确认敏感文件没有被上传
# 应该看不到:
# - backend/campus_sports.db
# - backend/.venv/
# - backend/uploads/*.jpg, *.mp4
# - fronted/unpackage/
```

### 3. 更新README（如果需要）

如果发现README需要修改:

```bash
# 修改文件后
git add README.md
git commit -m "docs: Update README"
git push
```

## 📦 后续维护

### 日常提交流程

```bash
# 1. 查看修改
git status

# 2. 添加修改
git add .

# 3. 提交
git commit -m "描述你的修改"

# 4. 推送
git push
```

### 分支管理（可选）

```bash
# 创建开发分支
git checkout -b develop

# 切换回主分支
git checkout master

# 合并分支
git merge develop
```

### 标签管理（版本发布）

```bash
# 创建标签
git tag -a v1.0.0 -m "Version 1.0.0"

# 推送标签
git push origin v1.0.0

# 推送所有标签
git push origin --tags
```

## 🎉 完成！

上传成功后，你的项目将在以下地址可见:
- 仓库地址: https://github.com/Ctofol/campus-system
- 克隆地址: `git@github.com:Ctofol/campus-system.git`

## 📞 遇到问题？

### 常见错误

1. **Permission denied (publickey)**
   - 解决: 检查SSH密钥配置

2. **fatal: remote origin already exists**
   - 解决: `git remote remove origin` 然后重新添加

3. **Updates were rejected**
   - 解决: `git pull origin master` 或使用 `--force`

4. **Large files detected**
   - 解决: 检查.gitignore，移除大文件

### 获取帮助

- GitHub文档: https://docs.github.com
- Git文档: https://git-scm.com/doc
- 或在项目中提Issue

---

**祝你上传顺利！** 🚀
