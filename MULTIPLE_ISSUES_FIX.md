# 多个问题修复说明

## 问题1：体能测试只能上传照片，不能上传视频

### 问题分析
代码中已经实现了视频上传功能，使用 `uni.chooseVideo` API。但在微信小程序中可能遇到以下情况：
1. 微信开发者工具模拟器不完全支持视频选择
2. 需要在真机上测试
3. 如果视频选择失败，会自动降级到图片选择

### 代码逻辑
```javascript
const chooseFromGallery = () => {
  uni.chooseVideo({
    sourceType: ['album'],
    maxDuration: 300, // 5分钟
    success: (res) => {
      validateAndUpload(res.tempFilePath, 'video');
    },
    fail: () => {
      // 如果选择视频失败，尝试选择图片
      uni.chooseImage({
        count: 1,
        sourceType: ['album'],
        success: (res) => {
          validateAndUpload(res.tempFilePaths[0], 'image');
        }
      });
    }
  });
};
```

### 解决方案
1. ✅ 代码已支持视频上传
2. ⚠️ 需要在真机上测试（模拟器可能不支持）
3. ✅ 有降级机制，如果视频失败会选择图片

### 测试建议
- 在微信开发者工具中点击"预览"
- 使用手机扫码在真机上测试
- 真机上应该可以正常选择视频

---

## 问题2：跑步的步数没有变化

### 问题分析
步数统计使用加速度传感器（Accelerometer）实现，通过检测手机的加速度变化来计算步数。

### 代码逻辑
```javascript
const startStepCount = () => {
  uni.startAccelerometer({
    interval: 'game', // 20ms频率
    success: () => {
      console.log('Accelerometer started');
    },
    fail: (err) => {
      console.error('Start Accelerometer failed:', err);
    }
  });
  
  accelerometerCallback = (res) => {
    let acceleration = Math.sqrt(res.x*res.x + res.y*res.y + res.z*res.z);
    
    // 检测步数
    if (!isStepActive && acceleration > STEP_THRESHOLD_UP) {
      if (now - lastStepTime > MIN_STEP_INTERVAL) {
        stepCount.value += 1;
        lastStepTime = now;
        isStepActive = true;
      }
    }
  };
  
  uni.onAccelerometerChange(accelerometerCallback);
};
```

### 问题原因
1. **微信开发者工具模拟器不支持加速度传感器**
2. 模拟器中步数永远是0
3. 必须在真机上测试

### 解决方案
- ✅ 代码逻辑正确
- ⚠️ 必须在真机上测试
- ✅ 真机上跑步时会正常计步

### 测试步骤
1. 在微信开发者工具中点击"预览"
2. 使用手机扫码
3. 在真机上点击"开始跑步"
4. 拿着手机走动或跑步
5. 观察步数是否增加

### 调试方法
在真机上查看Console日志：
```javascript
console.log('Accelerometer started'); // 应该看到这个日志
console.log('Step count:', stepCount.value); // 查看步数
```

---

## 问题3：课程列表显示的还是旧数据

### 问题分析
课程列表页面硬编码了 `enrollment_count: 0`，并且后端接口没有返回 `enrolled` 和 `enrollment_count` 字段。

### 修复内容

#### 前端修复（fronted/pages/tab/learn.vue）
```javascript
// 修复前
const newCourses = res.items.map(c => ({
  ...c,
  category_label: getCategoryLabel(c.category),
  enrollment_count: 0 // ❌ 硬编码为0
}));

// 修复后
const newCourses = res.items.map(c => ({
  ...c,
  category_label: getCategoryLabel(c.category)
  // ✅ 保留后端返回的 enrollment_count 和 enrolled 字段
}));
```

#### 后端修复（backend/app/routers/courses.py）
```python
# 修复前
return {
    "items": courses,  # ❌ 直接返回Course对象，没有enrolled和enrollment_count
    "total": total,
    "page": page,
    "size": size
}

# 修复后
items = []
for course in courses:
    # 检查是否已选课
    enrolled = False
    if current_user and current_user.role == "student":
        enrollment = db.query(models.Enrollment).filter(
            models.Enrollment.student_id == current_user.id,
            models.Enrollment.course_id == course.id,
            models.Enrollment.status == "active"
        ).first()
        enrolled = enrollment is not None
    
    # 统计选课人数
    enrollment_count = db.query(models.Enrollment).filter(
        models.Enrollment.course_id == course.id,
        models.Enrollment.status == "active"
    ).count()
    
    # 构造课程数据
    course_dict = {
        "id": course.id,
        "title": course.title,
        # ...
        "enrolled": enrolled,  # ✅ 添加是否已加入
        "enrollment_count": enrollment_count  # ✅ 添加参与人数
    }
    items.append(course_dict)

return {
    "items": items,  # ✅ 返回包含完整信息的字典列表
    "total": total,
    "page": page,
    "size": size
}
```

### 修复效果
- ✅ 课程列表显示正确的参与人数
- ✅ 已加入的课程显示"已加入"标签
- ✅ 未加入的课程显示"加入课程"标签
- ✅ 加入课程后，列表自动更新状态

---

## 修改的文件

### 前端
1. `fronted/pages/tab/learn.vue` - 移除硬编码的 enrollment_count

### 后端
1. `backend/app/routers/courses.py` - 课程列表接口返回 enrolled 和 enrollment_count

---

## 测试验证

### 1. 体能测试视频上传
- [ ] 在真机上测试视频上传
- [ ] 验证视频可以正常选择和上传
- [ ] 验证降级机制（如果视频失败，可以选择图片）

### 2. 跑步步数统计
- [ ] 在真机上开始跑步
- [ ] 拿着手机走动或跑步
- [ ] 验证步数是否正常增加
- [ ] 验证步数显示在界面上

### 3. 课程列表数据
- [ ] 重新编译并运行
- [ ] 查看课程列表
- [ ] 验证参与人数显示正确
- [ ] 加入一个课程
- [ ] 返回列表，验证显示"已加入"
- [ ] 验证参与人数+1

---

## 重要提示

### 关于模拟器的限制
微信开发者工具的模拟器有很多限制：
1. ❌ 不支持加速度传感器（步数永远是0）
2. ❌ 视频选择可能不完全支持
3. ❌ 定位精度很低
4. ❌ 某些硬件API不可用

### 真机测试的重要性
以下功能必须在真机上测试：
- ✅ 步数统计
- ✅ 视频上传
- ✅ 精确定位
- ✅ 加速度传感器
- ✅ 陀螺仪
- ✅ 指南针

### 如何进行真机测试
1. 在微信开发者工具中点击"预览"
2. 使用手机微信扫描二维码
3. 在真机上测试所有功能
4. 查看真机上的Console日志（摇一摇手机打开调试）

---

## 相关文件
- `fronted/pages/test/test.vue` - 体能测试页面（视频上传）
- `fronted/components/student-run/student-run.vue` - 跑步页面（步数统计）
- `fronted/pages/tab/learn.vue` - 课程列表页面（前端修复）
- `backend/app/routers/courses.py` - 课程接口（后端修复）
