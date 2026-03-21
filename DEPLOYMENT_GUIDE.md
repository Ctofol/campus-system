# 部署指南 - UI优化更新

## 概述
本次更新完成了所有UI优化需求，包括首页优化、健康报备附件上传等功能。

---

## 部署步骤

### 1. 数据库迁移

首先需要为健康报备表添加附件字段：

```bash
# 进入后端目录
cd backend

# 运行迁移脚本
python add_health_attachments.py
```

**预期输出**:
```
✓ Added 'attachments' column to health_requests table
Migration completed!
```

如果显示 "attachments column already exists"，说明字段已存在，可以继续。

---

### 2. 后端部署（Docker方式）

#### 方式A: 重启后端容器（推荐）
```bash
# 在项目根目录
docker-compose restart backend
```

#### 方式B: 完全重新构建（如果遇到问题）
```bash
# 停止所有容器
docker-compose down

# 重新构建并启动
docker-compose up -d --build backend
```

#### 验证后端运行状态
```bash
# 查看容器状态
docker-compose ps

# 查看后端日志
docker-compose logs -f backend
```

**预期输出**: 应该看到 "Application startup complete" 或类似信息

---

### 3. 前端部署

#### 在HBuilderX中：

1. 打开项目 `fronted` 目录
2. 点击菜单：运行 → 运行到手机或模拟器 → 运行到Android/iOS设备
3. 或者：发行 → 原生App-云打包

#### 测试前端连接：
- 确保 `fronted/utils/request.js` 中的 `baseUrl` 设置为：
  ```javascript
  let baseUrl = 'http://120.26.17.147:8000';
  ```

---

### 4. 验证部署

#### 4.1 测试后端API

```bash
# 测试健康报备接口（需要先登录获取token）
curl -X GET http://120.26.17.147:8000/student/health/requests \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 4.2 测试前端功能

**学生端测试清单**:
1. ✅ 首页：只显示一个"首页"标签（在底部TabBar）
2. ✅ 首页：没有今日数据统计模块
3. ✅ 运动页面：显示总里程、总时长、总消耗、运动次数
4. ✅ 我的页面：可以编辑资料（头像、签名）
5. ✅ 健康报备：可以上传图片附件（最多3张）
6. ✅ 健康报备：可以预览已上传的图片
7. ✅ 健康报备：历史记录中可以查看附件
8. ✅ 跑步页面：没有荣誉模块和天气模块

---

## 常见问题排查

### 问题1: 数据库迁移失败

**错误**: `connection refused` 或 `authentication failed`

**解决方案**:
```bash
# 检查数据库容器是否运行
docker-compose ps

# 如果数据库未运行，启动它
docker-compose up -d db

# 等待几秒后重试迁移
python backend/add_health_attachments.py
```

---

### 问题2: 后端容器启动失败

**错误**: 容器不断重启

**解决方案**:
```bash
# 查看详细日志
docker-compose logs backend

# 常见原因：
# 1. 数据库连接失败 - 检查 .env.production 文件
# 2. 端口被占用 - 检查8000端口是否被占用
# 3. 依赖包问题 - 重新构建镜像

# 重新构建
docker-compose build --no-cache backend
docker-compose up -d backend
```

---

### 问题3: 图片上传失败

**错误**: 前端显示"上传失败"

**可能原因**:
1. Token过期 - 重新登录
2. 文件大小超限 - 检查后端配置
3. uploads目录权限问题

**解决方案**:
```bash
# 检查uploads目录权限
ls -la backend/uploads

# 如果权限不足，修改权限
chmod 755 backend/uploads

# 在Docker中
docker exec campus-backend chmod 755 /app/uploads
```

---

### 问题4: 前端无法连接后端

**错误**: 网络请求失败

**解决方案**:
1. 检查服务器防火墙是否开放8000端口
2. 检查 `fronted/utils/request.js` 中的 baseUrl 配置
3. 在浏览器中直接访问 `http://120.26.17.147:8000/docs` 测试后端是否可访问

---

## 回滚方案

如果部署出现严重问题，可以回滚到之前的版本：

```bash
# 1. 停止当前容器
docker-compose down

# 2. 恢复数据库（如果有备份）
# docker exec -i campus-db psql -U postgres campus_db < backup.sql

# 3. 切换到之前的代码版本
git checkout <previous-commit-hash>

# 4. 重新启动
docker-compose up -d
```

---

## 性能优化建议

### 图片上传优化
- 前端已设置图片压缩：`sizeType: ['compressed']`
- 建议在后端添加图片大小限制（如5MB）
- 考虑使用CDN存储图片

### 数据库优化
- 为 `health_requests.attachments` 字段添加索引（如果需要频繁查询）
- 定期清理过期的健康报备记录

---

## 监控和日志

### 查看实时日志
```bash
# 后端日志
docker-compose logs -f backend

# 数据库日志
docker-compose logs -f db

# 所有服务日志
docker-compose logs -f
```

### 日志位置
- 后端日志: Docker容器内
- 前端日志: HBuilderX控制台
- 数据库日志: Docker容器内

---

## 联系支持

如果遇到无法解决的问题：
1. 收集错误日志
2. 记录复现步骤
3. 联系开发团队

---

## 附录：完整的Docker命令参考

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启特定服务
docker-compose restart backend

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend

# 进入容器
docker exec -it campus-backend bash

# 重新构建
docker-compose build --no-cache
docker-compose up -d

# 清理未使用的镜像和容器
docker system prune -a
```

---

**部署完成后，请按照"验证部署"部分的测试清单进行全面测试！**
