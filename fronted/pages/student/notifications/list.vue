<template>
  <view class="page">
    <!-- 导航栏 -->
    <view class="navbar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="navbar-back" @tap="goBack"><text class="navbar-back-icon">‹</text></view>
      <text class="navbar-title">消息通知</text>
      <view class="navbar-right-group">
        <text class="navbar-link" @tap="showTeacherComposer">联系老师</text>
        <text class="navbar-link navbar-link--muted" @tap="clearUnread">已读</text>
      </view>
    </view>

    <view class="body" :style="{ paddingTop: navHeight + 'px' }">
      <view v-if="composerVisible" class="composer-card">
        <view class="composer-head">
          <text class="composer-title">给老师留言</text>
          <text class="composer-close" @tap="composerVisible = false">关闭</text>
        </view>
        <input class="composer-input" v-model.trim="teacherMessageTitle" maxlength="30" placeholder="标题，例如：训练问题" />
        <textarea class="composer-textarea" v-model.trim="teacherMessageBody" maxlength="300" placeholder="请输入需要老师查看的内容" />
        <button class="composer-btn" :loading="sendingTeacherMessage" @tap="sendTeacherMessage">发送</button>
      </view>

      <!-- 分类 Tab -->
      <view class="tab-row">
        <view
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-item"
          :class="{ 'tab-item--active': activeTab === tab.key }"
          @tap="switchTab(tab.key)"
        >
          <view class="tab-icon-wrap" :style="{ background: tab.color }">
            <image class="tab-icon-img" :src="tab.icon" mode="aspectFit" />
            <view v-if="tabBadge(tab.key) > 0" class="tab-badge">{{ tabBadge(tab.key) }}</view>
          </view>
          <text class="tab-label">{{ tab.label }}</text>
          <view v-if="activeTab === tab.key" class="tab-line" />
        </view>
      </view>

      <!-- 消息列表 -->
      <scroll-view scroll-y class="list" @scrolltolower="loadMore">
        <template v-if="filteredList.length">
          <template v-for="(group, gi) in groupedList" :key="gi">
            <text class="date-sep">{{ group.label }}</text>
            <view
              v-for="item in group.items"
              :key="item.id"
              class="notif-item"
              @tap="openItem(item)"
            >
              <view class="notif-avatar" :style="{ background: getAvatarBg(item) }">
                <image v-if="item.avatar" :src="item.avatar" class="notif-avatar-img" mode="aspectFill" />
                <image v-else class="notif-avatar-icon-img" :src="getAvatarIconSrc(item)" mode="aspectFit" />
              </view>
              <view class="notif-content">
                <view class="notif-row1">
                  <text class="notif-name">{{ item.sender_name || item.title }}</text>
                  <view v-if="item.tag" class="notif-tag" :style="{ color: getTagColor(item), background: getTagBg(item) }">
                    {{ item.tag }}
                  </view>
                  <view class="notif-time-wrap">
                    <text class="notif-time">{{ formatTime(item.created_at) }}</text>
                    <view v-if="!item.is_read" class="notif-dot" />
                  </view>
                </view>
                <text class="notif-sub">{{ item.title }}</text>
                <text class="notif-body">{{ item.body }}</text>
              </view>
            </view>
          </template>
        </template>

        <view v-if="!loading && filteredList.length === 0" class="empty">
          <text class="empty-txt">暂无消息</text>
        </view>
        <view v-if="!hasMore && filteredList.length > 0" class="no-more"><text>没有更多消息了~</text></view>
      </scroll-view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import { request } from '@/utils/request.js';

const statusBarHeight = ref(20);
const navHeight = computed(() => statusBarHeight.value + 44);

const tabs = [
  { key: 'all', label: '全部消息', icon: '/static/icons/icon-notification.svg', color: '#fff' },
  { key: 'run_group', label: '跑团消息', icon: '/static/icons/icon-group.svg', color: '#fff' },
  { key: 'interaction', label: '互动消息', icon: '/static/icons/icon-mail.svg', color: '#fff' },
  { key: 'system', label: '系统通知', icon: '/static/icons/icon-mail.svg', color: '#fff' },
];

