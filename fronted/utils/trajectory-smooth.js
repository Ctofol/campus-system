/**
 * 地图轨迹展示平滑：微信 map polyline 仅支持折线，通过 Catmull-Rom 样条插值加密点实现视觉曲线。
 * 原始 GPS 点用于里程/提交，本模块仅用于 map 展示。
 */

const EARTH_R = 6371000;

const toNum = (v) => {
  const n = Number(v);
  return Number.isFinite(n) ? n : NaN;
};

const normalizePoint = (p) => {
  if (!p || typeof p !== 'object') return null;
  const latitude = toNum(p.latitude ?? p.lat);
  const longitude = toNum(p.longitude ?? p.lng ?? p.lon);
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) return null;
  return { latitude, longitude };
};

export const haversineM = (lat1, lng1, lat2, lng2) => {
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLng / 2) ** 2;
  return 2 * EARTH_R * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
};

const dedupePoints = (points, minGapM = 0.5) => {
  if (points.length <= 1) return points;
  const out = [points[0]];
  for (let i = 1; i < points.length; i++) {
    const prev = out[out.length - 1];
    const cur = points[i];
    if (haversineM(prev.latitude, prev.longitude, cur.latitude, cur.longitude) >= minGapM) {
      out.push(cur);
    }
  }
  return out;
};

/** Douglas-Peucker 简化（长轨迹降采样） */
const douglasPeucker = (points, epsilonM) => {
  if (points.length <= 2) return points;

  const sqEpsilon = epsilonM * epsilonM;

  const perpendicularSqM = (p, a, b) => {
    const x0 = p.latitude;
    const y0 = p.longitude;
    const x1 = a.latitude;
    const y1 = a.longitude;
    const x2 = b.latitude;
    const y2 = b.longitude;
    const dx = x2 - x1;
    const dy = y2 - y1;
    if (dx === 0 && dy === 0) {
      const dlat = ((x0 - x1) * Math.PI) / 180;
      const dlng = ((y0 - y1) * Math.PI) / 180;
      return (dlat * EARTH_R) ** 2 + (dlng * EARTH_R * Math.cos((x1 * Math.PI) / 180)) ** 2;
    }
    const t = Math.max(0, Math.min(1, ((x0 - x1) * dx + (y0 - y1) * dy) / (dx * dx + dy * dy)));
    const projLat = x1 + t * dx;
    const projLng = y1 + t * dy;
    const dlat = ((x0 - projLat) * Math.PI) / 180;
    const dlng = ((y0 - projLng) * Math.PI) / 180;
    return (dlat * EARTH_R) ** 2 + (dlng * EARTH_R * Math.cos((projLat * Math.PI) / 180)) ** 2;
  };

  const recurse = (pts, start, end, keep) => {
    if (end <= start + 1) return;
    let maxSq = 0;
    let index = start;
    for (let i = start + 1; i < end; i++) {
      const sq = perpendicularSqM(pts[i], pts[start], pts[end]);
      if (sq > maxSq) {
        maxSq = sq;
        index = i;
      }
    }
    if (maxSq > sqEpsilon) {
      keep[index] = true;
      recurse(pts, start, index, keep);
      recurse(pts, index, end, keep);
    }
  };

  const keep = new Array(points.length).fill(false);
  keep[0] = true;
  keep[points.length - 1] = true;
  recurse(points, 0, points.length - 1, keep);
  return points.filter((_, i) => keep[i]);
};

const catmullRom = (p0, p1, p2, p3, t) => {
  const t2 = t * t;
  const t3 = t2 * t;
  return {
    latitude:
      0.5 *
      (2 * p1.latitude +
        (-p0.latitude + p2.latitude) * t +
        (2 * p0.latitude - 5 * p1.latitude + 4 * p2.latitude - p3.latitude) * t2 +
        (-p0.latitude + 3 * p1.latitude - 3 * p2.latitude + p3.latitude) * t3),
    longitude:
      0.5 *
      (2 * p1.longitude +
        (-p0.longitude + p2.longitude) * t +
        (2 * p0.longitude - 5 * p1.longitude + 4 * p2.longitude - p3.longitude) * t2 +
        (-p0.longitude + 3 * p1.longitude - 3 * p2.longitude + p3.longitude) * t3)
  };
};

