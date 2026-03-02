# 真机测试问题修复

## 修复内容总结

### 1. 视频上传功能优化

#### 问题
真机上无法选择或拍摄视频

#### 修复内容

**A. 添加权限配置（manifest.json）**
```json
"permission" : {
  "scope.camera" : {
    "desc" : "需要使用您的摄像头进行拍摄体测视频"
  },
  "scope.album" : {
    "desc" : "需要访问您的相册以选择照片或视频"
  }
},
"requiredPrivateInfos" : [
  "chooseImage",
  "chooseVideo",
  "chooseMedia"  // 新增：微信小程序推荐使用的API
]
```

**B. 优化上传逻辑（pages/test/test.vue）**
- 使用 `chooseMedia` API（微信小程序推荐）
- 分离视频和图片选择
- 添加详细的错误日志
- 提供4个选项：
  1. 从相册选择视频
  2. 从相册选择图片
  3. 拍摄视频
  4. 拍摄照片

```javascript
const chooseVideoFromGallery = () => {
  // #ifdef MP-WEIXIN
  uni.chooseMedia({
    count: 1,
    mediaType: ['video'],
    sourceType: ['album'],
    maxDuration: 300,
    success: (res) => {
      console.log('Choose video success:', res);
      const media = res.tempFiles[0];
      validateAndUpload(media.tempFilePath, 'video');
    },
    fail: (err) => {
      console.error('Choose video failed:', err);
      uni.showToast({
        title: '选择视频失败',
        icon: 'none'
      });
    }
  });
  // #endif
};
```

### 2. 步数统计功能优化

#### 问题
真机上步数不增加

#### 修复内容

**A. 添加权限配置（manifest.json）**
```json
"requiredPrivateInfos" : [
  "startAccelerometer"  // 新增：加速度传感器权限
]
```

**B. 优化步数统计逻辑（components/student-run/student-run.vue）**
- 添加详细的启动日志
- 添加启动成功/失败提示
- 添加步数变化日志
- 优化错误处理

```javascript
const startStepCount = () => {
  console.log('=== 开始启动步数统计 ===');
  
  uni.startAccelerometer({
    interval: 'game',
    success: () => {
      console.log('✅ 加速度传感器启动成功');
      uni.showToast({
        title: '步数统计已启动',
        icon: 'none',
        duration: 1500
      });
    },
    fail: (err) => {
      console.error('❌ 加速度传感器启动失败:', err);
      uni.showModal({
        title: '步数统计启动失败',
        content: '无法启动加速度传感器，步数将无法统计。错误：' + JSON.stringify(err),
        showCancel: false
      });
    }
  });
  
  accelerometerCallback = (res) => {
    // ... 计步逻辑
    if (!isStepActive && acceleration > STEP_THRESHOLD_UP) {
      if (now - lastStepTime > MIN_STEP_INTERVAL) {
        stepCount.value += 1;
        console.log('👣 步数+1，当前步数:', stepCount.value, '加速度:', acceleration.toFixed(2));
        // ...
      }
    }
  };
};
```

### 3. 课程列表数据修复

#### 问题
课程列表显示的参与人数和加入状态不正确

#### 修复内容
- ✅ 前端：移除硬编码的 `enrollment_count: 0`
- ✅ 后端：返回正确的 `enrolled` 和 `enrollment_count` 字段

---

## 测试步骤

### 1. 重新编译
1. 停止当前运行
2. 删除 `fronted/unpackage` 文件夹
3. 重新运行到微信开发者工具
4. 点击"预览"，用手机扫码

### 2. 测试视频上传
1. 进入体能测试页面
2. 点击"重新上传"
3. 应该看到4个选项：
   - 从相册选择视频
   - 从相册选择图片
   - 拍摄视频
   - 拍摄照片
4. 尝试每个选项
5. 查看Console日志，确认是否有错误

### 3. 测试步数统计
1. 进入跑步页面
2. 点击"开始跑步"
3. 应该看到提示"步数统计已启动"
4. 拿着手机走动或跑步
5. 观察步数是否增加
6. 打开Console查看日志：
   - 应该看到"✅ 加速度传感器启动成功"
   - 走动时应该看到"👣 步数+1，当前步数: X"

### 4. 测试课程列表
1. 进入课程页面
2. 查看参与人数是否正确
3. 加入一个课程
4. 返回列表，查看是否显示"已加入"

---

## 调试方法

### 查看真机Console日志

**方法1：微信开发者工具**
1. 手机和电脑连接同一WiFi
2. 在微信开发者工具中选择"真机调试"
3. 扫码后可以在工具中看到真机日志

**方法2：手机端vConsole**
1. 在手机上摇一摇
2. 会弹出调试面板
3. 可以查看Console日志

### 关键日志

**视频上传**
```
Choose video success: {...}  // 成功
Choose video failed: {...}   // 失败
```

**步数统计**
```
=== 开始启动步数统计 ===
✅ 加速度传感器启动成功
👣 步数+1，当前步数: 1 加速度: 1.35
👣 步数+1，当前步数: 2 加速度: 1.42
```

---

## 可能的问题和解决方案

### 问题1：视频上传仍然失败

**可能原因**：
1. 微信小程序权限未授予
2. 手机系统权限未开启

**解决方案**：
1. 删除小程序，重新扫码进入
2. 在手机设置中检查微信的相机和相册权限
3. 查看Console中的具体错误信息

### 问题2：步数仍然不增加

**可能原因**：
1. 加速度传感器启动失败
2. 手机不支持加速度传感器（极少见）
3. 阈值设置不合适

**解决方案**：
1. 查看是否有"✅ 加速度传感器启动成功"提示
2. 如果启动失败，查看错误信息
3. 尝试更大幅度的走动或跑步
4. 查看Console中的加速度值

### 问题3：课程列表数据仍然不对

**可能原因**：
1. 后端未重启
2. 缓存问题

**解决方案**：
1. 确认后端已重启
2. 下拉刷新课程列表
3. 重新编译前端

---

## 修改的文件

### 前端
1. `fronted/manifest.json` - 添加权限配置
2. `fronted/pages/test/test.vue` - 优化视频上传逻辑
3. `fronted/components/student-run/student-run.vue` - 优化步数统计
4. `fronted/pages/tab/learn.vue` - 修复课程列表数据

### 后端
1. `backend/app/routers/courses.py` - 修复课程列表接口

---

## 注意事项

1. **必须重新编译**：修改manifest.json后必须重新编译
2. **必须重新扫码**：权限变更后建议删除小程序重新进入
3. **查看日志**：遇到问题先查看Console日志
4. **真机调试**：使用真机调试模式可以实时查看日志

---

## 如果还是不行

请提供以下信息：
1. Console中的完整错误日志
2. 手机型号和微信版本
3. 具体的错误提示截图
4. 是否看到权限申请弹窗
