<template>
  <view class="home-container">
    <view class="student-dashboard">
      <view class="header-section">
        <view class="teacher-task-box" v-if="teacherTask" @click="handleTaskClick">
          <view class="task-icon-box"><text class="task-icon">📢</text></view>
          <view class="task-content">
            <text class="task-title">老师发布了新任务</text>
            <text class="task-desc">{{ teacherTask.title }}</text>
          </view>
          <view class="task-action"><text class="btn-text">去完成</text></view>
        </view>
        <view class="student-func-grid">
          <view class="stu-func-item" @click="gotoAiPolice">
            <view class="stu-func-icon">🤖</view><text class="stu-func-name">AI计数</text>
          </view>
          <view class="stu-func-item" @click="browseActivities">
            <view class="stu-func-icon">🚩</view><text class="stu-func-name">跑团活动</text>
          </view>
          <view class="stu-func-item" @click="uni.redirectTo({url: '/pages/test/test'})">
            <view class="stu-func-icon">📊</view><text class="stu-func-name">体测成绩</text>
          </view>
          <view class="stu-func-item" @click="uni.redirectTo({url: '/pages/mine/mine'})">
            <view class="stu-func-icon">👤</view><text class="stu-func-name">个人中心</text>
          </view>
        </view>
      </view>
      
      <view class="section-container module-card">
        <view class="section-header"><text class="section-title">体能考核项目</text></view>
        <view class="test-project-list">
           <view class="test-card" v-for="(item, index) in testProjects" :key="index" @click="startTestProject(item)">
             <view class="test-icon">{{ item.type === 'pull-up' ? '💪' : (item.type === 'sit-up' ? '🧘' : '🏋️') }}</view>
             <view class="test-info">
               <text class="test-name">{{ item.name }}</text>
               <view class="test-tags"><text class="tag-small" :class="item.tagClass">{{ item.tag }}</text></view>
             </view>
             <text class="test-status">{{ item.status }}</text>
           </view>
        </view>
      </view>

      <view class="section-container module-card">
        <view class="section-header" @click="showTrainingPlans = !showTrainingPlans">
          <text class="section-title">专项训练计划</text>
          <text class="section-more">{{ showTrainingPlans ? '收起' : '展开' }}</text>
        </view>
        <view class="training-list" v-if="showTrainingPlans">
          <view class="training-card" v-for="(item, index) in trainingPlans" :key="index" @click="startTraining(item)">
            <view class="card-left">
              <view class="tag-box" :class="item.typeClass"><text class="tag-text">{{ item.type }}</text></view>
              <view class="training-info"><text class="training-name">{{ item.name }}</text><text class="training-meta">{{ item.duration }}分钟 · {{ item.difficulty }}</text></view>
            </view>
            <view class="card-right">
              <view class="status-icon" v-if="item.isCompleted"><text>✅</text></view>
              <view class="start-btn-small" v-else><text>开始</text></view>
            </view>
          </view>
        </view>
      </view>

      <view class="section-container module-card">
        <view class="section-header">
          <text class="section-title">跑团联盟</text>
          <view class="header-actions">
            <text class="action-link" @click="createClub">创建</text><text class="divider">|</text>
            <text class="action-link" @click="joinClub">加入</text><text class="divider">|</text>
            <text class="action-link" @click="browseActivities">活动浏览</text>
          </view>
        </view>
        <view class="my-club-card" @click="enterClubDetail">
          <view class="club-bg-overlay"></view>
          <view class="club-info">
            <view class="club-header"><text class="club-name">{{ myClub.name }}</text><text class="club-rank">No.{{ myClub.rank }}</text></view>
            <view class="club-stats">
              <view class="stat-box"><text class="val">{{ myClub.members }}</text><text class="label">成员</text></view>
              <view class="stat-box"><text class="val">{{ myClub.totalDistance }}</text><text class="label">总里程(km)</text></view>
              <view class="stat-box"><text class="val">{{ myClub.activityCount }}</text><text class="label">本月活动</text></view>
            </view>
          </view>
          <view class="rank-entry" @click.stop="showRank"><text class="rank-icon">🏆</text><text class="rank-text">排行榜</text></view>
        </view>
        <view class="community-feed">
          <text class="feed-title">最新动态</text>
          <scroll-view scroll-x class="activity-scroll">
            <view class="activity-card" v-for="(act, idx) in activities" :key="idx" @click="showActivityDetail(act)">
              <view class="act-tag" :class="act.statusClass">{{ act.status }}</view>
              <text class="act-name">{{ act.name }}</text>
              <text class="act-time">🕒 {{ act.time }}</text>
              <view class="act-users">
                <view class="avatar-group"><view class="avatar-circle" v-for="n in 3" :key="n" :style="{backgroundColor: getRandomColor()}"></view></view>
                <text class="act-count">{{ act.joined }}人已报名</text>
              </view>
            </view>
          </scroll-view>
        </view>
      </view>
    </view>

    <!-- 底部占位 -->
    <view style="height: 120rpx;"></view>
    
    <CustomTabBar current="/pages/home/home" />

    <!-- 排行榜弹窗 -->
    <view class="modal-overlay" v-if="showRankModal" @click="closeRank">
      <view class="rank-modal" @click.stop>
        <view class="modal-header"><text class="modal-title">🏆 跑团排行榜</text><text class="close-btn" @click="closeRank">×</text></view>
        <view class="rank-list">
          <view class="rank-item" v-for="(item, idx) in rankList" :key="idx">
            <view class="rank-num" :class="'rank-' + (idx + 1)">{{ idx + 1 }}</view>
            <view class="rank-info"><text class="rank-name">{{ item.name }}</text><text class="rank-detail">{{ item.members }}人 / {{ item.distance }}km</text></view>
            <view class="rank-trend"><text>🔥 {{ item.heat }}</text></view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import CustomTabBar from '@/components/CustomTabBar/CustomTabBar.vue';
