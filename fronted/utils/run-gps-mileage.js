/**
 * 跑步里程：静止漂移识别、脏点剔除、动态最小位移（非单一硬阈值）
 */

const RAW_WINDOW_MS = 14000;
const RAW_WINDOW_MAX = 10;

/** @type {{ lat: number, lng: number, ts: number }[]} */
let rawWindow = [];

export const resetRunGpsRawWindow = () => {
  rawWindow = [];
};

/**
 * @param {number} lat
 * @param {number} lng
 * @param {number} ts
 */
export const pushRunGpsRawSample = (lat, lng, ts) => {
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) return;
  rawWindow.push({ lat, lng, ts });
  const cutoff = ts - RAW_WINDOW_MS;
  while (rawWindow.length > 0 && rawWindow[0].ts < cutoff) {
    rawWindow.shift();
  }
  while (rawWindow.length > RAW_WINDOW_MAX) {
    rawWindow.shift();
  }
};

/**
 * Haversine 米
 */
export const haversineM = (lat1, lng1, lat2, lng2) => {
  const R = 6371e3;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLng / 2) *
      Math.sin(dLng / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
};

/**
 * 近期原始点是否聚成一团（站着不动但 GPS 在跳）
 * @param {object} ctx
 * @param {boolean} ctx.hasRecentStepMotion
 * @param {boolean} ctx.hasStrongStepMotion
 */
export const isGpsClusterStationary = (ctx) => {
  if (ctx.hasStrongStepMotion || ctx.hasRecentStepMotion) return false;
  if (rawWindow.length < 4) return false;
  const span = rawWindow[rawWindow.length - 1].ts - rawWindow[0].ts;
  if (span < 2500) return false;

  let sumLat = 0;
  let sumLng = 0;
  for (const p of rawWindow) {
    sumLat += p.lat;
    sumLng += p.lng;
  }
  const n = rawWindow.length;
  const cLat = sumLat / n;
  const cLng = sumLng / n;
  let maxR = 0;
  let pathSum = 0;
  for (let i = 0; i < n; i++) {
    const p = rawWindow[i];
    maxR = Math.max(maxR, haversineM(cLat, cLng, p.lat, p.lng));
    if (i > 0) {
      pathSum += haversineM(rawWindow[i - 1].lat, rawWindow[i - 1].lng, p.lat, p.lng);
    }
  }
  // 半径小但折线累加高 → 典型静止漂移
  if (maxR <= 22 && pathSum >= 8) return true;
  if (maxR <= 14 && pathSum >= 4) return true;
  return false;
};

/**
 * 本段是否应拒绝计入里程（瞬移 / 静止尖峰 / 极差精度）
 */
export const shouldRejectMileageSegment = ({
  segmentM,
  timeDiffS,
  speedMps,
  accuracyM,
  hasRecentStepMotion,
  hasStrongStepMotion,
  hasRecentGpsMotionEvidence,
  runUnlocked
}) => {
  if (!Number.isFinite(segmentM) || segmentM <= 0) return true;
  const dt = Math.max(timeDiffS, 0.001);
  const v = segmentM / dt;

  if (Number.isFinite(accuracyM) && accuracyM > 95 && !hasRecentStepMotion && !hasStrongStepMotion) {
    return true;
  }

  if (v > 12 && !hasStrongStepMotion) return true;
  if (segmentM > 45 && dt < 8 && !hasStrongStepMotion) return true;
  if (segmentM > 28 && dt < 3 && !hasRecentStepMotion && !hasRecentGpsMotionEvidence) return true;

  if (
    !hasRecentStepMotion &&
    !hasStrongStepMotion &&
    !runUnlocked &&
    segmentM >= 5 &&
    segmentM <= 18 &&
    v < 0.35 &&
    Number.isFinite(accuracyM) &&
    accuracyM > 25
  ) {
    return true;
  }

  if (
    isGpsClusterStationary({
      hasRecentStepMotion,
      hasStrongStepMotion
    }) &&
    segmentM < 20
  ) {
    return true;
  }

  return false;
};

/**
 * 动态最小位移（米）：精度越差要求位移越大，有步频则降低
 */
export const computeDynamicMinDistanceM = ({
  accuracyM,
  runUnlocked,
  coldPhase,
  tierMinDistance,
  recentStepMotion,
  hasStrongStepMotion,
  stableCadence,
  hasRecentGpsMotionEvidence
}) => {
  let minD = runUnlocked ? 0.55 : coldPhase ? 0.95 : 0.75;
  minD = Math.max(minD, tierMinDistance);

  if (Number.isFinite(accuracyM) && accuracyM > 8) {
    const factor = runUnlocked ? 0.12 : recentStepMotion ? 0.14 : 0.2;
    const cap = runUnlocked ? 4.2 : recentStepMotion ? 5.5 : 8;
    minD = Math.max(minD, Math.min(accuracyM * factor, cap));
  }

  if (recentStepMotion && !runUnlocked) {
    minD = Math.min(minD, stableCadence ? 0.85 : 1.0);
  }
  if (runUnlocked && (stableCadence || hasStrongStepMotion)) {
    minD = Math.min(minD, stableCadence ? 1.35 : 1.65);
    minD *= 0.9;
  }
  if (!runUnlocked && stableCadence && hasRecentGpsMotionEvidence) {
    minD = Math.min(minD, 0.9);
  }

  return minD;
};
