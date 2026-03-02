# 小程序发布前检查清单

## 检查时间
2026-02-28

## 检查状态
✅ 已完成全面检查

---

## 一、后端配置检查

### 1.1 数据库配置 ✅
- **数据库类型**: PostgreSQL
- **连接地址**: `postgresql://postgres:Chen20070509@localhost:5432/campus_db`
- **配置文件**: `backend/app/database.py`
- **状态**: 正常，支持环境变量配置

### 1.2 服务器配置 ✅
- **运行地址**: `http://0.0.0.0:8000`
- **H5访问地址**: `http://127.0.0.1:8000`
- **小程序/真机地址**: `http://192.168.0.216:8000`
- **启动脚本**: `backend/start_backend.bat`
- **状态**: 后端服务已启动（进程ID: 1）

### 1.3 CORS配置 ✅
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（开发环境）
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)
```
- **状态**: 已配置为允许所有来源，适合开发和小程序测试

### 1.4 静态文件服务 ✅
```python
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
```
- **上传目录**: `uploads/`（按月份分组：`uploads/YYYYMM/`）
- **访问路径**: `http://192.168.0.216:8000/uploads/YYYYMM/filename.ext`
- **状态**: 正常配置

---

## 二、API接口检查

### 2.1 核心路由注册 ✅
所有路由已在 `backend/app/main.py` 中正确注册：
- ✅ `admin.router` - 管理员接口
- ✅ `teacher.router` - 教师接口
- ✅ `courses.router` - 课程管理接口
- ✅ `approvals.router` - 审批接口
- ✅ `student.router` - 学生接口
- ✅ `upload.router` - 文件上传接口
- ✅ `run_groups.router` - 跑团接口

### 2.2 认证机制 ✅
- **Token类型**: JWT Bearer Token
- **过期时间**: 7天
- **可选认证**: 课程详情等接口支持未登录访问
- **状态**: 正常，支持小程序端认证

### 2.3 关键接口列表

#### 认证接口 ✅
- `POST /auth/register` - 注册
- `POST /auth/login` - 登录
- `GET /users/profile` - 获取用户信息
- `GET /common/captcha` - 获取验证码

#### 学生接口 ✅
- `POST /activity/finish` - 提交运动记录
- `GET /activity/history` - 运动历史
- `GET /student/summary` - 今日统计
- `GET /student/tasks` - 我的任务
- `POST /student/health/request` - 健康报备

#### 教师接口 ✅
- `GET /teacher/dashboard/stats` - 教师工作台统计
- `GET /teacher/classes` - 班级管理
- `GET /teacher/students` - 学生管理
- `POST /teacher/tasks` - 创建任务
- `GET /teacher/health/requests` - 健康审批

#### 课程接口 ✅
- `GET /courses/` - 课程列表（无需登录）
- `GET /courses/{id}` - 课程详情（无需登录）
- `POST /courses/{id}/enroll` - 选课
- `GET /courses/my/enrollments` - 我的课程
- `POST /courses/` - 创建课程（教师）
- `POST /courses/{id}/contents` - 添加课程内容

#### 文件上传接口 ✅
- `POST /upload/file` - 通用文件上传
  - 支持视频（MP4，最大100MB）
  - 支持图片（JPG/PNG，最大5MB）
  - 返回格式：`{"url": "/uploads/YYYYMM/filename.ext", "type": "video|image", "size": 12345}`

#### 跑团接口 ✅
- `POST /run-group/create` - 创建跑团
- `POST /run-group/join` - 加入跑团
- `GET /run-group/list` - 跑团列表
- `GET /run-group/rank` - 跑团排行榜

---

## 三、前端配置检查

### 3.1 小程序配置 ✅
**文件**: `fronted/manifest.json`
- **AppID**: `wx0b00092e88476970`
- **小程序名称**: 灵析运动
- **权限配置**:
  - ✅ 位置权限（scope.userLocation）
  - ✅ 相机权限（scope.camera）
  - ✅ 相册权限（scope.album）
  - ✅ 录音权限（scope.record）

### 3.2 地图配置 ✅
- **地图SDK**: 腾讯地图
- **Key**: `ET4BZ-QJAL4-EMPUD-FBOLE-M23H3-3RBXD`
- **状态**: 已配置