/** 在 Catmull-Rom 段 p1→p2 上按弧长约 stepM 采样（t: 0→1 对应 p1→p2） */
const sampleCatmullSegment = (p0, p1, p2, p3, stepM) => {
  const out = [];
  let t = 0;
  let prev = { ...p1 };
  const dt = 0.02;
  while (t < 1 - 1e-6) {
    t = Math.min(1, t + dt);
    const cur = catmullRom(p0, p1, p2, p3, t);
    if (haversineM(prev.latitude, prev.longitude, cur.latitude, cur.longitude) >= stepM) {
      out.push(cur);
      prev = cur;
    }
  }
  return out;
};

const buildSmoothed = (control, stepM) => {
  const display = [{ ...control[0] }];
  for (let i = 0; i < control.length - 1; i++) {
    const p0 = control[Math.max(0, i - 1)];
    const p1 = control[i];
    const p2 = control[i + 1];
    const p3 = control[Math.min(control.length - 1, i + 2)];
    const seg = sampleCatmullSegment(p0, p1, p2, p3, stepM);
    for (const p of seg) {
      display.push(p);
    }
  }
  display[display.length - 1] = { ...control[control.length - 1] };
  return display;
};

/**
 * @param {Array} rawPoints
 * @param {{ sampleStepM?: number, maxDisplayPoints?: number, simplifyThreshold?: number, simplifyEpsilonM?: number }} options
 */
export const smoothTrajectoryForMap = (rawPoints, options = {}) => {
  let sampleStepM = options.sampleStepM ?? 3.5;
  const maxDisplayPoints = options.maxDisplayPoints ?? 1800;
  const simplifyThreshold = options.simplifyThreshold ?? 800;
  const simplifyEpsilonM = options.simplifyEpsilonM ?? 2;

  const normalized = [];
  for (const p of rawPoints || []) {
    const n = normalizePoint(p);
    if (n) normalized.push(n);
  }
  if (normalized.length === 0) return [];
  if (normalized.length === 1) return [...normalized];

  let control = dedupePoints(normalized, 0.5);
  if (control.length < 2) return control;

  if (control.length > simplifyThreshold) {
    control = douglasPeucker(control, simplifyEpsilonM);
  }
  if (control.length < 2) return control;

  let display = buildSmoothed(control, sampleStepM);

  while (display.length > maxDisplayPoints && sampleStepM < 14) {
    sampleStepM += 1;
    display = buildSmoothed(control, sampleStepM);
  }

  if (display.length > maxDisplayPoints) {
    const stride = Math.ceil(display.length / maxDisplayPoints);
    const thinned = [];
    for (let i = 0; i < display.length; i += stride) {
      thinned.push(display[i]);
    }
    if (thinned[thinned.length - 1] !== display[display.length - 1]) {
      thinned.push(display[display.length - 1]);
    }
    display = thinned;
    display[0] = { ...control[0] };
    display[display.length - 1] = { ...control[control.length - 1] };
  }

  return display.length >= 2 ? display : control;
};

export const DEFAULT_RUN_POLYLINE_STYLE = {
  color: '#1E88E5',
  width: 6,
  arrowLine: false,
  borderColor: '#FFFFFF',
  borderWidth: 2
};

export const DEFAULT_BRAND_POLYLINE_STYLE = {
  color: '#20C997',
  width: 6,
  arrowLine: false,
  borderColor: '#FFFFFF',
  borderWidth: 2
};

export const buildRunPolyline = (rawPoints, style = {}) => {
  const { smoothOptions, ...lineStyle } = style;
  const points = smoothTrajectoryForMap(rawPoints, smoothOptions || {});
  if (points.length < 2) return null;
  return { ...DEFAULT_RUN_POLYLINE_STYLE, ...lineStyle, points };
};

export const smoothTrajectoryFromRaw = (raw, options = {}) => {
  if (raw == null) return [];
  let arr = raw;
  if (typeof raw === 'string') {
    try {
      arr = JSON.parse(raw);
    } catch {
      return [];
    }
  }
  if (!Array.isArray(arr)) return [];
  return smoothTrajectoryForMap(arr, options);
};
