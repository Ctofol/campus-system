# 视频播放功能修复说明

## 问题描述
用户反馈视频播放失败，显示404错误和"Failed to load content"。

## 根本原因分析

### 1. 后端API缺失
前端视频播放器页面调用的API端点在后端不存在：
- `/courses/content/{content_id}` - 获取单个内容详情（404）
- `/courses/content/{content_id}/progress` - 获取/保存播放进度（404）

后端只有 `/courses/{course_id}/contents` (复数形式)，返回课程的所有内容列表，无法获取单个内容详情。

### 2. 前端配置错误
课程详情页面 `fronted/pages/courses/detail.vue` 中硬编码了错误的BASE_URL：
```javascript
const baseURL = 'http://127.0.0.1:8000';  // ❌ 本地地址
```

应该使用：
```javascript
import { BASE_URL } from '@/utils/request.js';  // ✅ 服务器地址
```

## 解决方案

### 1. 后端新增API端点 (`backend/app/routers/courses.py`)

#### 新增端点1: 获取单个内容详情
```python
@router.get("/content/{content_id}", response_model=schemas.CourseContentOut)
async def get_single_content(content_id: int, ...)
```
- 返回单个课程内容的详细信息（标题、描述、视频URL、时长等）

#### 新增端点2: 获取播放进度
```python
@router.get("/content/{content_id}/progress")
async def get_content_progress(content_id: int, ...)
```
- 返回用户对该内容的学习进度
- 包含：last_position（上次播放位置）、completed（是否完成）、progress（进度百分比）
- 如果没有记录，返回默认值（0, false, 0.0）

#### 新增端点3: 保存播放进度
```python
@router.post("/content/{content_id}/progress")
async def save_content_progress(content_id: int, last_position: int, completed: bool = False, ...)
```
- 保存或更新用户的播放进度
- 参数通过query string传递：`?last_position=120&completed=false`
- 自动计算进度百分比（基于播放位置/视频总时长）
- 完成时自动设置progress为100

### 2. 前端修复 (`fronted/pages/courses/player.vue`)

#### 修复API调用方式
- 将POST请求的data参数改为query参数
- 修复前：`data: { last_position: 120, completed: false }`
- 修复后：`url: /courses/content/${id}/progress?last_position=120&completed=false`

### 3. 跑团活动创建页面修复 (`fronted/pages/run-group/create-activity.vue`)

#### 修复变量名冲突
- 问题：`activityTime` 既作为ref变量，又在提交函数中作为局部变量使用
- 解决：将ref变量重命名为 `activityTimeValue`
- 避免了变量覆盖导致的逻辑错误

## 功能特性

### 视频播放器功能
1. ✅ 视频播放控制（播放、暂停、进度条）
2. ✅ 自动保存进度（每10秒保存一次）
3. ✅ 断点续播（记住上次播放位置）
4. ✅ 自动标记完成（播放结束时）
5. ✅ 课程列表切换
6. ✅ 自动播放下一节（完成后2秒自动跳转）
7. ✅ 错误处理（网络错误、视频加载失败）

### 进度管理
- 播放位置精确到秒
- 进度百分比自动计算
- 完成状态持久化
- 支持多设备同步（基于用户ID）

## 部署步骤

### 在服务器上执行（推荐使用快速部署脚本）

#### 方法1: 使用快速部署脚本
```bash
cd /root/campus-system
bash quick_deploy.sh
```

#### 方法2: 手动部署
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

### 验证部署

1. 检查容器状态：
```bash
docker-compose ps
```

2. 测试后端API：
```bash
bash test_video_api.sh
```

3. 在浏览器中测试前端功能

## 测试验证

### 测试步骤
1. 登录学生账号
2. 进入课程详情页
3. 点击任意课程内容
4. 验证视频能正常播放
5. 播放一段时间后退出
6. 重新进入，验证从上次位置继续播放
7. 播放到结束，验证自动标记完成
8. 验证自动跳转到下一节

### 预期结果
- ✅ 视频正常加载和播放
- ✅ 进度条可拖动
- ✅ 播放位置自动保存
- ✅ 断点续播正常工作
- ✅ 完成标记正确显示
- ✅ 课程列表切换流畅

## 注意事项

1. **视频URL格式**：确保视频URL是完整的HTTP路径或正确的相对路径
2. **权限验证**：所有API都需要用户登录（JWT token）
3. **进度计算**：需要CourseContent表中的duration字段有正确的视频时长
4. **数据库**：无需修改数据库结构，使用现有的CourseProgress表

## 相关文件
- `backend/app/routers/courses.py` - 后端API路由（新增3个端点）
- `fronted/pages/courses/player.vue` - 视频播放器页面（修复API调用）
- `fronted/pages/courses/detail.vue` - 课程详情页（修复BASE_URL）
- `fronted/pages/run-group/create-activity.vue` - 跑团活动创建页面（修复变量冲突）

## 部署和测试工具
- `quick_deploy.sh` - 快速部署脚本（Linux/Mac）
- `test_video_api.sh` - API测试脚本（Linux/Mac）
- `test_video_api.bat` - API测试脚本（Windows）
- `DEPLOY_AND_TEST.md` - 详细的部署和测试指南

## 下一步

1. 在服务器上运行 `bash quick_deploy.sh` 完成部署
2. 运行 `bash test_video_api.sh` 测试API
3. 在浏览器中测试视频播放功能
4. 如有问题，参考 `DEPLOY_AND_TEST.md` 进行排查
