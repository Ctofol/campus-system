<template>
  <view class="container">
    <view class="tabs">
      <view class="tab" :class="{active: role === 'student'}" @click="role = 'student'; fetchUsers()">学生</view>
      <view class="tab" :class="{active: role === 'teacher'}" @click="role = 'teacher'; fetchUsers()">教师</view>
    </view>
    
    <view class="list">
      <view class="list-item header-row">
        <text class="col name">姓名</text>
        <text class="col phone">手机号</text>
        <text class="col info" v-if="role==='student'">班级</text>
        <text class="col info" v-else>工号</text>
        <text class="col action">操作</text>
      </view>
      <view v-for="item in users" :key="item.id" class="list-item">
        <text class="col name">{{ item.name }}</text>
        <text class="col phone">{{ item.phone }}</text>
        <text class="col info">{{ role==='student' ? item.class_name : item.student_id }}</text>
        <view class="col action">
          <text class="btn reset" @click="resetPwd(item)">重置</text>
          <text class="btn delete" @click="deleteUser(item)">删除</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { request } from '@/utils/request.js';

const role = ref('student');
const users = ref([]);

const fetchUsers = async () => {
  try {
    const res = await request({ 
      url: '/admin/users',
      data: { role: role.value }
    });
    users.value = res;
  } catch (e) {
    console.error(e);
  }
};

const deleteUser = async (item) => {
  uni.showModal({
    title: '确认删除',
    content: `确定要删除用户 ${item.name} 吗？`,
    success: async (res) => {
      if (res.confirm) {
        try {
          await request({
            url: `/admin/users/${item.id}`,
            method: 'DELETE'
          });
          fetchUsers();
        } catch (e) {
           console.error(e);
        }
      }
    }
  });
};

const resetPwd = async (item) => {
  uni.showModal({
    title: '重置密码',
    content: `确定要重置 ${item.name} 的密码为 123456 吗？`,
    success: async (res) => {
      if (res.confirm) {
        try {
          await request({
            url: `/admin/users/${item.id}/reset-password`,
            method: 'POST'
          });
          uni.showToast({ title: '重置成功', icon: 'success' });
        } catch (e) {
           console.error(e);
        }
      }
    }
  });
};

onMounted(() => {
  fetchUsers();
});
</script>

<style>
.container {
  padding: 10px;
}
.tabs {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 1px solid #ddd;
}
.tab {
  flex: 1;
  text-align: center;
  padding: 10px;
  font-size: 16px;
}
.tab.active {
  color: #007aff;
  border-bottom: 2px solid #007aff;
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
.name { width: 20%; }
.phone { width: 30%; }
.info { width: 20%; }
.action { width: 30%; display: flex; justify-content: space-around; }

.btn {
  font-size: 12px;
  padding: 2px 5px;
}
.reset { color: #007aff; }
.delete { color: #ff4d4f; }
</style>
