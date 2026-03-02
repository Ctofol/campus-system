# 课程发布功能使用指南

## 功能概述

课程发布功能支持教师创建和发布课程，包含完整的表单验证、文件上传、富文本编辑等功能。

## 页面文件

### 1. 基础版（推荐）
- 文件路径: `fronted/pages/courses/create.vue`
- 功能: 基础课程创建，包含必填字段和封面上传
- 适用场景: 快速创建课程

### 2. 增强版
- 文件路径: `fronted/pages/courses/create-enhanced.vue`
- 功能: 完整课程创建，包含富文本编辑器、图片插入、视频链接等
- 适用场景: 需要详细课程内容的场景

## 功能特性

### ✅ 表单字段

| 字段 | 类型 | 必填 | 验证规则 |
|------|------|------|----------|
| 课程名称 | 文本 | 是 | 最大50字符 |
| 课程类型 | 下拉选择 | 是 | 技能课/理论课/体能课 |
| 课程封面 | 图片上传 | 是 | jpg/png，≤2MB |
| 课程简介 | 多行文本 | 是 | 最大200字符 |
| 课程内容 | 富文本 | 否 | 支持图片、视频链接 |
| 参与人数上限 | 数字 | 否 | 1-1000 |
| 公开设置 | 开关 | 否 | 默认公开 |

### ✅ 文件上传功能

#### 封面图上传
- 支持格式: jpg, png
- 文件大小: ≤2MB
- 上传前验证: 自动检查文件大小和格式
- 错误提示: 详细的错误信息提示

#### 内容图片上传（增强版）
- 支持格式: jpg, png, gif, webp
- 文件大小: ≤5MB
- 自动插入: 上传成功后自动插入到编辑器

#### 视频链接插入（增强版）
- 支持输入视频URL
- 自动验证URL格式
- 插入到课程内容中

### ✅ 表单验证

#### 客户端验证
- 实时字符计数
- 提交前完整验证
- 友好的错误提示

#### 服务端验证
- 后端二次验证
- 防止恶意提交
- 详细的错误响应

### ✅ 错误处理

#### 上传错误
```javascript
// 文件过大
"封面图大小不能超过2MB，请重新选择"

// 格式错误
"文件格式不支持，请上传jpg或png格式"

// 网络错误
"网络连接失败，请检查网络"

// 服务器错误
"服务器拒绝接收文件"
```

#### 提交错误
```javascript
// 验证错误
"请输入课程名称"
"请选择课程类型"
"请上传课程封面"

// 权限错误
"没有权限创建课程"
"登录已过期，请重新登录"

// 网络错误
"网络连接失败，请检查网络"
```

## 使用流程

### 1. 进入发布页面
```javascript
// 从课程列表页跳转
uni.navigateTo({
  url: '/pages/courses/create'
});
```

### 2. 填写课程信息
1. 输入课程名称（必填）
2. 选择课程类型（必填）
3. 上传课程封面（必填）
4. 输入课程简介（必填）
5. 编辑课程内容（可选）
6. 设置参与人数上限（可选）
7. 选择是否公开（默认公开）

### 3. 上传封面图
1. 点击"上传封面"区域
2. 选择图片（相册或拍照）
3. 系统自动验证文件大小和格式
4. 上传成功后显示预览图

### 4. 编辑课程内容（增强版）
1. 在富文本编辑器中输入内容
2. 点击"图片"按钮插入图片
3. 点击"视频"按钮插入视频链接
4. 使用工具栏格式化文本（加粗、斜体等）

### 5. 提交发布
1. 点击"发布课程"按钮
2. 系统自动验证所有字段
3. 提交数据到服务器
4. 发布成功后自动跳转到课程列表

## 工具函数

### 通用上传工具
```javascript
import { uploadFile, chooseAndUploadImage, showUploadError } from '@/utils/upload.js';

// 方式1: 手动选择文件后上传
const result = await uploadFile(filePath, 'image');

// 方式2: 选择并上传（一步完成）
try {
  const result = await chooseAndUploadImage({
    count: 1,
    sizeType: ['compressed']
  });
  console.log('上传成功:', result.url);
} catch (error) {
  showUploadError(error);
}
```

