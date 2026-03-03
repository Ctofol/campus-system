# 校园运动健康系统 - 完整更新历史

## 最新更新 (2026-03-03)

### 🎯 核心功能完善

#### 1. 体测视频上传与AI评分系统
**学生端：**
- ✅ 支持体测视频上传功能
- ✅ 自动上传到服务器并保存URL
- ✅ 提交后生成模拟AI评分（70-95分）
- ✅ 显示评分详情和动作标准度

**教师端：**
- ✅ 实时监控学生体测视频
- ✅ 显示最近2小时内的体测记录
- ✅ 视频播放器支持在线播放
- ✅ AI评分和动作标准度展示
- ✅ 修复视频URL路径问题（完整URL拼接）

**后端API：**
- ✅ `/upload/file` - 文件上传接口
- ✅ `/activity/finish` - 体测记录提交
- ✅ `/teacher/tests/live` - 实时体测数据获取
- ✅ 数据库字段优化（video_url允许为空）

#### 2. 跑团系统完整实现
**跑团管理：**
- ✅ 创建跑团功能
- ✅ 加入/退出跑团
- ✅ 跑团详情页面
- ✅ 成员列表展示
- ✅ 跑团排行榜

**活动管理：**
- ✅ 发布跑团活动
- ✅ 活动封面上传功能
- ✅ 活动列表展示（支持筛选）
- ✅ 活动详情页面
- ✅ 报名/取消报名功能
- ✅ 删除静态测试数据，改为真实后端数据

**权限控制：**
- ✅ 跑团创建者身份识别
- ✅ 创建者显示"发布活动"按钮
- ✅ 普通成员显示"退出跑团"按钮
- ✅ 非成员显示"加入跑团"按钮

**数据模型：**
- ✅ RunGroup - 跑团基础信息
- ✅ RunGroupMember - 成员关系
- ✅ RunGroupActivity - 活动信息（新增cover_image字段）
- ✅ RunGroupActivityApplication - 报名记录

#### 3. 前后端连接优化
**服务器部署：**
- ✅ 阿里云服务器配置（120.26.17.147:8000）
- ✅ Docker容器化部署
- ✅ PostgreSQL数据库配置
- ✅ 文件上传目录挂载

**前端配置：**
- ✅ 统一BASE_URL配置
- ✅ 请求拦截器优化
- ✅ Token自动管理
- ✅ 错误处理优化

**数据库管理：**
- ✅ 数据库清理脚本
- ✅ Volume管理优化
- ✅ 自动表结构创建

---

## 之前的更新记录

### Phase 5: 跑团联盟系统 (2026-02)

#### 5.1 跑团基础功能
- ✅ 跑团创建与管理
- ✅ 成员加入/退出机制
- ✅ 跑团信息展示
- ✅ 成员列表管理

#### 5.2 跑团活动系统
- ✅ 活动发布功能
- ✅ 活动报名系统
- ✅ 活动状态管理（报名中/进行中/已结束）
- ✅ 活动详情页面

#### 5.3 跑团排行榜
- ✅ 总里程排名
- ✅ 成员贡献统计
- ✅ 实时数据更新

---

### Phase 4: 课程系统 (2026-01)

#### 4.1 课程管理
- ✅ 课程创建与编辑
- ✅ 课程分类（理论/技能/体能）
- ✅ 课程封面上传
- ✅ 课程内容管理

#### 4.2 课程学习
- ✅ 课程浏览与搜索
- ✅ 课程报名
- ✅ 学习进度跟踪
- ✅ 视频播放记录

#### 4.3 教师功能
- ✅ 课程发布权限
- ✅ 学员管理
- ✅ 学习数据统计

---

### Phase 3: 教师管理系统 (2025-12)

#### 3.1 教师工作台
- ✅ 数据概览面板
- ✅ 待办事项提醒
- ✅ 快捷操作入口
- ✅ 周趋势图表

#### 3.2 班级管理
- ✅ 班级创建与绑定
- ✅ 学生管理
- ✅ 班级统计数据
- ✅ 批量操作功能

#### 3.3 任务管理
- ✅ 任务发布系统
- ✅ 任务类型（跑步/体测）
- ✅ 任务截止时间
- ✅ 完成情况统计

#### 3.4 审批系统
- ✅ 活动审批
- ✅ 健康报备审批
- ✅ 批量审批功能
- ✅ 审批历史记录

#### 3.5 测试监控
- ✅ 实时监控面板
- ✅ 数据分析图表
- ✅ 历史记录查询
- ✅ 异常处理系统

---

### Phase 2: 学生运动系统 (2025-11)

#### 2.1 跑步功能
- ✅ GPS轨迹记录
- ✅ 实时数据显示（距离/时长/配速）
- ✅ 打卡点系统
- ✅ 运动数据提交

#### 2.2 体能测试
- ✅ 多种测试类型
- ✅ 计时功能
- ✅ 成绩记录
- ✅ 历史数据查询

#### 2.3 运动历史
- ✅ 历史记录列表
- ✅ 详细数据展示
- ✅ 统计图表
- ✅ 数据导出

#### 2.4 健康管理
- ✅ 健康状态报备
- ✅ 请假申请
- ✅ 异常状态标记
- ✅ 审批流程

---

### Phase 1: 基础架构 (2025-10)

#### 1.1 用户系统
- ✅ 用户注册/登录
- ✅ 角色管理（学生/教师/管理员）
- ✅ 验证码系统
- ✅ Token认证

#### 1.2 数据库设计
- ✅ 用户表（User）
- ✅ 班级表（Class）
- ✅ 活动表（Activity）
- ✅ 任务表（Task）
- ✅ 关系表设计

