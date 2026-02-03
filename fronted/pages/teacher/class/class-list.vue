<template>
  <view class="container">
    <view class="header">
      <text class="title">班级管理</text>
      <button class="add-btn" size="mini" type="primary" @click="openBindModal">+ 关联班级</button>
    </view>
    
    <view class="class-list">
      <view class="class-item" v-for="cls in classes" :key="cls.id" @click="goToDetail(cls.id)">
        <view class="info">
          <text class="name">{{ cls.name }}</text>
          <text class="count">{{ cls.student_count }} 人</text>
        </view>
        <view class="actions">
           <text class="delete-btn" @click.stop="unbindClass(cls)">解绑</text>
        </view>
      </view>
      <view v-if="classes.length === 0" class="empty-tip">暂无关联班级，请关联</view>
    </view>
    
    <!-- Bind Modal -->
    <view v-if="showBindModal" class="modal-mask">
      <view class="modal">
        <view class="modal-title">关联已有班级</view>
        <view class="checkbox-list" v-if="availableClasses.length > 0">
           <checkbox-group @change="onCheckboxChange">
              <label class="checkbox-item" v-for="item in availableClasses" :key="item.id">
                 <checkbox :value="String(item.id)" :checked="selectedClassIds.includes(String(item.id))" />
                 <text class="checkbox-label">{{ item.name }} ({{ item.student_count }}人)</text>
              </label>
           </checkbox-group>
        </view>
        <view v-else class="empty-tip">
           没有可关联的班级（所有班级均已有老师）
        </view>
        <view class="modal-btns">
          <button size="mini" @click="showBindModal = false">取消</button>
          <button size="mini" type="primary" @click="bindClasses" :disabled="selectedClassIds.length === 0">确定</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { request } from '@/utils/request';

const classes = ref([]);
const showBindModal = ref(false);
const availableClasses = ref([]);
const selectedClassIds = ref([]);

const fetchClasses = async () => {
  try {
    const res = await request({ url: '/teacher/classes' });
    classes.value = res;
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' });
  }
};

const openBindModal = async () => {
   try {
      const res = await request({ url: '/teacher/available_classes' });
      availableClasses.value = res;
      selectedClassIds.value = [];
      showBindModal.value = true;
   } catch (e) {
      uni.showToast({ title: '无法获取可选班级', icon: 'none' });
   }
};

const onCheckboxChange = (e) => {
   selectedClassIds.value = e.detail.value;
};

const bindClasses = async () => {
  if (selectedClassIds.value.length === 0) return;
  try {
    // Convert string IDs to integers
    const ids = selectedClassIds.value.map(id => parseInt(id));
    await request({
      url: '/teacher/classes/bind',
      method: 'POST',
      data: { class_ids: ids }
    });
    showBindModal.value = false;
    fetchClasses();
    uni.showToast({ title: '关联成功', icon: 'success' });
  } catch (e) {
    uni.showToast({ title: '关联失败: ' + (e.message || '未知错误'), icon: 'none' });
  }
};

const unbindClass = async (cls) => {
  uni.showModal({
    title: '确认解绑',
    content: `确定要不再管理班级 ${cls.name} 吗？\n（班级和学生数据将保留）`,
    success: async (res) => {
      if (res.confirm) {
        try {
          await request({ url: `/teacher/classes/${cls.id}`, method: 'DELETE' });
          fetchClasses();
          uni.showToast({ title: '解绑成功', icon: 'success' });
        } catch (e) {
          uni.showToast({ title: '解绑失败', icon: 'none' });
        }
      }
    }
  });
};

const goToDetail = (id) => {
  uni.navigateTo({ url: `/pages/teacher/class/class-detail?id=${id}` });
};

onMounted(() => {
  fetchClasses();
});
</script>

<style>
.container { padding: 20px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.title { font-size: 20px; font-weight: bold; }
.class-list { margin-top: 10px; }
.class-item {
  background: #fff;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 10px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.name { font-size: 16px; font-weight: 500; }
.count { font-size: 14px; color: #666; margin-left: 10px; }
.delete-btn { color: #ff4d4f; font-size: 14px; padding: 5px 10px; }
.empty-tip { text-align: center; color: #999; margin-top: 30px; font-size: 14px; }

/* Modal Styles */
.modal-mask {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
}
.modal {
  background: #fff;
  width: 80%;
  border-radius: 12px;
  padding: 20px;
}
.modal-title {
  font-size: 18px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 20px;
}
.input {
  border: 1px solid #ddd;
  padding: 10px;
  border-radius: 6px;
  margin-bottom: 20px;
}
.modal-btns {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}
.checkbox-list {
   max-height: 200px;
   overflow-y: auto;
   margin-bottom: 15px;
}
.checkbox-item {
   display: flex;
   align-items: center;
   padding: 10px 0;
   border-bottom: 1px solid #f5f5f5;
}
.checkbox-label {
   margin-left: 10px;
   font-size: 15px;
}
</style>