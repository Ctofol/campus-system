# 课程详情页 - 接口调用规范

## 概述

本文档定义了课程详情页所需的接口规范，兼容RESTful API标准，适用于Java/Node.js/Python等主流后端框架。

---

## 1. 获取课程详情接口

### 接口地址
```
GET /courses/{course_id}
```

### 请求参数

#### 路径参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| course_id | Integer | 是 | 课程ID |

#### 请求头
```
Authorization: Bearer {token}
```

### 请求示例
```
GET /courses/1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 响应格式

#### 成功响应 (200 OK)
```json
{
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
      "order": 1,
      "created_at": "2026-02-27T10:00:00"
    },
    {
      "id": 2,
      "title": "第二章：传球技巧",
      "content_type": "video",
      "content_url": "http://example.com/video2.mp4",
      "duration": 480,
      "order": 2,
      "created_at": "2026-02-27T10:00:00"
    }
  ]
}
```

#### 字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | Integer | 课程ID |
| title | String | 课程名称 |
| description | String | 课程简介 |
| cover_url | String | 课程封面URL |
| category | String | 课程类型（skill/theory/fitness） |
| is_public | Boolean | 是否公开 |
| teacher_id | Integer | 教师ID |
| teacher_name | String | 教师姓名（可选） |
| created_at | String | 创建时间（ISO 8601格式） |
| enrolled | Boolean | 当前用户是否已加入 |
| enrollment_count | Integer | 参与人数 |
| contents | Array | 课程章节列表 |

#### 章节对象字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | Integer | 章节ID |
| title | String | 章节标题 |
| content_type | String | 内容类型（video/document/text） |
| content_url | String | 内容URL |
| duration | Integer | 时长（秒） |
| order | Integer | 排序序号 |
| created_at | String | 创建时间 |

#### 错误响应

##### 404 Not Found - 课程不存在
```json
{
  "detail": "Course not found",
  "message": "课程不存在"
}
```

##### 401 Unauthorized - 未授权
```json
{
  "detail": "Not authenticated",
  "message": "请先登录"
}
```

##### 403 Forbidden - 无权限
```json
{
  "detail": "Not authorized",
  "message": "没有权限查看此课程"
}
```

---

## 2. 加入课程接口

### 接口地址
```
POST /courses/{course_id}/enroll
```

### 请求参数

#### 路径参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| course_id | Integer | 是 | 课程ID |

#### 请求头
```
Content-Type: application/json
Authorization: Bearer {token}
```

#### 请求体
无需请求体（空对象或不传）

### 请求示例
```
POST /courses/1/enroll
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{}
```

### 响应格式

#### 成功响应 (200 OK)
```json
{
  "success": true,
  "message": "加入成功"
}
```

#### 错误响应

##### 400 Bad Request - 已加入
```json
{
  "detail": "Already enrolled",
  "message": "已加入过此课程"
}
```

##### 404 Not Found - 课程不存在
```json
{
  "detail": "Course not found",
  "message": "课程不存在"
}
```

##### 403 Forbidden - 无权限
```json
{
  "detail": "Not authorized",
  "message": "没有权限加入此课程"
}
```

##### 401 Unauthorized - 未授权
```json
{
  "detail": "Not authenticated",
  "message": "请先登录"
}
```

---

## 3. 获取学习进度接口

### 接口地址
```
GET /courses/me/enrollments/{course_id}/progress
```

### 请求参数

#### 路径参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| course_id | Integer | 是 | 课程ID |

#### 请求头
```
Authorization: Bearer {token}
```

### 请求示例
```
GET /courses/me/enrollments/1/progress
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 响应格式

#### 成功响应 (200 OK)
```json
{
  "percent": 65
}
```

#### 字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| percent | Integer | 学习进度百分比（0-100） |

#### 错误响应

##### 404 Not Found - 未加入课程
```json
{
  "detail": "Not enrolled in this course",
  "message": "未加入此课程"
}
```

---

## 前端调用示例

### 1. 加载课程详情

```javascript
import { request } from '@/utils/request.js';

const loadCourseDetail = async (courseId) => {
  try {
    const res = await request({
      url: `/courses/${courseId}`,
      method: 'GET'
    });
    
    console.log('课程详情:', res);
    // 处理数据
    course.value = res;
    
    // 如果已加入，加载进度
    if (res.enrolled) {
      loadProgress(courseId);
    }
    
  } catch (error) {
    console.error('加载失败:', error);
    
    // 错误处理
    if (error.statusCode === 404) {
      uni.showToast({ title: '课程不存在', icon: 'none' });
    } else if (error.type === 'network') {
      uni.showToast({ title: '网络连接失败', icon: 'none' });
    } else {
      uni.showToast({ title: '加载失败', icon: 'none' });
    }
  }
};
```

### 2. 加入课程

```javascript
const joinCourse = async (courseId) => {
  try {
    await request({
      url: `/courses/${courseId}/enroll`,
      method: 'POST'
    });
    
    // 更新状态（无需刷新页面）
    course.value.enrolled = true;
    course.value.enrollment_count++;
    
    uni.showToast({ 
      title: '加入成功', 
      icon: 'success' 
    });
    
    // 加载学习进度
    loadProgress(courseId);
    
  } catch (error) {
    console.error('加入失败:', error);
    
    // 错误处理
    if (error.statusCode === 400) {
      uni.showToast({ title: '已加入过此课程', icon: 'none' });
    } else if (error.statusCode === 403) {
      uni.showToast({ title: '没有权限加入', icon: 'none' });
    } else {
      uni.showToast({ title: '加入失败', icon: 'none' });
    }
  }
};
```