#### 1.3 前端架构
- ✅ uni-app框架搭建
- ✅ 组件化开发
- ✅ 路由配置
- ✅ 状态管理

#### 1.4 后端架构
- ✅ FastAPI框架
- ✅ SQLAlchemy ORM
- ✅ RESTful API设计
- ✅ 中间件配置

---

## 技术栈

### 前端
- **框架**: uni-app (Vue 3)
- **UI**: 自定义组件库
- **状态管理**: Composition API
- **网络请求**: uni.request封装
- **地图**: 高德地图API

### 后端
- **框架**: FastAPI (Python 3.10+)
- **数据库**: PostgreSQL
- **ORM**: SQLAlchemy
- **认证**: JWT Token
- **文件存储**: 本地文件系统

### 部署
- **服务器**: 阿里云ECS
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx（可选）
- **数据库**: PostgreSQL容器

---

## 数据库表结构

### 核心表
1. **users** - 用户信息
2. **classes** - 班级信息
3. **activities** - 运动记录
4. **activity_metrics** - 运动指标（含video_url）
5. **tasks** - 任务信息
6. **courses** - 课程信息
7. **run_groups** - 跑团信息
8. **run_group_members** - 跑团成员
9. **run_group_activities** - 跑团活动（含cover_image）
10. **run_group_activity_applications** - 活动报名

---

## API接口汇总

### 认证接口
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `GET /common/captcha` - 获取验证码

### 学生接口
- `POST /activity/finish` - 提交运动记录
- `GET /activity/history` - 运动历史
- `GET /student/tasks` - 我的任务
- `POST /upload/file` - 文件上传

### 教师接口
- `GET /teacher/dashboard/stats` - 工作台数据
- `GET /teacher/classes` - 班级列表
- `GET /teacher/tasks` - 任务管理
- `GET /teacher/tests/live` - 实时体测监控
- `GET /teacher/tests/stats` - 体测数据分析
- `POST /teacher/activity/{id}/approve` - 审批活动

### 跑团接口
- `POST /run-group/create` - 创建跑团
- `POST /run-group/join` - 加入跑团
- `POST /run-group/leave` - 退出跑团
- `GET /run-group/my` - 我的跑团
- `GET /run-group/list` - 跑团列表
- `GET /run-group/members/{group_id}` - 成员列表
- `POST /run-group/activity/create` - 创建活动
- `GET /run-group/activities/{group_id}` - 活动列表
- `GET /run-group/rank` - 跑团排行榜

### 课程接口
- `GET /courses/` - 课程列表
- `GET /courses/{id}` - 课程详情
- `POST /courses/` - 创建课程
- `POST /courses/{id}/enroll` - 报名课程
- `GET /courses/my/enrollments` - 我的课程

---

## 部署指南

### 服务器配置
```bash
# 1. 拉取代码
git pull origin master

# 2. 停止服务
docker-compose down

# 3. 清理数据库（可选）
docker volume rm campus-system_postgres_data

# 4. 启动服务
docker-compose up -d backend db

# 5. 查看日志
docker logs -f campus-backend
```

### 创建管理员账号
```bash
docker exec -it campus-backend python3 -c "
from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

db = SessionLocal()
admin = User(
    phone='admin',
    name='系统管理员',
    role='admin',
    password_hash=get_password_hash('admin123')
)
db.add(admin)
db.commit()
print('✅ 管理员账号创建成功！')
db.close()
"
```

### 创建教师账号
```bash
docker exec -it campus-backend python3 -c "
from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

db = SessionLocal()
teacher = User(
    phone='teacher001',
    name='张老师',
    role='teacher',
    password_hash=get_password_hash('123456')
)
db.add(teacher)
db.commit()
print('✅ 教师账号创建成功！')
db.close()
"
```

---

## 已知问题与解决方案

### 1. 视频无法播放
**问题**: 教师端看不到学生上传的视频
**原因**: 视频URL是相对路径
**解决**: 已修复，自动拼接完整URL

### 2. 跑团身份识别
**问题**: 创建者看不到"发布活动"按钮
**原因**: userInfo字段名不匹配
**解决**: 已修复，使用正确的userId字段

### 3. 数据库字段约束
**问题**: video_url字段NOT NULL导致提交失败
**原因**: 旧数据库表结构
**解决**: 已修复，video_url允许为空

### 4. 静态测试数据
**问题**: 活动列表显示假数据
**原因**: 前端写死的测试数据
**解决**: 已删除，改为从后端获取

---

## 下一步计划

### 短期目标
- [ ] AI视频评分接口接入
- [ ] 跑团活动详情页完善
- [ ] 数据统计图表优化
- [ ] 移动端适配优化

### 中期目标
- [ ] 社交功能（点赞/评论）
- [ ] 成就系统
- [ ] 排行榜系统
- [ ] 消息通知系统

### 长期目标
- [ ] 小程序版本
- [ ] iOS/Android原生应用
- [ ] 数据分析平台
- [ ] 智能推荐系统

---

## 贡献者
- 开发团队
- 测试团队
- 运维团队

---

## 更新日志

### v2.0.0 (2026-03-03)
- 🎉 体测视频上传与AI评分系统上线
- 🎉 跑团系统完整实现
- 🐛 修复视频播放问题
- 🐛 修复跑团权限识别问题
- ✨ 活动封面上传功能
- ✨ 删除静态测试数据

### v1.5.0 (2026-02-15)
- 🎉 跑团联盟系统上线
- ✨ 跑团活动管理
- ✨ 跑团排行榜

### v1.0.0 (2025-12-01)
- 🎉 系统正式上线
- ✨ 基础功能完整实现
- ✨ 教师管理系统
- ✨ 学生运动系统

---

**最后更新时间**: 2026-03-03
**文档版本**: v2.0.0