import { getStudentTasks } from '@/utils/request.js';

// 角色状态
const role = ref('student');
const userInfo = ref({});

const teacherTask = ref(null);

const fetchLatestTask = async () => {
  try {
    const res = await getStudentTasks({ page: 1, size: 1 });
    if (res.items && res.items.length > 0) {
      const task = res.items[0];
      // Only show if pending or urgent? Or just the latest one.
      // If completed, maybe show "No pending tasks"?
      // For now show latest regardless of status, or prefer pending?
      // The API returns tasks ordered by ID desc.
      teacherTask.value = {
         id: task.id,
         title: task.title,
         desc: task.description || (task.min_distance ? `目标: ${task.min_distance}km` : '请查看详情')
      };
    } else {
        teacherTask.value = null;
    }
  } catch (e) {
    console.error('Fetch task failed', e);
    // teacherTask.value = { id: 101, title: '本周五前完成一次3000米拉练', desc: '示例任务' }; // Fallback? No, better null.
  }
};

onShow(() => {
  const userRole = uni.getStorageSync('userRole') || uni.getStorageSync('role');
  if (userRole) role.value = userRole;
  
  const storedUser = uni.getStorageSync('userInfo');
  if (storedUser) {
    try {
        userInfo.value = typeof storedUser === 'string' ? JSON.parse(storedUser) : storedUser;
    } catch (e) {
        console.error('JSON parse error', e);
        userInfo.value = {};
    }
  }
  
  fetchLatestTask();
});

// --- 学生端数据 ---
const showTrainingPlans = ref(true);
const showRankModal = ref(false);
// const teacherTask = ref({ id: 101, title: '本周五前完成一次3000米拉练，配速要求6\'00"', type: 'urgent' });
const testProjects = ref([
  { name: '引体向上', tag: '体测项目', tagClass: 'tag-police', status: '未完成', type: 'pull-up' },
  { name: '仰卧起坐', tag: '日常测评', tagClass: 'tag-daily', status: '进行中', type: 'sit-up' },
  { name: '俯卧撑', tag: '基础训练', tagClass: 'tag-base', status: '未开始', type: 'push-up' }
]);
const trainingPlans = ref([
  { id: 1, name: '综合体能测试', type: '考核', typeClass: 'tag-red', duration: 45, difficulty: '高强度', isCompleted: false },
  { id: 2, name: '1000米爆发力训练', type: '专项', typeClass: 'tag-blue', duration: 20, difficulty: '中强度', isCompleted: true },
  { id: 3, name: '核心力量强化课程', type: '日常', typeClass: 'tag-green', duration: 30, difficulty: '低强度', isCompleted: false }
]);
const myClub = ref({ name: '刑侦先锋跑团', rank: 3, members: 42, totalDistance: 1205.8, activityCount: 5 });
const activities = ref([
  { name: '五四青年节环校跑', time: '5月4日 07:00', status: '报名中', statusClass: 'status-active', joined: 128 },
  { name: '周末夜跑打卡赛', time: '本周六 19:00', status: '进行中', statusClass: 'status-ing', joined: 56 },
  { name: '运动技能交流会', time: '下周三 14:00', status: '预告', statusClass: 'status-future', joined: 30 }
]);
const memberUpdates = ref([
  { user: '张伟', time: '10分钟前', action: '完成了', result: '5公里晨跑', likes: 12, avatarColor: '#FF6B6B' },
  { user: '李娜', time: '35分钟前', action: '打卡了', result: '核心力量训练', likes: 8, avatarColor: '#4ECDC4' },
  { user: '王强', time: '1小时前', action: '刷新了', result: '3000米个人记录', likes: 25, avatarColor: '#45B7D1' }
]);
const rankList = ref([
  { name: '晨跑先锋队', members: 56, distance: 2300, heat: 9800 },
  { name: '长跑菁英团', members: 48, distance: 1800, heat: 8500 },
  { name: '校园马拉松社', members: 42, distance: 1205, heat: 7200 },
  { name: '阳光运动队', members: 35, distance: 980, heat: 6000 }
]);

