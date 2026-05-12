# 灵析运动App - 后端API文档

## 概述

本文档定义了灵析运动App后端API的完整规范，基于RESTful设计原则，兼容Java/Node.js/Python等主流后端技术栈。

---

## 通用规范

### 1. 响应格式

#### 标准响应格式
```json
{
  "code": 200,
  "data": {},
  "msg": "操作成功"
}
```

#### 字段说明
| 字段 | 类型 | 说明 |
|------|------|------|
| code | Integer | 状态码（200=成功，400=参数错误，404=资源不存在，500=服务器错误） |
| data | Object/Array | 业务数据 |
| msg | String | 提示信息 |

### 2. 状态码规范

| 状态码 | 说明 | 使用场景 |
|--------|------|----------|
| 200 | 成功 | 请求成功 |
| 201 | 创建成功 | 资源创建成功 |
| 400 | 请求错误 | 参数错误、验证失败 |
| 401 | 未授权 | Token失效或未登录 |
| 403 | 无权限 | 没有访问权限 |
| 404 | 不存在 | 资源不存在 |
| 413 | 文件过大 | 上传文件超过限制 |
| 415 | 格式不支持 | 文件格式不支持 |
| 500 | 服务器错误 | 服务器内部错误 |

### 3. 请求方式

| 方法 | 说明 | 使用场景 |
|------|------|----------|
| GET | 查询 | 获取资源 |
| POST | 创建/提交 | 创建资源、提交数据 |
| PUT | 修改 | 更新资源 |
| DELETE | 删除 | 删除资源 |

### 4. 请求头

```
Content-Type: application/json
Authorization: Bearer {token}
```

---

## 课程相关接口

### 1. 获取课程列表

#### 接口信息
- **路径**: `/api/courses` 或 `/courses/`
- **方法**: GET
- **权限**: 需要登录

#### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | Integer | 否 | 页码（默认1） |
| size | Integer | 否 | 每页数量（默认20） |
| category | String | 否 | 课程类型（skill/theory/fitness） |
| teacher_id | Integer | 否 | 教师ID筛选 |

#### 请求示例
```
GET /api/courses?page=1&size=20&category=skill
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### 响应示例
```json
{
  "code": 200,
  "data": {
    "items": [
      {
        "id": 1,
        "title": "篮球基础技能训练",
        "description": "本课程将教授篮球的基本技能",
        "cover_url": "http://127.0.0.1:8000/uploads/basketball.jpg",
        "category": "skill",
        "is_public": true,
        "teacher_id": 50,
        "created_at": "2026-02-27T10:00:00"
      }
    ],
    "total": 10,
    "page": 1,
    "size": 20
  },
  "msg": "获取成功"
}
```


### 2. 获取课程详情

#### 接口信息
- **路径**: `/api/courses/{id}` 或 `/courses/{id}`
- **方法**: GET
- **权限**: 需要登录

#### 路径参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | Integer | 是 | 课程ID |

#### 请求示例
```
GET /api/courses/1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### 响应示例
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "title": "篮球基础技能训练",
    "description": "本课程将教授篮球的基本技能，包括运球、传球、投篮等",
    "cover_url": "http://127.0.0.1:8000/uploads/basketball.jpg",
    "category": "skill",
    "is_public": true,
    "teacher_id": 50,
    "teacher_name": "张老师",
    "created_at": "2026-02-27T10:00:00",
    "enrolled": false,
    "enrollment_count": 15,
    "contents": [
      {
        "id": 1,
        "title": "第一章：运球基础",
        "content_type": "video",
        "content_url": "http://example.com/video1.mp4",
        "duration": 600,
        "order": 1
      }
    ]
  },
  "msg": "获取成功"
}
```

#### 错误响应
```json
{
  "code": 404,
  "data": null,
  "msg": "课程不存在"
}
```

---

### 3. 创建课程

#### 接口信息
- **路径**: `/api/courses` 或 `/courses/`
- **方法**: POST
- **权限**: 需要教师权限

#### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| title | String | 是 | 课程名称（最大50字符） |
| category | String | 是 | 课程类型（skill/theory/fitness） |
| description | String | 是 | 课程简介（最大200字符） |
| cover_url | String | 是 | 课程封面URL |
| content | String | 否 | 课程详细内容（富文本HTML） |
| is_public | Boolean | 否 | 是否公开（默认true） |

#### 请求示例
```json
POST /api/courses
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "title": "篮球基础技能训练",
  "category": "skill",
  "description": "本课程将教授篮球的基本技能",
  "cover_url": "http://127.0.0.1:8000/uploads/basketball.jpg",
  "is_public": true
}
```

#### 响应示例
```json
{
  "code": 201,
  "data": {
    "id": 1,
    "title": "篮球基础技能训练",
    "category": "skill",
    "description": "本课程将教授篮球的基本技能",
    "cover_url": "http://127.0.0.1:8000/uploads/basketball.jpg",
    "is_public": true,
    "teacher_id": 50,
    "created_at": "2026-02-27T10:00:00"
  },
  "msg": "创建成功"
}
```

#### 错误响应
```json
{
  "code": 400,
  "data": null,
  "msg": "课程名称不能为空"
}
```

---

### 4. 加入课程

#### 接口信息
- **路径**: `/api/courses/{id}/enroll` 或 `/courses/{id}/enroll`
- **方法**: POST
- **权限**: 需要学生权限

#### 路径参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | Integer | 是 | 课程ID |

#### 请求示例
```
POST /api/courses/1/enroll
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{}
```

#### 响应示例
```json
{
  "code": 200,
  "data": {
    "success": true
  },
  "msg": "加入成功"
}
```

#### 错误响应
```json
{
  "code": 400,
  "data": null,
  "msg": "已加入过此课程"
}
```

---

## 文件上传接口

### 1. 上传文件

#### 接口信息
- **路径**: `/api/upload` 或 `/upload/file`
- **方法**: POST
- **权限**: 需要登录
- **Content-Type**: multipart/form-data

#### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| file | File | 是 | 上传的文件 |

#### 文件限制

##### 图片文件
- 支持格式: jpg, jpeg, png
- 最大大小: 5MB
- Content-Type: image/jpeg, image/png

##### 视频文件
- 支持格式: mp4
- 最大大小: 100MB
- Content-Type: video/mp4

#### 请求示例（curl）
```bash
curl -X POST http://127.0.0.1:8000/upload/file \
  -H "Authorization: Bearer {token}" \
  -F "file=@/path/to/image.jpg"
