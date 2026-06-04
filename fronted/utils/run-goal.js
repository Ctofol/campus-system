import { request } from '@/utils/request.js';

/** 保存本周跑步目标（公里），0 表示清除 */
export async function saveRunGoalKm(km) {
  const n = Number(km);
  const weekly_goal_km = Number.isFinite(n) && n > 0 ? Math.min(999, Math.round(n * 10) / 10) : 0;
  const res = await request({
    url: '/student/home/run-goal',
    method: 'PUT',
    data: { weekly_goal_km }
  });
  return res?.weekly_run_goal_km ?? weekly_goal_km;
}