const activeTab = ref('all');
const notifications = ref([]);
const loading = ref(false);
const hasMore = ref(true);
const page = ref(1);
const composerVisible = ref(false);
const sendingTeacherMessage = ref(false);
const teacherMessageTitle = ref('');
const teacherMessageBody = ref('');

const tabBadge = (key) => {
  const list = key === 'all' ? notifications.value : notifications.value.filter(n => mapType(n.ntype) === key);
  return list.filter(n => !n.is_read).length;
};

const mapType = (ntype) => {
  if (!ntype) return 'system';
  if (['run_group', 'group', 'run_group_activity', 'run_group_apply'].includes(ntype)) return 'run_group';
  if (['like', 'comment', 'follow', 'interaction'].includes(ntype)) return 'interaction';
  return 'system';
};

const filteredList = computed(() => {
  if (activeTab.value === 'all') return notifications.value;
  return notifications.value.filter(n => mapType(n.ntype) === activeTab.value);
});

const groupedList = computed(() => {
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);

  const todayStr = today.toDateString();
  const yestStr = yesterday.toDateString();

  const groups = {};
  filteredList.value.forEach(item => {
    const d = new Date(item.created_at);
    const ds = d.toDateString();
    let label;
    if (ds === todayStr) label = '今天';
    else if (ds === yestStr) label = '昨天';
    else label = `更早`;
    if (!groups[label]) groups[label] = [];
    groups[label].push(item);
  });

  const order = ['今天', '昨天', '更早'];
  return order.filter(l => groups[l]).map(l => ({ label: l, items: groups[l] }));
});

const getAvatarBg = (item) => {
  const type = mapType(item.ntype);
  if (type === 'run_group' || type === 'interaction' || type === 'system') return '#e8f8f2';
  return '#fff4e6';
};

const getAvatarIconSrc = (item) => {
  const type = mapType(item.ntype);
  if (type === 'run_group') return '/static/icons/icon-group.svg';
  if (type === 'interaction' || type === 'system') return '/static/icons/icon-mail.svg';
  return '/static/icons/icon-notification.svg';
};

const getTagColor = (item) => {
  if (item.tag === '跑团') return '#26b586';
  if (item.tag === '成员' || item.tag === '副团长') return '#5b8cff';
  return '#f5a623';
};

const getTagBg = (item) => {
  if (item.tag === '跑团') return '#e8f8f2';
  if (item.tag === '成员' || item.tag === '副团长') return '#eef2ff';
  return '#fff4e6';
};

const formatTime = (iso) => {
  if (!iso) return '';
  const d = new Date(iso);
  const now = new Date();
  const diff = now - d;
  const days = Math.floor(diff / 86400000);
  if (days === 0) return `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
  if (days === 1) return `昨天 ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
  return `${d.getMonth()+1}-${String(d.getDate()).padStart(2,'0')}`;
};

const enrichItem = (item) => {
  const type = mapType(item.ntype);
  return {
    ...item,
    tag: type === 'run_group' ? '跑团' : type === 'interaction' ? '成员' : getSystemTag(item.ntype),
    sender_name: item.sender_name || item.title,
    body: item.body || item.content || '',
  };
};

const getSystemTag = (ntype) => {
  const map = {
    task: '任务',
    task_reminder: '任务',
    teacher_message: '教师',
    health_review: '健康',
    system: '系统'
  };
  return map[ntype] || '系统';
};

