/**
 * 跑步里程：静止漂移识别、脏点剔除、动态最小位移、方向反转惩罚
 */

const RAW_WINDOW_MS = 14000;
const RAW_WINDOW_MAX = 10;

/** @type {{ lat: number, lng: number, ts: number }[]} */
let rawWindow = [];

/** 方向历史：最近若干已接受段的方位角（度），用于反转检测 */
let bearingHistory = [];
const BEARING_HISTORY_MAX = 4;
const REVERSAL_ANGLE_DEG = 120;

/** 速度历史：最近若干段的速度 (m/s)，用于尖峰检测 */
let speedHistory = [];
const SPEED_HISTORY_MAX = 5;

export const resetRunGpsRawWindow = () => {
  rawWindow = [];
  bearingHistory = [];
  speedHistory = [];
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
 * 记录一段已被接受的里程的方向和速度
 */
export const recordAcceptedSegment = (bearingDeg, speedMps) => {
  if (Number.isFinite(bearingDeg)) {
    bearingHistory.push(bearingDeg);
    while (bearingHistory.length > BEARING_HISTORY_MAX) bearingHistory.shift();
  }
  if (Number.isFinite(speedMps) && speedMps > 0) {
    speedHistory.push(speedMps);
    while (speedHistory.length > SPEED_HISTORY_MAX) speedHistory.shift();
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
 * 计算方位角（度）：从点1到点2
 */
export const bearingDeg = (lat1, lng1, lat2, lng2) => {
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const rLat1 = (lat1 * Math.PI) / 180;
  const rLat2 = (lat2 * Math.PI) / 180;
  const y = Math.sin(dLng) * Math.cos(rLat2);
  const x =
    Math.cos(rLat1) * Math.sin(rLat2) -
    Math.sin(rLat1) * Math.cos(rLat2) * Math.cos(dLng);
  return ((Math.atan2(y, x) * 180) / Math.PI + 360) % 360;
};

/**
 * 两个方位角的差值（取锐角）
 */
const angleDiff = (a, b) => {
  let d = Math.abs(a - b) % 360;
  if (d > 180) d = 360 - d;
  return d;
};

/**
 * 检测当前方向是否与最近趋势相反（典型漂移抖动特征）
 */
const isDirectionReversal = (currentBearingDeg) => {
  if (bearingHistory.length < 2) return false;
  const recentAvg = bearingHistory.reduce((s, v) => s + v, 0) / bearingHistory.length;
  return angleDiff(currentBearingDeg, recentAvg) > REVERSAL_ANGLE_DEG;
};

/**
 * 检测速度尖峰：当前速度远超近期均值（GPS 瞬移特征）
 */
const isSpeedSpike = (currentSpeedMps) => {
  if (speedHistory.length < 3) return false;
  const avg = speedHistory.reduce((s, v) => s + v, 0) / speedHistory.length;
  return currentSpeedMps > avg * 3.5 && currentSpeedMps > 3;
};

/**
 * 近期原始点是否聚成一团（站着不动但 GPS 在跳）
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
  if (maxR <= 22 && pathSum >= 8) return true;
  if (maxR <= 14 && pathSum >= 4) return true;
  return false;
};

/**
 * 检测原始 GPS 窗口是否呈现高频小幅度抖动（典型静止漂移）
 * 与 isGpsClusterStationary 互补：后者看空间聚集，这个看振荡模式
 */
const isGpsJitterOscillation = () => {
  if (rawWindow.length < 5) return false;
  const span = rawWindow[rawWindow.length - 1].ts - rawWindow[0].ts;
  if (span < 4000 || span > RAW_WINDOW_MS) return false;

  let directionChanges = 0;
  for (let i = 2; i < rawWindow.length; i++) {
    const prevBearing = bearingDeg(
      rawWindow[i - 2].lat, rawWindow[i - 2].lng,
      rawWindow[i - 1].lat, rawWindow[i - 1].lng
    );
    const curBearing = bearingDeg(
      rawWindow[i - 1].lat, rawWindow[i - 1].lng,
      rawWindow[i].lat, rawWindow[i].lng
    );
    if (angleDiff(prevBearing, curBearing) > 100) directionChanges++;
  }

  if (directionChanges < 2) return false;

  let sumDist = 0;
  for (let i = 1; i < rawWindow.length; i++) {
    sumDist += haversineM(rawWindow[i - 1].lat, rawWindow[i - 1].lng, rawWindow[i].lat, rawWindow[i].lng);
  }
  const avgDistPerPoint = sumDist / (rawWindow.length - 1);
  // 平均每点位移小但方向频繁变化 → 振荡漂移
  return avgDistPerPoint < 6 && directionChanges >= 3;
};

/**
 * 本段是否应拒绝计入里程
 */
export const shouldRejectMileageSegment = ({
  segmentM,
  timeDiffS,
  speedMps,
  accuracyM,
  hasRecentStepMotion,
  hasStrongStepMotion,
  hasRecentGpsMotionEvidence,
  runUnlocked,
  bearingDeg: segmentBearingDeg
}) => {
  if (!Number.isFinite(segmentM) || segmentM <= 0) return true;
  const dt = Math.max(timeDiffS, 0.001);
  const v = segmentM / dt;

  // 极差精度 + 无步频 → 直接丢弃
  if (Number.isFinite(accuracyM) && accuracyM > 95 && !hasRecentStepMotion && !hasStrongStepMotion) {
    return true;
  }

  // 无步频时的速度/距离尖峰
  if (v > 12 && !hasStrongStepMotion) return true;
  if (segmentM > 45 && dt < 8 && !hasStrongStepMotion) return true;
  if (segmentM > 28 && dt < 3 && !hasRecentStepMotion && !hasRecentGpsMotionEvidence) return true;

  // 低速长位移：有位移但无步频 → 漂移
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

  // 静止聚簇检测
  if (
    isGpsClusterStationary({
      hasRecentStepMotion,
      hasStrongStepMotion
    }) &&
    segmentM < 20
  ) {
    return true;
  }

  // 方向反转检测：无步频时方向突然掉头
  if (
    !hasRecentStepMotion &&
    !hasStrongStepMotion &&
    Number.isFinite(segmentBearingDeg) &&
    isDirectionReversal(segmentBearingDeg)
  ) {
    return true;
  }

  // 速度尖峰检测：远超近期均值
  if (
    !hasStrongStepMotion &&
    isSpeedSpike(v)
  ) {
    return true;
  }

  // 高频振荡漂移：原始 GPS 在频繁变向
  if (
    !hasRecentStepMotion &&
    !hasStrongStepMotion &&
    isGpsJitterOscillation()
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

export const getDirectionReversalStatus = () => {
  if (bearingHistory.length < 2) return 'none';
  const recent = bearingHistory.slice(-3);
  let changes = 0;
  for (let i = 1; i < recent.length; i++) {
    if (angleDiff(recent[i], recent[i - 1]) > 80) changes++;
  }
  if (changes >= 2) return 'oscillating';
  return 'none';
};