### 3. 加载学习进度

```javascript
const loadProgress = async (courseId) => {
  try {
    const res = await request({
      url: `/courses/me/enrollments/${courseId}/progress`,
      method: 'GET'
    });
    
    courseProgress.value = res.percent || 0;
    
  } catch (error) {
    console.error('加载进度失败:', error);
    // 进度加载失败不影响主流程
  }
};
```

---

## 后端实现示例

### Java Spring Boot

```java
@RestController
@RequestMapping("/courses")
public class CourseController {
    
    @GetMapping("/{courseId}")
    public ResponseEntity<?> getCourseDetail(
        @PathVariable Long courseId,
        @AuthenticationPrincipal User currentUser
    ) {
        Course course = courseService.findById(courseId);
        if (course == null) {
            return ResponseEntity.status(404)
                .body(Map.of("detail", "Course not found"));
        }
        
        // 检查是否已加入
        boolean enrolled = enrollmentService
            .isEnrolled(currentUser.getId(), courseId);
        
        CourseDetailDTO dto = new CourseDetailDTO(course);
        dto.setEnrolled(enrolled);
        dto.setEnrollmentCount(
            enrollmentService.countByCourseId(courseId)
        );
        
        return ResponseEntity.ok(dto);
    }
    
    @PostMapping("/{courseId}/enroll")
    public ResponseEntity<?> enrollCourse(
        @PathVariable Long courseId,
        @AuthenticationPrincipal User currentUser
    ) {
        try {
            enrollmentService.enroll(currentUser.getId(), courseId);
            return ResponseEntity.ok(
                Map.of("success", true, "message", "加入成功")
            );
        } catch (AlreadyEnrolledException e) {
            return ResponseEntity.status(400)
                .body(Map.of("detail", "Already enrolled"));
        }
    }
}
```

### Node.js Express

```javascript
const express = require('express');
const router = express.Router();

// 获取课程详情
router.get('/courses/:courseId', authenticate, async (req, res) => {
  try {
    const courseId = req.params.courseId;
    const userId = req.user.id;
    
    const course = await Course.findById(courseId);
    if (!course) {
      return res.status(404).json({
        detail: 'Course not found'
      });
    }
    
    // 检查是否已加入
    const enrolled = await Enrollment.exists({
      student_id: userId,
      course_id: courseId,
      status: 'active'
    });
    
    // 统计参与人数
    const enrollmentCount = await Enrollment.countDocuments({
      course_id: courseId,
      status: 'active'
    });
    
    res.json({
      ...course.toJSON(),
      enrolled,
      enrollment_count: enrollmentCount
    });
    
  } catch (error) {
    res.status(500).json({ detail: error.message });
  }
});

// 加入课程
router.post('/courses/:courseId/enroll', authenticate, async (req, res) => {
  try {
    const courseId = req.params.courseId;
    const userId = req.user.id;
    
    // 检查是否已加入
    const existing = await Enrollment.findOne({
      student_id: userId,
      course_id: courseId
    });
    
    if (existing && existing.status === 'active') {
      return res.status(400).json({
        detail: 'Already enrolled'
      });
    }
    
    // 创建或更新选课记录
    await Enrollment.create({
      student_id: userId,
      course_id: courseId,
      status: 'active'
    });
    
    res.json({
      success: true,
      message: '加入成功'
    });
    
  } catch (error) {
    res.status(500).json({ detail: error.message });
  }
});

module.exports = router;
```

### Python FastAPI

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/courses", tags=["courses"])

@router.get("/{course_id}")
async def get_course_detail(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取课程详情"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # 检查是否已加入
    enrolled = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == course_id,
        Enrollment.status == "active"
    ).first() is not None
    
    # 统计参与人数
    enrollment_count = db.query(Enrollment).filter(
        Enrollment.course_id == course_id,
        Enrollment.status == "active"
    ).count()
    
    return {
        **course.__dict__,
        "enrolled": enrolled,
        "enrollment_count": enrollment_count
    }

@router.post("/{course_id}/enroll")
async def enroll_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """加入课程"""
    # 检查课程是否存在
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # 检查是否已加入
    existing = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == course_id
    ).first()
    
    if existing and existing.status == "active":
        raise HTTPException(status_code=400, detail="Already enrolled")
    
    # 创建选课记录
    enrollment = Enrollment(
        student_id=current_user.id,
        course_id=course_id,
        status="active"
    )
    db.add(enrollment)
    db.commit()
    
    return {"success": True, "message": "加入成功"}
```

---

## 状态码说明

| 状态码 | 说明 | 使用场景 |
|--------|------|----------|
| 200 | 成功 | 请求成功 |
| 400 | 请求错误 | 参数错误、已加入等 |
| 401 | 未授权 | Token失效或未登录 |
| 403 | 无权限 | 没有访问权限 |
| 404 | 不存在 | 资源不存在 |
| 500 | 服务器错误 | 服务器内部错误 |

---

## 测试用例

### 1. 正常流程测试
- 加载课程详情
- 验证数据完整性
- 加入课程
- 验证状态更新
- 加载学习进度

### 2. 异常流程测试
- 课程不存在（404）
- 未登录访问（401）
- 重复加入（400）
- 网络异常

### 3. 边界测试
- 课程无章节
- 进度为0%
- 进度为100%
- 参与人数为0

---

## 更新日志

### v1.0.0 (2026-02-27)
- 初始版本
- 定义课程详情接口
- 定义加入课程接口
- 定义学习进度接口
- 提供多语言后端示例
