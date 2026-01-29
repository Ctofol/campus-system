# 校园运动管理系统 (Campus Sports System)

这是一个基于 **Uni-app** 和 **FastAPI** 开发的校园运动管理系统，旨在帮助学校管理学生的日常跑步打卡和体能测试。系统包含学生端（APP/小程序）和教师端（管理后台）。

## 🛠 技术栈

- **前端**: Uni-app (Vue 3)
- **后端**: Python FastAPI
- **数据库**: PostgreSQL
- **开发工具**: HBuilderX, PyCharm/VS Code

## ✨ 主要功能

### 👨‍🎓 学生端
- **跑步打卡**: 基于 GPS 的实时跑步轨迹记录、配速分析、校园定点打卡。
- **体能测试 (AI Police)**: 专项体能测试（如 2000米），支持视频录制与上传证据。
- **AI 助手**: 智能问答助手，提供运动建议和数据分析。
- **个人中心**: 查看历史运动记录、成就徽章。

### 👩‍🏫 教师端
- **数据看板**: 查看班级整体运动数据、异常预警。
- **审批管理**: 审核学生提交的体测视频和成绩，支持视频在线预览。
- **任务管理**: 发布跑步或体测任务。
- **学生管理**: 管理学生档案和班级信息。

## 🚀 快速开始

### 1. 后端环境配置 (Backend)

确保已安装 **Python 3.8+** 和 **PostgreSQL**。

1. 进入后端目录：
   ```bash
   cd backend
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 配置数据库：
   - 确保本地 PostgreSQL 服务已启动。
   - 检查/修改 `app/database.py` 中的数据库连接配置。

4. 启动服务：
   ```bash
   # 在 backend 目录下运行
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   启动成功后，API 文档地址: `http://localhost:8000/docs`

### 2. 前端环境配置 (Frontend)

需使用 **HBuilderX** 打开 `fronted` 目录。

#### ⚠️ 真机调试关键步骤 (重要)

如果你需要使用手机连接电脑进行真机调试（App 或 小程序），**必须修改 API 请求地址**：

1. 打开文件: `fronted/utils/request.js`
2. 找到以下代码段：
   ```javascript
   // #ifndef H5
   baseUrl = 'http://10.48.100.174:8000'; // 修改为你电脑当前的局域网 IP
   // #endif
   ```
3. 将 IP 地址修改为你电脑当前的 WiFi IP 地址（可通过 cmd 输入 `ipconfig` 查看）。
   > **注意**: 手机和电脑必须连接同一个 WiFi。

#### 运行项目

- **浏览器运行**: 菜单栏 -> 运行 -> 运行到浏览器 -> Chrome。
- **真机/模拟器运行**: 连接手机 -> 菜单栏 -> 运行 -> 运行到手机或模拟器。

## 📂 目录结构

```
campus-system/
├── backend/                # 后端代码
│   ├── app/                # 核心逻辑 (API, Models, Schemas)
│   ├── uploads/            # 上传的媒体文件 (视频/图片)
│   └── requirements.txt    # Python 依赖
├── fronted/                # 前端代码 (Uni-app)
│   ├── pages/              # 页面文件 (学生端/教师端)
│   ├── utils/              # 工具函数 (request.js 等)
│   └── static/             # 静态资源
└── README.md               # 项目文档
```

## 📝 注意事项

1. **视频上传**: 体测视频文件较大，请确保网络环境良好，真机调试时尽量靠近路由器。
2. **地图服务**: 跑步功能依赖地图组件，需确保 manifest.json 中配置了有效的地图 API Key (如高德/腾讯地图)。
3. **权限**: 手机端运行时需授权 **定位** 和 **相机/麦克风** 权限。
