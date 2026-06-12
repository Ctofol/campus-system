/**
 * 按段配速为地图 polyline 上色（慢红 → 快绿）
 */
import { haversineM, smoothTrajectoryForMap, DEFAULT_RUN_POLYLINE_STYLE } from './trajectory-smooth.js';

const PACE_SLOW = 14;
const PACE_FAST = 4;

const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

const lerp = (a, b, t) => a + (b - a) * t;

const hexByte = (n) => {
  const v = Math.round(clamp(n, 0, 255));
  return v.toString(16).padStart(2, '0');
};

/** pace min/km → #RRGGBB */
export const paceToColor = (paceMinPerKm) => {
  if (!Number.isFinite(paceMinPerKm) || paceMinPerKm <= 0) {
    return DEFAULT_RUN_POLYLINE_STYLE.color;
  }
  const p = clamp(paceMinPerKm, PACE_FAST, PACE_SLOW);
  const t = (p - PACE_FAST) / (PACE_SLOW - PACE_FAST);
  let r;
  let g;
  let b;
  if (t < 0.5) {
    const u = t / 0.5;
    r = lerp(0x4c, 0xff, u);
    g = lerp(0xaf, 0xc1, u);
    b = lerp(0x50, 0x07, u);
  } else {
    const u = (t - 0.5) / 0.5;
    r = lerp(0xff, 0xff, u);
    g = lerp(0xc1, 0x52, u);
    b = lerp(0x07, 0x52, u);
  }
  return `#${hexByte(r)}${hexByte(g)}${hexByte(b)}`;
};

const normalizeRawPoint = (p) => {
  if (!p || typeof p !== 'object') return null;
  const latitude = Number(p.latitude ?? p.lat);
  const longitude = Number(p.longitude ?? p.lng ?? p.lon);
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) return null;
  const timestamp = p.timestamp != null ? Number(p.timestamp) : null;
  const speed = p.speed != null ? Number(p.speed) : null;
  return { latitude, longitude, timestamp, speed };
};

const segmentPaceMinPerKm = (a, b) => {
  const v = b.speed;
  if (Number.isFinite(v) && v > 0.15 && v < 12) {
    const kmh = v * 3.6;
    return 60 / kmh;
  }
  const t0 = a.timestamp;
  const t1 = b.timestamp;
  if (t0 != null && t1 != null && t1 > t0) {
    const dt = (t1 - t0) / 1000;
    const d = haversineM(a.latitude, a.longitude, b.latitude, b.longitude);
    if (d >= 0.5 && dt > 0.2) {
      const km = d / 1000;
      return km > 0 ? dt / 60 / km : null;
    }
  }
  return null;
};

/**
 * @param {object[]} rawPoints
 * @param {object} [options]
 * @returns {object[]}
 */
export const buildPaceColoredPolylines = (rawPoints, options = {}) => {
  const pts = (rawPoints || []).map(normalizeRawPoint).filter(Boolean);
  if (pts.length < 2) return [];

  const lineStyle = {
    width: options.width ?? DEFAULT_RUN_POLYLINE_STYLE.width,
    arrowLine: options.arrowLine ?? false,
    borderColor: options.borderColor ?? DEFAULT_RUN_POLYLINE_STYLE.borderColor,
    borderWidth: options.borderWidth ?? DEFAULT_RUN_POLYLINE_STYLE.borderWidth
  };
  const maxSegments = options.maxSegments ?? 120;
  const smoothSegment = options.smoothSegment !== false;

  const segments = [];
  for (let i = 0; i < pts.length - 1; i++) {
    const a = pts[i];
    const b = pts[i + 1];
    const pace = segmentPaceMinPerKm(a, b);
    segments.push({
      pace: pace != null && pace > 0 && pace < 99 ? pace : PACE_SLOW * 0.65,
      points: [a, b]
    });
  }

  if (!segments.length) return [];

  const bucketSize = Math.max(1, Math.ceil(segments.length / maxSegments));
  const merged = [];
  for (let i = 0; i < segments.length; i += bucketSize) {
    const chunk = segments.slice(i, i + bucketSize);
    const paceAvg = chunk.reduce((s, c) => s + c.pace, 0) / chunk.length;
    const points = [chunk[0].points[0]];
    chunk.forEach((c) => points.push(c.points[1]));
    merged.push({ pace: paceAvg, points });
  }

  return merged
    .map((seg) => {
      let drawPts = seg.points;
      if (smoothSegment && drawPts.length >= 2) {
        drawPts = smoothTrajectoryForMap(drawPts, { maxDisplayPoints: 80 });
      }
      if (drawPts.length < 2) return null;
      return {
        ...lineStyle,
        color: paceToColor(seg.pace),
        points: drawPts
      };
    })
    .filter(Boolean);
};
