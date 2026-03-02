# 灵析运动App - 接口规范文档

## 通用规范

### 1. 请求格式

#### 1.1 请求头（Headers）
```
Content-Type: application/json
Authorization: Bearer {token}
```

#### 1.2 请求方法
- GET: 查询数据
- POST: 创建数据
- PUT: 更新数据
- DELETE: 删除数据

### 2. 响应格式

#### 2.1 成功响应
```json
{
  "data": {},
  "message": "操作成功"
}
```

#### 2.2 错误响应
```json
{
  "detail": "错误描述",
  "message": "错误信息"
}
```

#### 2.3 HTTP状态码
- 200: 成功
- 201: 创建成功
- 400: 请求参数错误
- 401: 未授权（Token失效）
- 403: 无权限
- 404: 资源不存在
- 413: 文件过大
- 415: 不支持的文件格式
- 500: 服务器错误

---

## 文件上传接口

### 接口地址
```
POST /upload/file
```

### 请求格式
- Content-Type: `multipart/form-data`
- 请求方式: `uni.uploadFile` 或 `FormData`

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| file | File | 是 | 上传的文件（字段名必须为"file"） |
| type | String | 否 | 文件类型（image/video/document） |

### 请求示例（uni-app）
```javascript
uni.uploadFile({
  url: 'http://127.0.0.1:8000/upload/file',
  filePath: tempFilePath,
  name: 'file',  // 后端接收的字段名
  header: {
    'Authorization': 'Bearer {token}'
  },
  formData: {
    type: 'image'
  },
  success: (res) => {
    const data = JSON.parse(res.data);
    console.log('上传成功:', data.url);
  }
});
```

### 请求示例（JavaScript/Axios）
```javascript
const formData = new FormData();
formData.append('file', fileObject);
formData.append('type', 'image');

axios.post('http://127.0.0.1:8000/upload/file', formData, {
  headers: {
    'Content-Type': 'multipart/form-data',
    'Authorization': 'Bearer {token}'
  }
});
```

### 响应示例
```json
{
  "url": "http://127.0.0.1:8000/uploads/abc123.jpg",
  "filename": "abc123.jpg",
  "size": 102400,
  "type": "image"
}
```

### 文件限制

#### 图片文件
- 支持格式: jpg, jpeg, png, gif, webp
- 最大大小: 5MB
- 推荐尺寸: 1920x1080

#### 视频文件
- 支持格式: mp4, mov, avi, wmv, flv, webm
- 最大大小: 100MB
- 推荐格式: mp4

#### 文档文件
- 支持格式: pdf, doc, docx, xls, xlsx, ppt, pptx
- 最大大小: 10MB

---

## 课程管理接口

### 1. 创建课程

#### 接口地址
```
POST /courses/
```

#### 请求头
```
Content-Type: application/json
Authorization: Bearer {token}
```

#### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| title | String | 是 | 课程名称（最大50字符） |
| category | String | 是 | 课程类型（skill/theory/fitness） |
| description | String | 是 | 课程简介（最大200字符） |
| cover_url | String | 是 | 课程封面URL |
| content | String | 否 | 课程内容（富文本HTML） |
| max_enrollment | Integer | 否 | 参与人数上限（1-1000） |
| is_public | Boolean | 否 | 是否公开（默认true） |

#### 请求示例
```json
{
  "title": "篮球基础技能训练",
  "category": "skill",
  "description": "本课程将教授篮球的基本技能，包括运球、传球、投篮等",
  "cover_url": "http://127.0.0.1:8000/uploads/basketball.jpg",
  "content": "<p>课程内容详情...</p>",
  "max_enrollment": 30,
  "is_public": true
}
```

#### 响应示例
```json
{
  "id": 1,
  "title": "篮球基础技能训练",
  "category": "skill",
  "description": "本课程将教授篮球的基本技能",
  "cover_url": "http://127.0.0.1:8000/uploads/basketball.jpg",
  "is_public": true,
  "teacher_id": 50,
  "created_at": "2026-02-27T10:00:00"
}
```

### 2. 获取课程列表

#### 接口地址
```
GET /courses/
```

#### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | Integer | 否 | 页码（默认1） |
| size | Integer | 否 | 每页数量（默认20） |
| category | String | 否 | 课程类型筛选 |
| teacher_id | Integer | 否 | 教师ID筛选 |

#### 请求示例
```
GET /courses/?page=1&size=20&category=skill
```

