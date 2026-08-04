# 配置说明

后端配置由环境变量提供，代码入口为 `backend/app/config.py`。现有大写常量继续保留，以兼容当前服务代码。

## 核心配置

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `APP_ENV` | `development` | `development`、`test` 或 `production` |
| `SQLALCHEMY_DATABASE_URL` | 后端目录 SQLite | 数据库连接地址 |
| `SECRET_KEY` | 开发占位值 | JWT 密钥；生产环境必须显式设置 |
| `CAPTCHA_SECRET` | 开发占位值 | 验证码签名密钥；生产环境必须显式设置 |
| `INITIAL_ACCOUNT_PASSWORD` | `123456` | 管理员新建、导入或重置账号时使用的统一初始密码；用户首次登录必须修改 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `86400` | 保持现有两个月默认行为 |
| `FACE_PROVIDER` | `none` | `none`、`local` 或 `tencent` |
| `TENCENT_MAP_KEY` | 空 | 服务端天气接口 Key |
| `TEST_ANALYSIS_USE_BACKGROUND` | `true` | 是否使用现有后台分析方式 |

完整示例见 `backend/.env.example`。

## 配置校验

强类型解析会在导入配置时检查枚举、布尔值和数值格式。`validate_runtime_config(strict=True)` 用于部署前检查：生产环境若仍使用默认密钥，校验失败。为保持现有开发行为，应用启动暂不自动启用严格模式。

## 密钥规则

- `.env.example` 只放占位值，不能放真实服务密钥。
- 微信 AppID、客户端地图 Key 等公开标识仍应设置平台白名单和配额限制。
- 日志、测试夹具和错误响应不得输出 Token、密码、私钥或人脸 embedding。
