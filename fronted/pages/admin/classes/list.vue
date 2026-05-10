<template>
  <view class="container">
    <view class="header">
      <text class="title">班级管理</text>
      <button size="mini" type="primary" @click="showAddModal = true">+ 新增班级</button>
    </view>
    
    <view class="list">
      <view class="list-item header-row">
        <text class="col id">ID</text>
        <text class="col name">班级名称</text>
        <text class="col teacher">绑定教师ID</text>
        <text class="col count">人数</text>
        <text class="col action">操作</text>
      </view>
      <view v-for="item in classes" :key="item.id" class="list-item">
        <text class="col id">{{ item.id }}</text>
        <text class="col name">{{ item.name }}</text>
        <text class="col teacher">{{ item.teacher_id || '-' }}</text>
        <text class="col count">{{ item.student_count }}</text>
        <view class="col action">
          <text class="delete-btn" @click="deleteClass(item)">删除</text>
        </view>
      </view>
    </view>
    
    <!-- Add Modal -->
    <view v-if="showAddModal" class="modal-overlay">
      <view class="modal">
        <view class="modal-header">新增班级</view>
        <input class="input" v-model="newClassName" placeholder="请输入班级名称" />
        <view class="modal-footer">
          <button size="mini" @click="showAddModal = false">取消</button>
          <button size="mini" type="primary" @click="addClass">确定</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { request } from '@/utils/request.js';

const classes = ref([]);
const showAddModal = ref(false);
const newClassName = ref('');

const fetchClasses = async () => {
  try {
    const res = await request({ url: '/admin/classes' });
    classes.value = res;
  } catch (e) {
    console.error(e);
  }
};

const addClass = async () => {
  if (!newClassName.value) return;
  try {
    await request({
      url: '/admin/classes',
      method: 'POST',
      data: { name: newClassName.value }
    });
    showAddModal.value = false;
    newClassName.value = '';
    fetchClasses();
  } catch (e) {
    console.error(e);
  }
};

const deleteClass = async (item) => {
  uni.showModal({
    title: '确认删除',
    content: `确定要删除 ${item.name} 吗？`,
    success: async (res) => {
      if (res.confirm) {
        try {
          await request({
            url: `/admin/classes/${item.id}`,
            method: 'DELETE'
          });
          fetchClasses();
        } catch (e) {
           console.error(e);
        }
      }
    }
  });
};

onMounted(() => {
  fetchClasses();
});
</script>

<style>
.container {
  padding: 10px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}
.title {
  font-size: 18px;
  font-weight: bold;
}
.list-item {
  display: flex;
  padding: 10px 0;
  border-bottom: 1px solid #f5f5f5;
  align-items: center;
}
.header-row {
  background-color: #f9f9f9;
  font-weight: bold;
}
.col {
  font-size: 14px;
  text-align: center;
}
.id { width: 10%; }
.name { width: 30%; }
.teacher { width: 20%; }
.count { width: 15%; }
.action { width: 25%; }

.delete-btn {
  color: #ff4d4f;
  font-size: 14px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
}
.modal {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  width: 80%;
}
.modal-header {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 15px;
  text-align: center;
}
.input {
  border: 1px solid #ddd;
  padding: 8px;
  border-radius: 4px;
  margin-bottom: 15px;
}
.modal-footer {
  display: flex;
  justify-content: space-around;
}
</style>
