# 校园运动健康管理系统 (Campus Sports Health System)

一个基于 **Uni-app** 和 **FastAPI** 开发的校园运动健康管理系统，支持跑步打卡、体能测试、课程学习、跑团活动等功能。

## 🎯 项目特色

- 🏃 **智能跑步**: GPS轨迹记录、实时配速分析、步数统计
- 📹 **AI体测**: 视频上传、AI评分、姿态分析
- 📚 **在线课程**: 体育理论课程、视频学习、进度跟踪
- 👥 **跑团联盟**: 创建跑团、组织活动、排行榜
- 📊 **数据分析**: 运动数据可视化、健康报告

## 🛠 技术栈

### 前端
- **框架**: Uni-app (Vue 3 + Composition API)
- **UI**: 自定义组件库
- **地图**: 腾讯地图 API
- **平台**: 微信小程序、H5、App

### 后端
- **框架**: Python FastAPI
- **数据库**: PostgreSQL / SQLite
- **ORM**: SQLAlchemy
- **认证**: JWT Token

## ✨ 主要功能

### 👨‍🎓 学生端
- **跑步打卡**: 
  - 普通跑步模式（自由跑步）
  - 校园打卡模式（定点打卡）
  - 实时轨迹记录、配速分析
  - 步数统计（加速度传感器）
  
- **体能测试**: 
  - 多种测试类型（仰卧起坐、俯卧撑、跳绳等）
  - 视频/图片上传
  - AI智能评分
  
- **课程学习**:
  - 浏览体育课程
  - 在线学习视频
  - 学习进度跟踪
  
- **跑团活动**:
  - 加入跑团
  - 参与活动
  - 查看排行榜

### 👩‍🏫 教师端
- **数据看板**: 
  - 班级运动数据统计
  - 学生体能概览
  - 数据可视化图表
  
- **任务管理**: 
  - 发布跑步/体测任务
  - 设置任务要求
  - 查看完成情况
  
- **审批管理**: 
  - 审核学生活动
  - 查看体测视频
  - 成绩评定
  
- **课程管理**:
  - 创建课程
  - 上传课程内容
  - 管理学员

### 🔧 管理员端
- **用户管理**: 批量导入学生、教师信息
- **班级管理**: 创建班级、分配班主任
- **系统配置**: 打卡点设置、系统参数

## 🌐 在线访问

- **前端H5**: http://101.37.24.171
- **API文档**: http://101.37.24.171:8000/docs
- **服务器**: 101.37.24.171:8000

## 🚀 快速开始

### 环境要求
- Python 3.8+
- PostgreSQL 12+ (或 SQLite)
- Node.js 14+ (可选)
- HBuilderX (前端开发)

### 1. 后端配置

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 初始化数据库（可选）
python seed.py

# 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API文档: http://localhost:8000/docs

### 2. 前端配置

1. 使用 HBuilderX 打开 `fronted` 目录

2. 修改API地址（真机调试时）:
   - 打开 `fronted/utils/request.js`
   - 修改 `baseUrl` 为你的电脑IP地址
   ```javascript
   // 真机调试地址
   baseUrl = 'http://192.168.0.216:8000'; // 改为你的IP
   ```

3. 配置小程序AppID（可选）:
   - 打开 `fronted/manifest.json`
   - 修改 `mp-weixin.appid`

4. 运行项目:
   - 浏览器: 运行 → 运行到浏览器 → Chrome
   - 小程序: 运行 → 运行到小程序模拟器 → 微信开发者工具
   - 真机: 连接手机 → 运行 → 运行到手机

### 3. 测试账号

```
学生账号: 13800138000 / 123456
教师账号: 13800138001 / 123456
```

## 📂 项目结构

```
campus-system/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── main.py            # 主应用入口
│   │   ├── models.py          # 数据模型
│   │   ├── schemas.py         # Pydantic模型
│   │   ├── auth.py            # 认证逻辑
│   │   ├── database.py        # 数据库配置
│   │   ├── routers/           # 路由模块
│   │   │   ├── admin.py       # 管理员接口
│   │   │   ├── teacher.py     # 教师接口
│   │   │   ├── student.py     # 学生接口
│   │   │   ├── courses.py     # 课程接口
│   │   │   └── run_groups.py  # 跑团接口
│   │   └── services/          # 业务逻辑
│   ├── uploads/               # 上传文件
│   ├── requirements.txt       # Python依赖
│   └── seed.py               # 数据初始化
│
├── fronted/                   # 前端代码
│   ├── pages/                # 页面
│   │   ├── tab/             # 底部导航页
│   │   ├── login/           # 登录注册
│   │   ├── run/             # 跑步页面
│   │   ├── test/            # 体测页面
│   │   ├── courses/         # 课程页面
│   │   ├── run-group/       # 跑团页面
│   │   ├── admin/           # 管理员页面
│   │   └── teacher/         # 教师页面
│   ├── components/          # 组件
│   │   ├── student-home/    # 学生首页
│   │   ├── student-run/     # 跑步组件
│   │   ├── teacher-home/    # 教师首页
│   │   └── ...
│   ├── utils/               # 工具函数
│   │   ├── request.js       # 网络请求
│   │   └── location.js      # 定位工具
│   ├── static/              # 静态资源
│   ├── manifest.json        # 应用配置
│   └── pages.json          # 页面配置
│
├── .gitignore
├── docker-compose.yml       # Docker配置
└── README.md
```

## 📱 功能截图

（待添加）

## 🔧 配置说明

### 地图配置
在 `fronted/manifest.json` 中配置腾讯地图Key:
```json
"sdkConfigs": {
  "maps": {
    "tencent": {
      "key": "YOUR_TENCENT_MAP_KEY"
    }
  }
}
```

### 数据库配置
在 `backend/app/database.py` 中配置数据库连接:
```python
DATABASE_URL = "postgresql://user:password@localhost:5432/campus_db"
# 或使用SQLite
DATABASE_URL = "sqlite:///./campus_sports.db"
```

## 📝 开发文档

- [API文档](backend/API_DOCUMENTATION.md)
- [课程功能说明](fronted/COURSE_DETAIL_API.md)
- [部署指南](fronted/DEPLOY.md)
- [更新历史](COMPLETE_UPDATE_HISTORY.md)

## ⚠️ 注意事项

### 真机测试
1. **定位功能**: 模拟器定位不准确，必须真机测试
2. **步数统计**: 需要加速度传感器，模拟器不支持
3. **视频上传**: 建议在真机上测试，模拟器可能不支持

### 权限配置
小程序需要以下权限:
- 位置信息（跑步轨迹）
- 相机（拍摄体测视频）
- 相册（选择照片/视频）
- 加速度传感器（步数统计）

### 网络配置
- 开发环境: 在微信开发者工具中勾选"不校验合法域名"
- 生产环境: 需要配置服务器域名白名单

## 🐛 常见问题

### 1. 登录502错误
- 检查后端服务是否启动
- 检查IP地址配置是否正确
- 确保手机和电脑在同一WiFi

### 2. 步数不增加
- 必须在真机上测试
- 检查是否授予加速度传感器权限
- 查看Console日志确认传感器启动

### 3. 视频上传失败
- 检查文件大小（限制100MB）
- 确保授予相机和相册权限
- 查看网络连接状态

## 📄 License

MIT License

## 👥 贡献者

- Ctofol - 项目开发

## 📮 联系方式

如有问题或建议，欢迎提Issue或PR。