const getRandomColor = () => {
  const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD'];
  return colors[Math.floor(Math.random() * colors.length)];
};

const handleTaskClick = () => { 
  uni.navigateTo({
    url: '/pages/student/tasks/list'
  });
};
const gotoAiPolice = () => { uni.navigateTo({url: '/pages/ai-police/ai-police'}); };
const browseActivities = () => { uni.navigateTo({url: '/pages/activity/list'}); };
const createClub = () => { uni.showToast({title: '创建功能即将上线', icon:'none'}); };
const joinClub = () => { uni.showToast({title: '加入功能即将上线', icon:'none'}); };
const enterClubDetail = () => { uni.showToast({title: '跑团详情', icon:'none'}); };
const showRank = () => { showRankModal.value = true; };
const closeRank = () => { showRankModal.value = false; };
const showActivityDetail = (act) => { 
  uni.navigateTo({
    url: `/pages/activity/detail?name=${act.name}`
  });
};
const startTestProject = (item) => { uni.redirectTo({url: '/pages/test/test?project=' + item.name + '&type=' + item.type}); };
const startTraining = (item) => { 
  // 实战训练跳转
  uni.navigateTo({
    url: `/pages/run/run?mode=training&planId=${item.id}&name=${item.name}`
  }); 
};

</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.student-dashboard {
  padding-bottom: 20rpx;
}