```

#### 响应示例
```json
{
  "code": 200,
  "data": {
    "url": "/uploads/202602/abc123.jpg",
    "type": "image",
    "size": 102400,
    "original_filename": "image.jpg"
  },
  "msg": "上传成功"
}
```

#### 错误响应

##### 文件过大
```json
{
  "code": 413,
  "data": null,
  "msg": "图片文件大小不能超过5MB"
}
```

##### 格式不支持
```json
{
  "code": 415,
  "data": null,
  "msg": "不支持的文件类型，仅支持MP4视频和JPG/PNG图片"
}
```

---

## 参数校验规范

### 1. 课程名称
- 必填
- 类型: String
- 最小长度: 1
- 最大长度: 50
- 错误提示: "课程名称不能为空" / "课程名称不能超过50字符"

### 2. 课程类型
- 必填
- 类型: String
- 枚举值: skill, theory, fitness
- 错误提示: "请选择课程类型" / "课程类型不正确"

### 3. 课程简介
- 必填
- 类型: String
- 最小长度: 1
- 最大长度: 200
- 错误提示: "课程简介不能为空" / "课程简介不能超过200字符"

### 4. 课程封面
- 必填
- 类型: String (URL)
- 格式: 有效的URL
- 错误提示: "请上传课程封面" / "封面URL格式不正确"

### 5. 文件上传
- 必填
- 类型: File
- 大小限制: 图片≤5MB, 视频≤100MB
- 格式限制: 图片(jpg/png), 视频(mp4)
- 错误提示: "文件不能为空" / "文件大小超过限制" / "文件格式不支持"

---

## 错误码规范

### 业务错误码

| 错误码 | 说明 | 示例 |
|--------|------|------|
| 1001 | 参数验证失败 | 课程名称为空 |
| 1002 | 资源不存在 | 课程不存在 |
| 1003 | 资源已存在 | 已加入过此课程 |
| 1004 | 权限不足 | 只有教师可以创建课程 |
| 1005 | 操作失败 | 数据库操作失败 |
| 2001 | 文件上传失败 | 文件保存失败 |
| 2002 | 文件格式错误 | 不支持的文件格式 |
| 2003 | 文件过大 | 文件超过大小限制 |

### 错误响应示例
```json
{
  "code": 400,
  "data": {
    "error_code": 1001,
    "field": "title",
    "value": ""
  },
  "msg": "课程名称不能为空"
}
```

---

## 跨框架适配建议

### Java Spring Boot

```java
// 统一响应格式
@Data
public class ApiResponse<T> {
    private Integer code;
    private T data;
    private String msg;
    
    public static <T> ApiResponse<T> success(T data) {
        ApiResponse<T> response = new ApiResponse<>();
        response.setCode(200);
        response.setData(data);
        response.setMsg("操作成功");
        return response;
    }
    
    public static <T> ApiResponse<T> error(Integer code, String msg) {
        ApiResponse<T> response = new ApiResponse<>();
        response.setCode(code);
        response.setMsg(msg);
        return response;
    }
}

// 全局异常处理
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(ValidationException.class)
    public ApiResponse<?> handleValidation(ValidationException e) {
        return ApiResponse.error(400, e.getMessage());
    }
    
    @ExceptionHandler(ResourceNotFoundException.class)
    public ApiResponse<?> handleNotFound(ResourceNotFoundException e) {
        return ApiResponse.error(404, e.getMessage());
    }
}
```

### Node.js Express

```javascript
// 统一响应格式
class ApiResponse {
  static success(data, msg = '操作成功') {
    return {
      code: 200,
      data,
      msg
    };
  }
  
  static error(code, msg, data = null) {
    return {
      code,
      data,
      msg
    };
  }
}

