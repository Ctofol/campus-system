/**
 * Minimal GPS helpers for running.
 * Real location updates are accepted unless they are clearly impossible.
 */

let bearingHistory = [];

export const resetRunGpsRawWindow = () => {
  bearingHistory = [];
};

export const pushRunGpsRawSample = () => {};

export const recordAcceptedSegment = (bearing, speed) => {
  if (!Number.isFinite(bearing)) return;
  bearingHistory.push(bearing);
  if (bearingHistory.length > 4) bearingHistory.shift();
};

export const haversineM = (lat1, lng1, lat2, lng2) => {
  const R = 6371e3;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLng / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
};

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

export const isGpsClusterStationary = () => false;

export const shouldRejectMileageSegment = ({ segmentM, timeDiffS }) => {
  if (!Number.isFinite(segmentM) || segmentM <= 0) return true;
  const speed = segmentM / Math.max(Number(timeDiffS) || 0, 0.001);
  return speed > 12 || (segmentM > 50 && timeDiffS < 2);
};

export const computeDynamicMinDistanceM = () => 0.5;

export const getDirectionReversalStatus = () => 'none';
