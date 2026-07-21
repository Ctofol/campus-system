import { haversineM } from './trajectory-smooth.js';

const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

// A compact pace series for result/history charts. It visualizes measured
// segment pace and never participates in distance calculation.
export const buildRunPaceSeries = (points, maxSamples = 32) => {
  const raw = Array.isArray(points) ? points : [];
  const series = [];
  let anchorIndex = 0;
  for (let index = 1; index < raw.length; index += 1) {
    const start = raw[anchorIndex];
    const end = raw[index];
    const startMs = Number(start?.timestamp);
    const endMs = Number(end?.timestamp);
    if (!Number.isFinite(startMs) || !Number.isFinite(endMs) || endMs <= startMs) continue;
    const seconds = (endMs - startMs) / 1000;
    const meters = haversineM(start.latitude, start.longitude, end.latitude, end.longitude);
    // A pace sample needs enough time and displacement to suppress GPS jitter.
    if (seconds < 5 || meters < 7) continue;
    const pace = (seconds / 60) / (meters / 1000);
    if (!Number.isFinite(pace) || pace < 2.5 || pace > 25) continue;
    series.push({ index, pace: Number(clamp(pace, 2.5, 25).toFixed(2)) });
    anchorIndex = index;
  }
  if (series.length <= maxSamples) return series;
  const stride = Math.ceil(series.length / maxSamples);
  return series.filter((_, index) => index % stride === 0 || index === series.length - 1);
};