### 3.3 网络请求配置 ✅
**文件**: `fronted/utils/request.js`

```javascript
// H5环境
baseUrl = 'http://127.0.0.1:8000';

// 小程序/真机环境
baseUrl = 'http://192.168.0.216:8000';
```

**特性**:
- ✅ 条件编译支持（#ifdef H5 / #ifndef H5）
- ✅ 自动Token管理
- ✅ 401自动跳转登录
- ✅ 统一错误处理

### 3.4 文件上传工具 ✅
**文件**: `fronted/utils/upload.js`

**功能**:
- ✅ 文件类型验证（图片/视频/文档）
- ✅ 文件大小验证
- ✅ 批量上传支持
- ✅ 选择并上传图片（`chooseAndUploadImage`）
- ✅ 选择并上传视频（`chooseAndUploadVideo`）
- ✅ 错误提示封装

---

## 四、页面路由检查

### 4.1 核心页面 ✅
所有页面已在 `fronted/pages.json` 中正确配置：

**Tab页面**:
- ✅ `/pages/tab/home` - 首页
- ✅ `/pages/tab/function` - 运动
- ✅ `/pages/tab/learn` - 课程
- ✅ `/pages/tab/mine` - 我的

**学生功能页面**:
- ✅ `/pages/run/run` - 跑步
- ✅ `/pages/test/test` - 体能测试
- ✅ `/pages/result/result` - 结算
- ✅ `/pages/student/tasks/list` - 我的任务
- ✅ `/pages/history/history` - 历史记录
- ✅ `/pages/health/request` - 健康报备

**教师功能页面**:
- ✅ `/pages/teacher/home/home` - 教师工作台
- ✅ `/pages/teacher/students/students` - 学员管理
- ✅ `/pages/teacher/tasks/tasks` - 任务管理
- ✅ `/pages/teacher/approve/approve` - 活动审批
- ✅ `/pages/teacher/resources/resources` - 教学资源

**课程页面**:
- ✅ `/pages/courses/list` - 课程列表
- ✅ `/pages/courses/detail` - 课程详情
- ✅ `/pages/courses/create` - 创建课程
- ✅ `/pages/courses/content-manage` - 课程内容管理

**跑团页面**:
- ✅ `/pages/run-group/discover` - 跑团发现
- ✅ `/pages/run-group/my` - 我的跑团
- ✅ `/pages/run-group/detail` - 跑团详情
- ✅ `/pages/run-group/activity-list` - 活动列表

**通用页面**:
- ✅ `/pages/login/login` - 登录
- ✅ `/pages/register/register` - 注册

### 4.2 导航栏配置 ✅
```json
{
  "navigationBarTextStyle": "black",
  "navigationBarTitleText": "灵析运动",
  "navigationBarBackgroundColor": "#F8F8F8",
  "backgroundColor": "#F8F8F8"
}
```

### 4.3 TabBar配置 ✅
- ✅ 首页（home）
- ✅ 运动（function）
- ✅ 课程（learn）
- ✅ 我的（mine）

---

## 五、小程序特有功能检查

### 5.1 地图定位功能 ✅
**使用场景**:
- 跑步页面（`/pages/run/run`）
- 位置选择（`/pages/common/choose-location/choose-location`）

**配置状态**:
- ✅ 腾讯地图SDK已配置
- ✅ 位置权限已声明
- ✅ 条件编译支持

### 5.2 文件上传功能 ✅
**支持场景**:
- 课程封面上传
- 课程视频上传
- 运动视频上传
- 头像上传

**实现方式**:
```javascript
// 使用uni.uploadFile
uni.uploadFile({
  url: `${BASE_URL}/upload/file`,
  filePath: filePath,
  name: 'file',
  header: {
    'Authorization': `Bearer ${token}`
  }
})
```

**条件编译**:
```javascript
// #ifdef H5
// H5环境使用input[type=file]
// #endif

// #ifndef H5
// 小程序使用uni.chooseImage/uni.chooseVideo
// #endif
```

### 5.3 相机功能 ✅
**使用场景**:
- 拍照上传
- 视频录制