### 请求封装
```javascript
import { createCourse } from '@/utils/request.js';

// 创建课程
const result = await createCourse({
  title: '课程名称',
  category: 'skill',
  description: '课程简介',
  cover_url: 'http://example.com/cover.jpg',
  is_public: true
});
```

## 配置说明

### 后端地址配置
文件: `fronted/utils/request.js`

```javascript
// H5浏览器测试
let baseUrl = 'http://127.0.0.1:8000';

// 真机测试（需配置防火墙）
// baseUrl = 'http://192.168.0.216:8000';

// 生产环境
// baseUrl = 'http://your-domain.com';
```

### 文件大小限制配置
文件: `fronted/utils/upload.js`

```javascript
const FILE_TYPES = {
  image: {
    maxSize: 5 * 1024 * 1024, // 5MB
  },
  video: {
    maxSize: 100 * 1024 * 1024, // 100MB
  }
};
```

## 常见问题

### Q1: 上传失败怎么办？
**A:** 检查以下几点：
1. 文件大小是否超过限制
2. 文件格式是否正确
3. 网络连接是否正常
4. 后端服务是否启动
5. Token是否有效

### Q2: 如何修改文件大小限制？
**A:** 修改 `fronted/utils/upload.js` 中的 `FILE_TYPES` 配置

### Q3: 如何添加新的文件类型？
**A:** 在 `FILE_TYPES` 中添加新的类型配置：
```javascript
const FILE_TYPES = {
  audio: {
    extensions: ['mp3', 'wav', 'ogg'],
    maxSize: 10 * 1024 * 1024,
    mimeTypes: ['audio/mpeg', 'audio/wav', 'audio/ogg']
  }
};
```

### Q4: 富文本编辑器不显示？
**A:** 确保：
1. 使用增强版页面 `create-enhanced.vue`
2. 页面已完全加载（onReady触发）
3. editor组件ID正确

### Q5: 如何自定义错误提示？
**A:** 修改错误处理函数：
```javascript
catch (error) {
  let errorMsg = '自定义错误信息';
  if (error.type === 'validation') {
    errorMsg = '文件验证失败';
  }
  uni.showModal({
    title: '提示',
    content: errorMsg
  });
}
```

## 测试建议

### 1. 功能测试
- [ ] 所有必填字段验证
- [ ] 文件大小限制验证
- [ ] 文件格式验证
- [ ] 上传成功流程
- [ ] 上传失败处理
- [ ] 提交成功流程
- [ ] 提交失败处理

### 2. 边界测试
- [ ] 最大字符数测试
- [ ] 最大文件大小测试
- [ ] 网络中断测试
- [ ] Token过期测试

### 3. 兼容性测试
- [ ] H5浏览器测试
- [ ] iOS真机测试
- [ ] Android真机测试
- [ ] 不同网络环境测试

## 性能优化

### 1. 图片压缩
```javascript
uni.chooseImage({
  sizeType: ['compressed'], // 压缩图片
  success: (res) => {
    // 上传压缩后的图片
  }
});
```

### 2. 上传进度显示
```javascript
uni.showLoading({ 
  title: '上传中...', 
  mask: true  // 防止用户重复操作
});
```

### 3. 防抖处理
```javascript
let submitting = false;

const handleSubmit = async () => {
  if (submitting) return;  // 防止重复提交
  submitting = true;
  
  try {
    await createCourse(data);
  } finally {
    submitting = false;
  }
};
```

## 安全建议

1. **前端验证**: 所有输入都要验证
2. **文件验证**: 上传前检查文件类型和大小
3. **Token管理**: 及时处理Token过期
4. **敏感信息**: 不在前端存储敏感信息
5. **HTTPS**: 生产环境使用HTTPS

## 更新日志

### v1.0.0 (2026-02-27)
- ✅ 基础课程创建功能
- ✅ 增强版富文本编辑
- ✅ 完整的文件上传功能
- ✅ 详细的错误处理
- ✅ 表单验证
- ✅ 通用工具函数
- ✅ 接口规范文档

## 技术支持

如有问题，请查看：
- API规范文档: `fronted/API_SPECIFICATION.md`
- 上传工具源码: `fronted/utils/upload.js`
- 请求封装源码: `fronted/utils/request.js`
