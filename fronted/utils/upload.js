/**
 * 通用文件上传工具
 * 支持图片、视频等多种文件类型上传
 * 兼容主流后端框架（Java/Node.js/Python等）
 */

import { BASE_URL } from './request.js';

/**
 * 文件类型配置
 */
const FILE_TYPES = {
  image: {
    extensions: ['jpg', 'jpeg', 'png', 'gif', 'webp'],
    maxSize: 5 * 1024 * 1024, // 5MB
    mimeTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  },
  video: {
    extensions: ['mp4', 'mov', 'avi', 'wmv', 'flv', 'webm'],
    maxSize: 100 * 1024 * 1024, // 100MB
    mimeTypes: ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-ms-wmv', 'video/x-flv', 'video/webm']
  },
  document: {
    extensions: ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'],
    maxSize: 10 * 1024 * 1024, // 10MB
    mimeTypes: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
  }
};

/**
 * 获取文件扩展名
 * @param {String} filePath 文件路径
 * @returns {String} 扩展名（小写）
 */
function getFileExtension(filePath) {
  const parts = filePath.split('.');
  return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : '';
}

/**
 * 验证文件类型
 * @param {String} filePath 文件路径
 * @param {String} fileType 文件类型（image/video/document）
 * @returns {Object} { valid: Boolean, message: String }
 */
function validateFileType(filePath, fileType) {
  const ext = getFileExtension(filePath);
  const config = FILE_TYPES[fileType];
  
  if (!config) {
    return { valid: false, message: '不支持的文件类型' };
  }
  
  if (!config.extensions.includes(ext)) {
    return { 
      valid: false, 
      message: `只支持${config.extensions.join('、')}格式` 
    };
  }
  
  return { valid: true };
}

/**
 * 验证文件大小
 * @param {Number} fileSize 文件大小（字节）
 * @param {String} fileType 文件类型
 * @returns {Object} { valid: Boolean, message: String }
 */
function validateFileSize(fileSize, fileType) {
  const config = FILE_TYPES[fileType];
  
  if (!config) {
    return { valid: false, message: '不支持的文件类型' };
  }
  
  if (fileSize > config.maxSize) {
    const maxSizeMB = (config.maxSize / (1024 * 1024)).toFixed(0);
    return { 
      valid: false, 
      message: `文件大小不能超过${maxSizeMB}MB` 
    };
  }
  
  return { valid: true };
}

/**
 * 通用文件上传函数
 * @param {String} filePath 本地文件路径
 * @param {String} fileType 文件类型（image/video/document）
 * @param {Object} options 额外选项
 * @returns {Promise} 返回上传结果
 */
export function uploadFile(filePath, fileType = 'image', options = {}) {
  return new Promise((resolve, reject) => {
    // 1. 验证文件类型
    const typeValidation = validateFileType(filePath, fileType);
    if (!typeValidation.valid) {
      reject({ 
        type: 'validation', 
        message: typeValidation.message 
      });
      return;
    }
    
    // 2. 获取文件信息并验证大小
    uni.getFileInfo({
      filePath: filePath,
      success: (fileInfo) => {
        // 验证文件大小
        const sizeValidation = validateFileSize(fileInfo.size, fileType);
        if (!sizeValidation.valid) {
          reject({ 
            type: 'validation', 
            message: sizeValidation.message 
          });
          return;
        }
        
        // 3. 执行上传
        const token = uni.getStorageSync('token');
        
        uni.uploadFile({
          url: `${BASE_URL}/upload/file`,
          filePath: filePath,
          name: 'file', // 后端接收的字段名
          header: {
            'Authorization': token ? `Bearer ${token}` : ''
          },
          formData: {
            type: fileType,
            ...options.formData
          },
          success: (res) => {
            if (res.statusCode >= 200 && res.statusCode < 300) {
              try {
                const data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data;
                resolve(data);
              } catch (e) {
                console.error('Parse upload response error:', e);
                reject({ 
                  type: 'parse', 
                  message: '解析服务器响应失败',
                  raw: res.data
                });
              }
            } else if (res.statusCode === 401) {
              // Token失效
              uni.removeStorageSync('token');
              uni.removeStorageSync('userInfo');
              reject({ 
                type: 'auth', 
                statusCode: 401,
                message: '登录已过期，请重新登录' 
              });
              
              // 跳转登录页
              setTimeout(() => {
                uni.reLaunch({ url: '/pages/login/login' });
              }, 1500);
            } else if (res.statusCode === 413) {
              reject({ 
                type: 'server', 
                statusCode: 413,
                message: '文件过大，服务器拒绝接收' 
              });
            } else if (res.statusCode === 415) {
              reject({ 
                type: 'server', 
                statusCode: 415,
                message: '文件格式不支持' 
              });
            } else {
              // 其他服务器错误
              let errorMsg = '上传失败';
              try {
                const errorData = typeof res.data === 'string' ? JSON.parse(res.data) : res.data;
                errorMsg = errorData.detail || errorData.message || errorMsg;
              } catch (e) {
                // 解析失败，使用默认错误信息
              }
              
              reject({ 
                type: 'server', 
                statusCode: res.statusCode,
                message: errorMsg 
              });
            }
          },
          fail: (err) => {
            console.error('Upload fail:', err);
            reject({ 
              type: 'network', 
              message: '网络连接失败，请检查网络',
              error: err
            });
          }
        });
      },
      fail: (err) => {
        console.error('Get file info fail:', err);
        reject({ 
          type: 'system', 
          message: '获取文件信息失败',
          error: err
        });
      }
    });
  });
}