// 全局错误处理中间件
app.use((err, req, res, next) => {
  if (err.name === 'ValidationError') {
    return res.status(400).json(
      ApiResponse.error(400, err.message)
    );
  }
  
  if (err.name === 'NotFoundError') {
    return res.status(404).json(
      ApiResponse.error(404, err.message)
    );
  }
  
  res.status(500).json(
    ApiResponse.error(500, '服务器错误')
  );
});
```

### Python FastAPI

```python
# 统一响应格式
from typing import Any, Optional
from pydantic import BaseModel

class ApiResponse(BaseModel):
    code: int
    data: Optional[Any] = None
    msg: str
    
    @classmethod
    def success(cls, data: Any = None, msg: str = "操作成功"):
        return cls(code=200, data=data, msg=msg)
    
    @classmethod
    def error(cls, code: int, msg: str, data: Any = None):
        return cls(code=code, data=data, msg=msg)

# 全局异常处理
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(ValueError)
async def validation_exception_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content=ApiResponse.error(400, str(exc)).dict()
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse.error(exc.status_code, exc.detail).dict()
    )
```

---

## 数据库设计建议

### 课程表 (courses)

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | Integer | 主键 | PRIMARY KEY, AUTO_INCREMENT |
| title | String(50) | 课程名称 | NOT NULL |
| description | String(200) | 课程简介 | NOT NULL |
| cover_url | String(255) | 封面URL | NOT NULL |
| category | String(20) | 课程类型 | NOT NULL |
| content | Text | 详细内容 | NULL |
| is_public | Boolean | 是否公开 | DEFAULT TRUE |
| teacher_id | Integer | 教师ID | NOT NULL, FOREIGN KEY |
| created_at | DateTime | 创建时间 | DEFAULT CURRENT_TIMESTAMP |
| updated_at | DateTime | 更新时间 | ON UPDATE CURRENT_TIMESTAMP |

### 选课表 (enrollments)

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | Integer | 主键 | PRIMARY KEY, AUTO_INCREMENT |
| student_id | Integer | 学生ID | NOT NULL, FOREIGN KEY |
| course_id | Integer | 课程ID | NOT NULL, FOREIGN KEY |
| status | String(20) | 状态 | DEFAULT 'active' |
| enrolled_at | DateTime | 加入时间 | DEFAULT CURRENT_TIMESTAMP |

### 课程内容表 (course_contents)

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | Integer | 主键 | PRIMARY KEY, AUTO_INCREMENT |
| course_id | Integer | 课程ID | NOT NULL, FOREIGN KEY |
| title | String(100) | 章节标题 | NOT NULL |
| content_type | String(20) | 内容类型 | NOT NULL |
| content_url | String(255) | 内容URL | NULL |
| duration | Integer | 时长(秒) | NULL |
| order | Integer | 排序 | DEFAULT 0 |
| created_at | DateTime | 创建时间 | DEFAULT CURRENT_TIMESTAMP |

---

## 安全建议

### 1. 认证授权
- 使用JWT Token进行身份验证
- Token有效期建议7天
- 刷新Token机制
- 权限分级（学生/教师/管理员）

### 2. 数据验证
- 前端验证 + 后端验证
- SQL注入防护
- XSS攻击防护
- CSRF防护

### 3. 文件上传安全
- 文件类型白名单
- 文件大小限制
- 文件名随机化
- 病毒扫描（生产环境）
- 存储路径隔离

### 4. 接口限流
- 单IP限流
- 单用户限流
- 接口级别限流
- 防止暴力破解

---

## 性能优化建议

### 1. 数据库优化
- 添加索引（teacher_id, category, created_at）
- 分页查询
- 避免N+1查询
- 使用连接池

### 2. 缓存策略
- Redis缓存热门课程
- 课程列表缓存（5分钟）
- 课程详情缓存（10分钟）
- 用户选课状态缓存

### 3. 文件存储
- 使用CDN加速
- 图片压缩
- 视频转码
- 分布式存储

### 4. 接口优化
- 响应压缩（gzip）
- 异步处理
- 批量操作
- 数据预加载

---

## 测试用例

### 1. 课程列表接口
- ✅ 正常获取列表
- ✅ 分页功能
- ✅ 类型筛选
- ✅ 空列表处理
- ✅ 未登录访问

### 2. 课程详情接口
- ✅ 正常获取详情
- ✅ 课程不存在
- ✅ 已加入状态
- ✅ 未加入状态
- ✅ 权限验证

### 3. 创建课程接口
- ✅ 正常创建
- ✅ 参数验证
- ✅ 权限验证
- ✅ 重复创建
- ✅ 数据库异常

### 4. 加入课程接口
- ✅ 正常加入
- ✅ 重复加入
- ✅ 课程不存在
- ✅ 权限验证
- ✅ 状态更新

### 5. 文件上传接口
- ✅ 正常上传
- ✅ 文件过大
- ✅ 格式错误
- ✅ 文件为空
- ✅ 存储失败

---

## 更新日志

### v1.0.0 (2026-02-27)
- 初始版本
- 定义课程相关接口
- 定义文件上传接口
- 统一响应格式
- 错误码规范
- 跨框架适配建议
