# 部署和测试指南

## 问题诊断

根据错误日志，视频播放失败的原因是：
1. 后端API端点不存在（404 Not Found）
2. 前端课程详情页使用了错误的BASE_URL（127.0.0.1而不是服务器地址）

## 修复内容

### 1. 后端新增API
- `GET /courses/content/{content_id}` - 获取单个内容详情
- `GET /courses/content/{content_id}/progress` - 获取播放进度
- `POST /courses/content/{content_id}/progress` - 保存播放进度

### 2. 前端修复
- 修复 `fronted/pages/courses/detail.vue` 中的BASE_URL
- 修复 `fronted/pages/run-group/create-activity.vue` 中的变量冲突

## 部署步骤

### 方法1: 完整部署（推荐）

在服务器上执行：

```bash
# 1. 进入项目目录
cd /root/campus-system

# 2. 拉取最新代码
git pull origin master

# 3. 停止所有容器
docker-compose down

# 4. 重新构建并启动
docker-compose build
docker-compose up -d

# 5. 查看日志确认启动成功
docker-compose logs -f backend
```

按 `Ctrl+C` 退出日志查看。

### 方法2: 仅重启后端（快速）

如果只修改了后端代码：

```bash
cd /root/campus-system
git pull origin master
docker-compose restart backend

# 查看后端日志
docker-compose logs -f backend
```

### 方法3: 仅重新构建前端

如果只修改了前端代码：

```bash
cd /root/campus-system
git pull origin master
docker-compose build fronted
docker-compose up -d fronted

# 查看前端日志
docker-compose logs -f fronted
```

## 测试步骤

### 1. 测试后端API

#### Windows系统：
```bash
# 运行测试脚本
test_video_api.bat
```

#### Linux/Mac系统：
```bash
# 给脚本执行权限
chmod +x test_video_api.sh

# 运行测试脚本
./test_video_api.sh
```

#### 手动测试：

1. 登录获取token：
```bash
curl -X POST "http://120.26.17.147:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800000001","password":"123456"}'
```

2. 测试获取内容详情（假设content_id=1）：
```bash
curl -X GET "http://120.26.17.147:8000/courses/content/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

3. 测试获取进度：
```bash
curl -X GET "http://120.26.17.147:8000/courses/content/1/progress" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

4. 测试保存进度：
```bash
curl -X POST "http://120.26.17.147:8000/courses/content/1/progress?last_position=120&completed=false" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. 测试前端功能

1. 打开浏览器访问：`http://120.26.17.147`
2. 登录学生账号
3. 进入"学习"页面
4. 点击任意课程
5. 点击课程内容播放视频
6. 验证：
   - ✅ 视频能正常加载
   - ✅ 视频能正常播放
   - ✅ 进度条可以拖动
   - ✅ 退出后重新进入，从上次位置继续播放
   - ✅ 播放完成后自动跳转下一节

## 常见问题排查

### 问题1: 后端API返回404

**原因**: 后端代码没有更新或没有重启

**解决**:
```bash
cd /root/campus-system
git pull origin master
docker-compose restart backend
```

### 问题2: 前端仍然显示"视频播放失败"

**可能原因**:
1. 前端代码没有更新
2. 浏览器缓存
3. 课程内容没有视频URL

**解决**:
```bash
# 1. 更新前端代码
cd /root/campus-system
git pull origin master
docker-compose build fronted
docker-compose up -d fronted

# 2. 清除浏览器缓存（Ctrl+Shift+Delete）

# 3. 检查课程内容是否有视频URL
# 登录数据库查看
docker exec -it campus-system-postgres-1 psql -U postgres -d campus_sports
SELECT id, title, content_url FROM course_contents;
```

### 问题3: 视频URL是相对路径，无法播放

**原因**: 视频文件不在服务器上，或路径不正确

**解决**:
1. 确保视频文件已上传到服务器
2. 视频URL应该是完整的HTTP路径或正确的相对路径
3. 如果是相对路径，确保文件在 `backend/uploads/` 目录下

### 问题4: 跑团活动创建页面输入框无法输入

**原因**: 变量名冲突已修复

**解决**: 重新部署前端代码即可

## 验证部署成功

### 1. 检查容器状态
```bash
docker-compose ps
```

应该看到所有容器都是 `Up` 状态。

### 2. 检查后端日志
```bash
docker-compose logs backend | tail -50
```

应该看到类似：
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. 检查前端日志
```bash
docker-compose logs fronted | tail -50
```

应该看到nginx启动成功的日志。

### 4. 测试API端点
```bash
# 测试健康检查
curl http://120.26.17.147:8000/

# 应该返回: {"message":"Campus Sports Health System API"}
```

## 数据库检查

如果需要检查数据库中的课程数据：

```bash
# 进入数据库容器
docker exec -it campus-system-postgres-1 psql -U postgres -d campus_sports

# 查看课程列表
SELECT id, title, teacher_id FROM courses;

# 查看课程内容
SELECT id, course_id, title, content_type, content_url, duration FROM course_contents;

# 查看学习进度
SELECT * FROM course_progress;

# 退出数据库
\q
```

## 创建测试数据

如果数据库中没有课程数据，可以手动创建：

```sql
-- 创建测试课程
INSERT INTO courses (title, description, category, is_public, teacher_id, created_at, updated_at)
VALUES ('测试课程', '这是一个测试课程', 'fitness', true, 1, NOW(), NOW());

-- 创建测试内容（假设课程ID为1）
INSERT INTO course_contents (course_id, title, content_type, content_url, duration, "order", created_at)
VALUES 
(1, '第一节：热身运动', 'video', '/uploads/test_video1.mp4', 300, 1, NOW()),
(1, '第二节：核心训练', 'video', '/uploads/test_video2.mp4', 600, 2, NOW());
```

## 联系支持

如果问题仍然存在，请提供：
1. 错误截图
2. 浏览器控制台日志（F12 -> Console）
3. 后端日志：`docker-compose logs backend | tail -100`
4. 前端日志：`docker-compose logs fronted | tail -100`