/* Header Section */
.header-section {
  background: linear-gradient(180deg, #20C997 0%, #20C997 60%, #f5f7fa 90%);
  padding: 20rpx 30rpx 40rpx;
  border-bottom-left-radius: 40rpx;
  border-bottom-right-radius: 40rpx;
}

.teacher-task-box {
  background: rgba(255,255,255,0.95);
  border-radius: 16rpx;
  padding: 20rpx;
  display: flex;
  align-items: center;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.08);
}
.task-icon-box { width: 60rpx; height: 60rpx; background: #e8f5e9; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 20rpx; }
.task-icon { font-size: 32rpx; }
.task-content { flex: 1; display: flex; flex-direction: column; }
.task-title { font-size: 26rpx; font-weight: bold; color: #333; }
.task-desc { font-size: 22rpx; color: #666; margin-top: 4rpx; }
.task-action { background: #ff6b6b; padding: 8rpx 20rpx; border-radius: 30rpx; }
.btn-text { color: #fff; font-size: 22rpx; font-weight: bold; }

.student-func-grid {
  display: flex;
  justify-content: space-between;
  padding: 20rpx 10rpx;
}
.stu-func-item { display: flex; flex-direction: column; align-items: center; }
.stu-func-icon {
  width: 100rpx; height: 100rpx; border-radius: 30rpx; background: #fff;
  display: flex; align-items: center; justify-content: center; font-size: 48rpx;
  margin-bottom: 12rpx; box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.05);
}
.stu-func-name { font-size: 24rpx; color: #333; font-weight: 500; }

.section-container {
  background: #fff;
  border-radius: 20rpx;
  margin: 20rpx 30rpx;
  padding: 30rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.02);
}
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24rpx; }
.section-title { font-size: 32rpx; font-weight: bold; color: #333; border-left: 8rpx solid #20C997; padding-left: 16rpx; }
.section-more, .action-link { font-size: 26rpx; color: #999; }
.header-actions { display: flex; gap: 10rpx; align-items: center; }
.divider { color: #eee; font-size: 20rpx; }

/* Test Project List */
.test-project-list { display: flex; flex-direction: column; gap: 20rpx; }
.test-card { display: flex; align-items: center; padding: 20rpx; background: #f9f9f9; border-radius: 12rpx; }
.test-icon { font-size: 40rpx; margin-right: 20rpx; width: 60rpx; text-align: center; }
.test-info { flex: 1; }
.test-name { font-size: 28rpx; font-weight: bold; color: #333; }
.test-tags { margin-top: 6rpx; }
.tag-small { font-size: 20rpx; padding: 2rpx 8rpx; border-radius: 4rpx; color: #fff; }
.tag-police { background: #4dabf7; }
.tag-daily { background: #20C997; }
.tag-base { background: #adb5bd; }
.test-status { font-size: 24rpx; color: #ff9f43; font-weight: bold; }

/* Training List */
.training-list { display: flex; flex-direction: column; gap: 20rpx; }
.training-card { display: flex; justify-content: space-between; align-items: center; padding: 20rpx; background: #fff; border: 1px solid #f0f0f0; border-radius: 12rpx; }
.card-left { display: flex; align-items: center; }
.tag-box { padding: 6rpx 12rpx; border-radius: 8rpx; margin-right: 20rpx; }
.tag-text { font-size: 20rpx; color: #fff; }
.tag-red { background: #ff6b6b; }
.tag-blue { background: #4dabf7; }
.tag-green { background: #20C997; }
.training-info { display: flex; flex-direction: column; }
.training-name { font-size: 28rpx; font-weight: bold; color: #333; }
.training-meta { font-size: 22rpx; color: #999; margin-top: 4rpx; }
.start-btn-small { padding: 6rpx 20rpx; background: #20C997; color: #fff; border-radius: 20rpx; font-size: 22rpx; }

/* Club Card */
.my-club-card { background: linear-gradient(135deg, #3a3a3a, #1a1a1a); border-radius: 20rpx; padding: 30rpx; color: #fff; position: relative; overflow: hidden; margin-bottom: 30rpx; }
.club-bg-overlay { position: absolute; right: -20rpx; bottom: -20rpx; width: 200rpx; height: 200rpx; background: rgba(255,255,255,0.05); border-radius: 50%; }
.club-header { display: flex; align-items: center; margin-bottom: 20rpx; }
.club-name { font-size: 32rpx; font-weight: bold; margin-right: 20rpx; }
.club-rank { font-size: 22rpx; background: #ff9f43; color: #fff; padding: 2rpx 10rpx; border-radius: 6rpx; }
.club-stats { display: flex; justify-content: space-between; }
.stat-box { display: flex; flex-direction: column; align-items: center; }
.stat-box .val { font-size: 32rpx; font-weight: bold; color: #20C997; }
.stat-box .label { font-size: 22rpx; color: #aaa; margin-top: 4rpx; }
.rank-entry { position: absolute; top: 30rpx; right: 30rpx; display: flex; align-items: center; background: rgba(255,255,255,0.1); padding: 6rpx 16rpx; border-radius: 30rpx; }
.rank-icon { font-size: 24rpx; margin-right: 6rpx; }
.rank-text { font-size: 22rpx; }

/* Community Feed */
.community-feed { margin-top: 10rpx; }
.feed-title { font-size: 28rpx; font-weight: bold; color: #333; margin-bottom: 20rpx; display: block; }
.activity-scroll { white-space: nowrap; width: 100%; }
.activity-card { display: inline-block; width: 300rpx; background: #f8f9fa; border-radius: 12rpx; padding: 20rpx; margin-right: 20rpx; vertical-align: top; position: relative; }
.act-tag { position: absolute; top: 0; right: 0; font-size: 18rpx; padding: 4rpx 10rpx; border-bottom-left-radius: 12rpx; border-top-right-radius: 12rpx; color: #fff; }
.status-active { background: #20C997; }
.status-ing { background: #ff9f43; }
.status-future { background: #4dabf7; }
.act-name { font-size: 26rpx; font-weight: bold; color: #333; display: block; margin-bottom: 10rpx; margin-top: 10rpx; white-space: normal; }
.act-time { font-size: 20rpx; color: #999; display: block; margin-bottom: 16rpx; }
.act-users { display: flex; align-items: center; justify-content: space-between; }
.avatar-group { display: flex; }
.avatar-circle { width: 30rpx; height: 30rpx; border-radius: 50%; border: 2rpx solid #fff; margin-left: -10rpx; }
.avatar-circle:first-child { margin-left: 0; }
.act-count { font-size: 20rpx; color: #666; }

/* Rank Modal */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 1000; display: flex; justify-content: center; align-items: center; }
.rank-modal { width: 600rpx; background: #fff; border-radius: 20rpx; padding: 30rpx; max-height: 80vh; overflow-y: auto; }
.modal-header { display: flex; justify-content: space-between; margin-bottom: 30rpx; align-items: center; }
.modal-title { font-size: 32rpx; font-weight: bold; }
.close-btn { font-size: 40rpx; color: #999; line-height: 1; }
.rank-list { display: flex; flex-direction: column; gap: 20rpx; }
.rank-item { display: flex; align-items: center; padding: 10rpx 0; border-bottom: 1px solid #f5f5f5; }
.rank-num { width: 50rpx; font-size: 32rpx; font-weight: bold; color: #999; text-align: center; margin-right: 20rpx; }
.rank-1 { color: #ffd700; }
.rank-2 { color: #c0c0c0; }
.rank-3 { color: #cd7f32; }
.rank-info { flex: 1; display: flex; flex-direction: column; }
.rank-name { font-size: 28rpx; font-weight: bold; color: #333; }
.rank-detail { font-size: 22rpx; color: #999; }
.rank-trend { font-size: 24rpx; color: #ff6b6b; font-weight: bold; }
</style>
