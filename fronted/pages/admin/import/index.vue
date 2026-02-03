<template>
  <view class="container">
    <view class="section">
      <view class="header">批量导入学生 (含模板下载)</view>
      <view class="desc">请上传Excel文件，包含列：姓名, 手机号, 密码, 学号, 所属班级名称</view>
      <view class="actions">
        <button type="primary" size="mini" class="btn" @click="chooseFile('student')">选择文件并导入</button>
        <button type="default" size="mini" class="btn" @click="downloadTemplate('student')">下载模板</button>
      </view>
    </view>
    
    <view class="section">
      <view class="header">批量导入教师 (含模板下载)</view>
      <view class="desc">请上传Excel文件，包含列：姓名, 手机号, 密码, 工号</view>
      <view class="actions">
        <button type="primary" size="mini" class="btn" @click="chooseFile('teacher')">选择文件并导入</button>
        <button type="default" size="mini" class="btn" @click="downloadTemplate('teacher')">下载模板</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { BASE_URL } from '@/utils/request.js';

const chooseFile = (type) => {
  // #ifdef H5
  uni.chooseFile({
    count: 1,
    extension: ['.xls', '.xlsx'],
    success: (res) => {
      if (res.tempFilePaths && res.tempFilePaths.length > 0) {
        uploadFile(res.tempFilePaths[0], type);
      }
    }
  });
  // #endif
  
  // #ifndef H5
  uni.showToast({ title: '请在Web端使用导入功能', icon: 'none' });
  // #endif
};

const uploadFile = (filePath, type) => {
  const token = uni.getStorageSync('token');
  const url = type === 'student' ? '/admin/import/students' : '/admin/import/teachers';
  
  uni.showLoading({ title: '导入中...' });
  
  uni.uploadFile({
    url: BASE_URL + url,
    filePath: filePath,
    name: 'file',
    header: {
      'Authorization': `Bearer ${token}`
    },
    success: (uploadFileRes) => {
      uni.hideLoading();
      try {
        const data = JSON.parse(uploadFileRes.data);
        if (uploadFileRes.statusCode === 200) {
           let msg = `成功: ${data.success}, 失败: ${data.failed}`;
           if (data.errors && data.errors.length > 0) {
             msg += '\n\n失败详情:\n';
             data.errors.forEach(err => {
               msg += `行${err.row} (${err.name}): ${err.error}\n`;
             });
           }
           uni.showModal({
             title: '导入完成',
             content: msg,
             showCancel: false
           });
        } else {
           uni.showModal({
             title: '导入失败',
             content: data.detail || '未知错误',
             showCancel: false
           });
        }
      } catch (e) {
        uni.showToast({ title: '解析响应失败', icon: 'none' });
      }
    },
    fail: (err) => {
      uni.hideLoading();
      uni.showToast({ title: '上传失败', icon: 'none' });
      console.error(err);
    }
  });
};

const downloadTemplate = (type) => {
    const token = uni.getStorageSync('token');
    const url = BASE_URL + (type === 'student' ? '/admin/import/template/students' : '/admin/import/template/teachers');
    
    uni.showLoading({ title: '准备下载...' });
    
    uni.downloadFile({
        url: url,
        header: {
            'Authorization': `Bearer ${token}`
        },
        success: (res) => {
            uni.hideLoading();
            if (res.statusCode === 200) {
                // #ifdef H5
                const a = document.createElement('a');
                a.href = res.tempFilePath;
                a.download = type === 'student' ? '学生导入模板.xlsx' : '教师导入模板.xlsx';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                // #endif
                
                // #ifndef H5
                uni.saveFile({
                    tempFilePath: res.tempFilePath,
                    success: function (saveRes) {
                        uni.showToast({ title: '保存成功', icon: 'success' });
                        setTimeout(() => {
                             uni.openDocument({
                                filePath: saveRes.savedFilePath,
                                showMenu: true
                            });
                        }, 1000);
                    },
                    fail: () => {
                        uni.showToast({ title: '保存失败', icon: 'none' });
                    }
                });
                // #endif
            } else {
                uni.showToast({ title: '下载失败: ' + res.statusCode, icon: 'none' });
            }
        },
        fail: (err) => {
            uni.hideLoading();
            uni.showToast({ title: '请求失败', icon: 'none' });
            console.error(err);
        }
    });

};
</script>

<style>
.container {
  padding: 20px;
}
.section {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.header {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 10px;
}
.desc {
  font-size: 14px;
  color: #666;
  margin-bottom: 15px;
}
.actions {
  display: flex;
  gap: 10px;
}
.btn {
  margin: 0;
}
</style>