#### 响应示例
```json
{
  "items": [
    {
      "id": 1,
      "title": "篮球基础技能训练",
      "category": "skill",
      "description": "本课程将教授篮球的基本技能",
      "cover_url": "http://127.0.0.1:8000/uploads/basketball.jpg",
      "is_public": true,
      "teacher_id": 50,
      "created_at": "2026-02-27T10:00:00"
    }
  ],
  "total": 10,
  "page": 1,
  "size": 20
}
```

### 3. 获取课程详情

#### 接口地址
```
GET /courses/{course_id}
```

#### 响应示例
```json
{
  "id": 1,
  "title": "篮球基础技能训练",
  "category": "skill",
  "description": "本课程将教授篮球的基本技能",
  "cover_url": "http://127.0.0.1:8000/uploads/basketball.jpg",
  "is_public": true,
  "teacher_id": 50,
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
}
```

### 4. 更新课程

#### 接口地址
```
PUT /courses/{course_id}
```

#### 请求参数
与创建课程相同

### 5. 删除课程

#### 接口地址
```
DELETE /courses/{course_id}
```

#### 响应示例
```json
{
  "success": true
}
```

---

## 后端适配指南

### Java Spring Boot 示例

```java
@RestController
@RequestMapping("/upload")
public class UploadController {
    
    @PostMapping("/file")
    public ResponseEntity<?> uploadFile(
        @RequestParam("file") MultipartFile file,
        @RequestParam(required = false) String type
    ) {
        // 处理文件上传
        String url = fileService.save(file);
        
        Map<String, Object> response = new HashMap<>();
        response.put("url", url);
        response.put("filename", file.getOriginalFilename());
        response.put("size", file.getSize());
        response.put("type", type);
        
        return ResponseEntity.ok(response);
    }
}
```

### Node.js Express 示例

```javascript
const multer = require('multer');
const upload = multer({ dest: 'uploads/' });

app.post('/upload/file', upload.single('file'), (req, res) => {
  const file = req.file;
  const type = req.body.type;
  
  res.json({
    url: `http://localhost:8000/uploads/${file.filename}`,
    filename: file.filename,
    size: file.size,
    type: type
  });
});
```

### Python FastAPI 示例

```python
from fastapi import FastAPI, File, UploadFile, Form

@app.post("/upload/file")
async def upload_file(
    file: UploadFile = File(...),
    type: str = Form(None)
):
    # 保存文件
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    return {
        "url": f"http://localhost:8000/uploads/{file.filename}",
        "filename": file.filename,
        "size": file.size,
        "type": type
    }
```

---

## 错误处理最佳实践

### 前端错误处理示例

```javascript
try {
  const result = await uploadFile(filePath, 'image');
  console.log('上传成功:', result.url);
} catch (error) {
  // 根据错误类型显示不同提示
  if (error.type === 'validation') {
    uni.showToast({ 
      title: error.message, 
      icon: 'none' 
    });
  } else if (error.type === 'network') {
    uni.showModal({
      title: '网络错误',
      content: '请检查网络连接后重试',
      showCancel: false
    });
  } else if (error.type === 'auth') {
    // 跳转登录页
    uni.reLaunch({ url: '/pages/login/login' });
  } else {
    uni.showModal({
      title: '上传失败',
      content: error.message || '未知错误',
      showCancel: false
    });
  }
}
```

### 后端错误响应示例

```json
{
  "detail": "文件格式不支持",
  "message": "只支持jpg、png格式的图片",
  "code": "INVALID_FILE_FORMAT"
}
```

---

## 安全建议

1. **文件验证**: 后端必须验证文件类型和大小
2. **文件重命名**: 使用UUID或时间戳重命名文件，避免文件名冲突
3. **路径安全**: 防止路径遍历攻击
4. **病毒扫描**: 对上传文件进行病毒扫描
5. **访问控制**: 验证用户权限
6. **HTTPS**: 生产环境使用HTTPS传输

---

## 性能优化建议

1. **图片压缩**: 前端上传前压缩图片
2. **CDN加速**: 使用CDN存储和分发文件
3. **分片上传**: 大文件使用分片上传
4. **断点续传**: 支持上传中断后继续上传
5. **并发控制**: 限制同时上传的文件数量

---

## 测试用例

### 1. 正常上传测试
- 上传符合规范的图片文件
- 验证返回的URL可访问

### 2. 文件大小测试
- 上传超过限制的文件
- 验证返回413错误

### 3. 文件格式测试
- 上传不支持的文件格式
- 验证返回415错误

### 4. 认证测试
- 不带Token上传
- 验证返回401错误

### 5. 网络异常测试
- 模拟网络中断
- 验证错误提示正确

---

## 更新日志

### v1.0.0 (2026-02-27)
- 初始版本
- 支持图片、视频、文档上传
- 完整的错误处理机制
- 兼容主流后端框架