/**
 * 批量上传文件
 * @param {Array} filePaths 文件路径数组
 * @param {String} fileType 文件类型
 * @param {Object} options 额外选项
 * @returns {Promise} 返回所有上传结果
 */
export function uploadMultipleFiles(filePaths, fileType = 'image', options = {}) {
  const uploadPromises = filePaths.map(filePath => uploadFile(filePath, fileType, options));
  return Promise.all(uploadPromises);
}

/**
 * 选择并上传图片
 * @param {Object} options 选项
 * @returns {Promise} 返回上传结果
 */
export function chooseAndUploadImage(options = {}) {
  return new Promise((resolve, reject) => {
    uni.chooseImage({
      count: options.count || 1,
      sizeType: options.sizeType || ['compressed'],
      sourceType: options.sourceType || ['album', 'camera'],
      success: async (res) => {
        try {
          if (res.tempFilePaths.length === 1) {
            // 单张图片
            const result = await uploadFile(res.tempFilePaths[0], 'image', options);
            resolve(result);
          } else {
            // 多张图片
            const results = await uploadMultipleFiles(res.tempFilePaths, 'image', options);
            resolve(results);
          }
        } catch (e) {
          reject(e);
        }
      },
      fail: (err) => {
        reject({ 
          type: 'cancel', 
          message: '取消选择图片',
          error: err
        });
      }
    });
  });
}

/**
 * 选择并上传视频
 * @param {Object} options 选项
 * @returns {Promise} 返回上传结果
 */
export function chooseAndUploadVideo(options = {}) {
  return new Promise((resolve, reject) => {
    uni.chooseVideo({
      sourceType: options.sourceType || ['album', 'camera'],
      maxDuration: options.maxDuration || 60,
      camera: options.camera || 'back',
      success: async (res) => {
        try {
          const result = await uploadFile(res.tempFilePath, 'video', options);
          resolve(result);
        } catch (e) {
          reject(e);
        }
      },
      fail: (err) => {
        reject({ 
          type: 'cancel', 
          message: '取消选择视频',
          error: err
        });
      }
    });
  });
}

/**
 * 显示上传错误提示
 * @param {Object} error 错误对象
 */
export function showUploadError(error) {
  let title = '上传失败';
  let content = error.message || '未知错误';
  
  if (error.type === 'validation') {
    title = '文件验证失败';
  } else if (error.type === 'network') {
    title = '网络错误';
  } else if (error.type === 'auth') {
    title = '认证失败';
    uni.showToast({ title: content, icon: 'none', duration: 2000 });
    return;
  }
  
  uni.showModal({
    title: title,
    content: content,
    showCancel: false
  });
}

export default {
  uploadFile,
  uploadMultipleFiles,
  chooseAndUploadImage,
  chooseAndUploadVideo,
  showUploadError,
  FILE_TYPES
};