const loadNotifications = async (reset = true) => {
  if (loading.value) return;
  loading.value = true;
  if (reset) { page.value = 1; hasMore.value = true; }
  try {
    const res = await request({ url: `/notifications?limit=30&page=${page.value}`, method: 'GET' });
    const items = (Array.isArray(res) ? res : res?.items || []).map(enrichItem);
    if (reset) notifications.value = items;
    else notifications.value.push(...items);
    hasMore.value = items.length >= 30;
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const loadMore = () => {
  if (!hasMore.value || loading.value) return;
  page.value++;
  loadNotifications(false);
};

const switchTab = (key) => { activeTab.value = key; };

const openItem = async (item) => {
  if (!item.is_read) {
    item.is_read = true;
    try { await request({ url: `/notifications/${item.id}/read`, method: 'PUT' }); } catch (e) {}
  }
  if (item.ntype === 'health_review') {
    uni.navigateTo({ url: '/pages/health/request' });
    return;
  }
  if (item.ntype === 'run_group' || item.ntype === 'group' || item.ntype === 'run_group_activity') {
    uni.navigateTo({ url: '/pages/run-group/my' });
    return;
  }
  if (item.ntype === 'task' || item.ntype === 'task_reminder') {
    uni.navigateTo({ url: '/pages/student/tasks/list' });
    return;
  }
  uni.showModal({ title: item.title, content: item.body || '', showCancel: false });
};

const clearUnread = async () => {
  try {
    await request({ url: '/notifications/read-all', method: 'PUT' });
    notifications.value.forEach(n => { n.is_read = true; });
    uni.showToast({ title: '已清除未读', icon: 'success' });
  } catch (e) {
    uni.showToast({ title: '操作失败', icon: 'none' });
  }
};

const showTeacherComposer = () => {
  composerVisible.value = true;
};

const sendTeacherMessage = async () => {
  const message = teacherMessageBody.value.trim();
  if (!message) {
    uni.showToast({ title: '请输入留言内容', icon: 'none' });
    return;
  }
  sendingTeacherMessage.value = true;
  try {
    const res = await request({
      url: '/notifications/to-teachers',
      method: 'POST',
      data: {
        title: teacherMessageTitle.value.trim() || '学生消息',
        message
      }
    });
    uni.showToast({ title: `已发送给${res.sent || 0}位老师`, icon: 'success' });
    teacherMessageTitle.value = '';
    teacherMessageBody.value = '';
    composerVisible.value = false;
  } catch (e) {
    uni.showToast({ title: e.message || '发送失败', icon: 'none' });
  } finally {
    sendingTeacherMessage.value = false;
  }
};

const goBack = () => uni.navigateBack();

onShow(() => {
  const sys = uni.getSystemInfoSync();
  statusBarHeight.value = sys.statusBarHeight || 20;
  loadNotifications();
});
</script>

<style scoped>
.page { min-height: 100vh; background: #f5f7fa; }

.navbar {
  position: fixed; top: 0; left: 0; right: 0;
  background: #fff; z-index: 100;
  display: flex; align-items: center;
  padding: 0 28rpx; height: 44px;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.06);
}
.navbar-back { width: 60rpx; display: flex; align-items: center; }
.navbar-back-icon { font-size: 48rpx; color: #333; }
.navbar-title { flex: 1; text-align: center; font-size: 32rpx; font-weight: 700; color: #1a2b3c; }
.navbar-right-group {
  width: 176rpx;
  display: flex;
  justify-content: flex-end;
  gap: 18rpx;
}
.navbar-link { font-size: 24rpx; color: #26b586; white-space: nowrap; }
.navbar-link--muted { color: #718094; }

.body { background: #f5f7fa; }

.composer-card {
  margin: 18rpx 24rpx;
  padding: 24rpx;
  background: #fff;
  border-radius: 18rpx;
  border: 1rpx solid rgba(24, 35, 46, 0.06);
}
.composer-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18rpx;
}
.composer-title { font-size: 30rpx; font-weight: 700; color: #18232e; }
.composer-close { font-size: 24rpx; color: #718094; }
.composer-input,
.composer-textarea {
  box-sizing: border-box;
  width: 100%;
  border-radius: 14rpx;
  background: #f7faf9;
  border: 1rpx solid rgba(24, 35, 46, 0.06);
  padding: 18rpx;
  font-size: 26rpx;
  color: #18232e;
}
.composer-textarea {
  height: 150rpx;
  margin-top: 14rpx;
}
.composer-btn {
  margin-top: 18rpx;
  height: 76rpx;
  line-height: 76rpx;
  border-radius: 999rpx;
  background: #24bfa2;
  color: #fff;
  font-size: 28rpx;
}

/* 分类 Tab */
.tab-row {
  background: #fff;
  display: flex;
  padding: 24rpx 0 16rpx;
  margin-bottom: 16rpx;
}
.tab-item {
  flex: 1; display: flex; flex-direction: column; align-items: center;
  position: relative; padding-bottom: 8rpx;
}
.tab-icon-wrap {
  width: 88rpx; height: 88rpx; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 40rpx; position: relative; margin-bottom: 10rpx;
}
.tab-icon { font-size: 38rpx; }
.tab-icon-img { width: 44rpx; height: 44rpx; }
.tab-badge {
  position: absolute; top: -4rpx; right: -4rpx;
  min-width: 30rpx; height: 30rpx; border-radius: 15rpx;
  background: #ff4d4f; color: #fff; font-size: 18rpx;
  display: flex; align-items: center; justify-content: center;
  padding: 0 6rpx;
}
.tab-label { font-size: 22rpx; color: #8a9bab; }
.tab-item--active .tab-label { color: #26b586; font-weight: 600; }
.tab-line {
  position: absolute; bottom: 0; left: 50%; transform: translateX(-50%);
  width: 40rpx; height: 4rpx; background: #26b586; border-radius: 2rpx;
}

/* 日期分隔 */
.date-sep {
  display: block; font-size: 24rpx; color: #8a9bab;
  padding: 12rpx 28rpx 8rpx;
}

/* 消息列表 */
.list { height: calc(100vh - 44px - 160rpx); }

.notif-item {
  background: #fff; margin: 0 0 2rpx;
  padding: 28rpx 28rpx;
  display: flex; align-items: flex-start; gap: 20rpx;
}
.notif-avatar {
  width: 88rpx; height: 88rpx; border-radius: 50%;
  flex-shrink: 0; display: flex; align-items: center; justify-content: center;
  overflow: hidden;
}
.notif-avatar-img { width: 100%; height: 100%; border-radius: 50%; }
.notif-avatar-icon { font-size: 40rpx; }
.notif-avatar-icon-img { width: 44rpx; height: 44rpx; }

.notif-content { flex: 1; min-width: 0; }
.notif-row1 { display: flex; align-items: center; margin-bottom: 8rpx; gap: 10rpx; }
.notif-name { font-size: 28rpx; font-weight: 700; color: #1a2b3c; }
.notif-tag {
  font-size: 20rpx; padding: 2rpx 12rpx; border-radius: 20rpx;
  flex-shrink: 0;
}
.notif-time-wrap { margin-left: auto; display: flex; align-items: center; gap: 10rpx; flex-shrink: 0; }
.notif-time { font-size: 22rpx; color: #8a9bab; }
.notif-dot { width: 14rpx; height: 14rpx; border-radius: 50%; background: #ff4d4f; }
.notif-sub { display: block; font-size: 26rpx; font-weight: 600; color: #333; margin-bottom: 6rpx; }
.notif-body { display: block; font-size: 24rpx; color: #8a9bab; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }

.empty { padding: 120rpx 0; display: flex; flex-direction: column; align-items: center; }
.empty-icon { font-size: 80rpx; display: block; margin-bottom: 20rpx; }
.empty-icon-img { width: 120rpx; height: 120rpx; display: block; margin-bottom: 20rpx; }
.empty-txt { font-size: 28rpx; color: #8a9bab; }

.loading-row { text-align: center; padding: 30rpx; color: #8a9bab; font-size: 24rpx; }
.no-more { text-align: center; padding: 30rpx; color: #c5ced6; font-size: 22rpx; }
</style>
