import { ref, computed } from 'vue';
import { getStudentTasks, getStoredToken, isAuthError, request } from '@/utils/request.js';

const emptyWeekly = () => ({
  distanceKm: '0.00',
  durationLabel: '0:00',
  paceLabel: "--'--\"",
  calories: 0,
  runCount: 0,
  sunshineKm: '0.00',
  hasData: false
});

const mapRecentFromApi = (rows) =>
  (rows || []).map((r) => ({
    id: r.id,
    title: r.title || '自由跑',
    distanceKm: r.distance_km,
    timeLabel: r.time_label,
    paceLabel: r.pace_label,
    hasTrack: !!r.has_track,
    isValid: !!r.is_valid,
    trajectoryPreview: (r.trajectory_preview || []).map((p) => ({
      lat: p.lat,
      lng: p.lng
    })),
    activity: r.activity || null,
    raw: r.activity || null
  }));

const mapWeeklyFromApi = (w) => {
  if (!w) return emptyWeekly();
  return {
    distanceKm: w.distance_km ?? '0.00',
    durationLabel: w.duration_label ?? '0:00',
    paceLabel: w.pace_label ?? "--'--\"",
    calories: Number(w.calories) || 0,
    runCount: Number(w.run_count) || 0,
    sunshineKm: w.sunshine_km ?? '0.00',
    hasData: !!w.has_data
  };
};

export function useStudentHomeDashboard() {
  const loading = ref(false);
  const totalDistanceKm = ref('0.0');
  const unreadNotifyCount = ref(0);
  const recentRuns = ref([]);
  const teacherTasks = ref([]);
  const weeklyStats = ref(emptyWeekly());
  const runGoalKm = ref(0);

  const greetingText = computed(() => {
    const h = new Date().getHours();
    if (h >= 5 && h < 12) return '早上好，跑步去吧！';
    if (h >= 12 && h < 18) return '下午好，运动起来！';
    return '晚上好，注意休息！';
  });

  const greetingIcon = computed(() => {
    const h = new Date().getHours();
    if (h >= 5 && h < 12) return '☀️';
    if (h >= 12 && h < 18) return '🌤️';
    return '🌙';
  });

  const greetingSub = computed(() => '坚持运动，遇见更好的自己');

  const weeklySubTitle = computed(() => {
    const n = weeklyStats.value.runCount;
    const sun = weeklyStats.value.sunshineKm;
    if (!weeklyStats.value.hasData) return '本周暂无跑步记录';
    let s = `本周 ${n} 次跑步`;
    if (Number(sun) > 0) s += ` · 阳光跑有效 ${sun} km`;
    return s;
  });

  const weekGoalProgress = computed(() => {
    const goal = Number(runGoalKm.value) || 0;
    const dist = Number(weeklyStats.value.distanceKm) || 0;
    if (goal <= 0) return 0;
    return Math.min(100, Math.round((dist / goal) * 100));
  });

  const goalHintText = computed(() => {
    const goal = Number(runGoalKm.value) || 0;
    if (goal <= 0) return '';
    const dist = Number(weeklyStats.value.distanceKm) || 0;
    if (dist >= goal) return '本周目标已达成';
    return `本周 ${dist.toFixed(1)} / ${goal} 公里`;
  });

  const fetchDashboard = async () => {
    const res = await request({ url: '/student/home/dashboard', method: 'GET' });
    totalDistanceKm.value = res?.total_distance_km ?? '0.0';
    weeklyStats.value = mapWeeklyFromApi(res?.weekly);
    recentRuns.value = mapRecentFromApi(res?.recent_runs);
    runGoalKm.value = Number(res?.weekly_run_goal_km) || 0;
    unreadNotifyCount.value = Number(res?.unread_notify_count) || 0;
  };

  const fetchTasks = async (onNewTasks) => {
    try {
      const res = await getStudentTasks({ page: 1, size: 20 });
      const ongoing = ['pending', 'in_progress', 'uncompleted', 'not_started', 'failed'];
      teacherTasks.value = (res?.items || [])
        .filter((t) => ongoing.includes(t.status))
        .map((task) => ({
          id: task.id,
          title: task.title,
          status: task.status,
          type: task.type || 'run',
          urgent: task.urgent || false,
          desc:
            task.description ||
            (task.min_distance ? `目标: ${task.min_distance}km` : '请查看详情')
        }));
      if (typeof onNewTasks === 'function') {
        onNewTasks(teacherTasks.value);
      }
    } catch (e) {
      if (isAuthError(e)) return;
      teacherTasks.value = [];
    }
  };

  const loadDashboard = async (onNewTasks) => {
    if (!getStoredToken()) return;
    loading.value = true;
    try {
      await Promise.all([fetchDashboard(), fetchTasks(onNewTasks)]);
    } catch (e) {
      if (!isAuthError(e)) {
        console.error('[home] dashboard load failed', e);
      }
      weeklyStats.value = emptyWeekly();
      recentRuns.value = [];
    } finally {
      loading.value = false;
    }
  };

  const applyRunGoal = (km) => {
    runGoalKm.value = Number(km) || 0;
  };

  return {
    loading,
    greetingText,
    greetingIcon,
    greetingSub,
    weeklySubTitle,
    totalDistanceKm,
    weeklyStats,
    recentRuns,
    teacherTasks,
    unreadNotifyCount,
    runGoalKm,
    weekGoalProgress,
    goalHintText,
    loadDashboard,
    applyRunGoal
  };
}
