/**
 * Motion-pulse counter for a hand-held phone.
 * One deliberate shake or walking impact counts once; tiny idle sensor noise does not.
 */

const DEFAULT_MIN_INTERVAL_MS = 260;
const DEFAULT_MOTION_THRESHOLD = 0.04;
const QUIET_RESET_MS = 100;

export function createStepCounter(options = {}) {
  const minIntervalMs = options.minIntervalMs ?? DEFAULT_MIN_INTERVAL_MS;
  const motionThreshold = options.motionThreshold ?? DEFAULT_MOTION_THRESHOLD;

  let steps = 0;
  let lastStepAt = 0;
  let lastSample = null;
  let gravityBaseline = null;
  let motionLatched = false;
  let quietSince = 0;
  const recentIntervals = [];

  const reset = () => {
    steps = 0;
    lastStepAt = 0;
    lastSample = null;
    gravityBaseline = null;
    motionLatched = false;
    quietSince = 0;
    recentIntervals.length = 0;
  };

  const getCadenceHz = () => {
    if (!recentIntervals.length) return 0;
    const avg = recentIntervals.reduce((sum, value) => sum + value, 0) / recentIntervals.length;
    return avg > 0 ? 1000 / avg : 0;
  };

  const recordInterval = (interval) => {
    if (interval < minIntervalMs || interval > 2200) return;
    recentIntervals.push(interval);
    if (recentIntervals.length > 6) recentIntervals.shift();
  };

  const feed = (x, y, z, now = Date.now()) => {
    const magnitude = Math.sqrt(x * x + y * y + z * z);
    if (!Number.isFinite(magnitude)) {
      return { stepped: false, steps, cadenceHz: getCadenceHz() };
    }

    const vectorDelta = lastSample
      ? Math.sqrt((x - lastSample.x) ** 2 + (y - lastSample.y) ** 2 + (z - lastSample.z) ** 2)
      : 0;
    lastSample = { x, y, z };
    gravityBaseline = gravityBaseline == null ? magnitude : gravityBaseline * 0.9 + magnitude * 0.1;
    const gravityDelta = Math.abs(magnitude - gravityBaseline);
    const motion = Math.max(vectorDelta, gravityDelta);

    if (motion < motionThreshold) {
      if (motionLatched) {
        if (!quietSince) quietSince = now;
        if (now - quietSince >= QUIET_RESET_MS) motionLatched = false;
      }
      return { stepped: false, steps, cadenceHz: getCadenceHz() };
    }

    quietSince = 0;
    if (motionLatched || (lastStepAt && now - lastStepAt < minIntervalMs)) {
      return { stepped: false, steps, cadenceHz: getCadenceHz() };
    }

    if (lastStepAt) recordInterval(now - lastStepAt);
    steps += 1;
    lastStepAt = now;
    motionLatched = true;
    return { stepped: true, steps, cadenceHz: getCadenceHz() };
  };

  return {
    feed,
    reset,
    getStepCount: () => steps,
    getCadenceHz,
    hasStableCadence: () => getCadenceHz() >= 0.7 && getCadenceHz() <= 4.5,
    setStepCount: (value) => {
      steps = Math.max(0, Math.floor(Number(value) || 0));
    }
  };
}