**权限配置**:
- ✅ scope.camera
- ✅ scope.album

---

## 六、测试账号

### 6.1 学生账号 ✅
- **手机号**: 13800138000
- **密码**: 123456
- **角色**: student

### 6.2 教师账号 ✅
- **手机号**: 13800138001
- **密码**: 123456
- **角色**: teacher

### 6.3 测试数据 ✅
- **课程ID 7**: 标题"体育课"，无封面
- **课程ID 8**: 标题"好渴"，有封面

---

## 七、潜在问题和建议

### 7.1 网络配置 ⚠️
**问题**: 小程序使用局域网IP `192.168.0.216:8000`
**影响**: 
- 只能在同一局域网内测试
- 无法在外网环境使用

**建议**:
1. 开发测试阶段：继续使用局域网IP
2. 正式发布前：
   - 部署到公网服务器
   - 配置域名和HTTPS
   - 更新 `fronted/utils/request.js` 中的生产环境地址

### 7.2 HTTPS要求 ⚠️
**问题**: 小程序正式版要求使用HTTPS
**当前状态**: 使用HTTP（仅开发测试可用）

**建议**:
1. 申请SSL证书
2. 配置Nginx反向代理
3. 在小程序后台配置服务器域名

### 7.3 文件上传大小限制 ⚠️
**当前限制**:
- 视频: 100MB
- 图片: 5MB

**建议**:
- 小程序端添加上传前压缩
- 考虑使用云存储服务（如腾讯云COS）

### 7.4 数据隔离 ✅
**状态**: 已实现教师数据隔离
- 教师只能看到自己班级的学生数据
- 教师只能管理自己创建的任务
- 教师只能审批自己班级的申请

---

## 八、发布前必做事项

### 8.1 开发环境测试 ✅
- [x] 后端服务正常启动
- [x] 数据库连接正常
- [x] API接口可访问
- [x] 文件上传功能正常

### 8.2 小程序开发工具测试 📋
**待测试项目**:
- [ ] 登录注册流程
- [ ] 学生端核心功能（跑步、任务、课程）
- [ ] 教师端核心功能（工作台、学生管理、任务管理）
- [ ] 文件上传（图片、视频）
- [ ] 地图定位功能
- [ ] 页面跳转和导航

### 8.3 真机测试 📋
**待测试项目**:
- [ ] 网络请求（确保能访问 `192.168.0.216:8000`）
- [ ] 相机和相册权限
- [ ] 位置权限
- [ ] 文件上传性能
- [ ] 页面加载速度

### 8.4 发布准备 📋
**待完成项目**:
- [ ] 申请小程序正式版
- [ ] 配置服务器域名
- [ ] 申请SSL证书
- [ ] 配置HTTPS
- [ ] 在小程序后台配置合法域名
- [ ] 提交代码审核

---

## 九、检查结论

### 9.1 当前状态
✅ **开发环境配置完整，可以进行小程序开发工具测试**

### 9.2 核心功能完整性
- ✅ 后端API接口完整
- ✅ 前端页面路由完整
- ✅ 认证机制正常
- ✅ 文件上传功能完整
- ✅ 数据隔离机制完善
- ✅ 小程序特有功能支持（地图、相机、文件选择）

### 9.3 下一步行动
1. **立即可做**: 在微信开发者工具中测试小程序功能
2. **真机测试**: 确保手机和电脑在同一局域网，测试真机功能
3. **发布准备**: 完成HTTPS配置和域名备案后，提交审核

---

## 十、快速启动指南

### 10.1 启动后端
```bash
cd backend
start_backend.bat
```
或
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 10.2 启动前端（HBuilderX）
1. 打开HBuilderX
2. 打开项目 `fronted` 目录
3. 运行 -> 运行到小程序模拟器 -> 微信开发者工具

### 10.3 真机测试
1. 确保手机和电脑在同一局域网
2. 确认电脑IP为 `192.168.0.216`（或更新配置文件）
3. 在微信开发者工具中点击"预览"
4. 使用微信扫码在真机上测试

---

**检查完成时间**: 2026-02-28
**检查人员**: Kiro AI Assistant
**检查结果**: ✅ 通过，可以进行小程序测试
