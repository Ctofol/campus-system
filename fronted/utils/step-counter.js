/**
 * 跑步专用计步：重力分离 + 步频带通（约 1.5–3.5 Hz）+ 峰谷检测。
 * 不识别「摇一摇」类三轴抖动，避免手摇误计。
 */

const MIN_CADENCE_HZ = 1.5;
const MAX_CADENCE_HZ = 3.5;
const MIN_INTERVAL_MS = Math.round(1000 / MAX_CADENCE_HZ); // ~286
const MAX_INTERVAL_MS = Math.round(1000 / MIN_CADENCE_HZ); // ~667
const DEFAULT_MIN_INTERVAL_MS = 250;
const DEFAULT_MAX_INTERVAL_MS = 700;

/**
 * @param {object} [options]
 * @param {number} [options.peakThreshold] 线性加速度峰阈值 (m/s² 量级)
 * @param {number} [options.minIntervalMs]
 * @param {number} [options.maxIntervalMs]
 */
export function createStepCounter(options = {}) {
  const peakThreshold = options.peakThreshold ?? 0.32;
  const minIntervalMs = options.minIntervalMs ?? DEFAULT_MIN_INTERVAL_MS;
  const maxIntervalMs = options.maxIntervalMs ?? DEFAULT_MAX_INTERVAL_MS;

  let steps = 0;
  let lastStepAt = 0;
  let gravityBaseline = null;
  let hpPrev = 0;
  let hp = 0;
  let bandPrev = 0;
  let band = 0;
  let wasAbove = false;
  let lastPeak = 0;
  const recentIntervals = [];

  const GRAVITY_ALPHA = 0.88;
  const HP_ALPHA = 0.82;
  const BP_ALPHA = 0.62;

  const reset = () => {
    steps = 0;
    lastStepAt = 0;
    gravityBaseline = null;
    hpPrev = 0;
    hp = 0;
    bandPrev = 0;
    band = 0;
    wasAbove = false;
    lastPeak = 0;
    recentIntervals.length = 0;
  };

  const getCadenceHz = () => {
    if (recentIntervals.length < 2) return 0;
    const avgMs = recentIntervals.reduce((a, b) => a + b, 0) / recentIntervals.length;
    return avgMs > 0 ? 1000 / avgMs : 0;
  };

  const hasStableCadence = () => {
    if (recentIntervals.length < 3) return false;
    const hz = getCadenceHz();
    return hz >= MIN_CADENCE_HZ && hz <= MAX_CADENCE_HZ;
  };

  const recordInterval = (dt) => {
    if (dt < minIntervalMs || dt > maxIntervalMs * 2) return;
    recentIntervals.push(dt);
    while (recentIntervals.length > 6) recentIntervals.shift();
  };

  /**
   * @param {number} x
   * @param {number} y
   * @param {number} z
   * @param {number} [now]
   * @returns {{ stepped: boolean, steps: number, cadenceHz: number }}
   */
  const feed = (x, y, z, now = Date.now()) => {
    const mag = Math.sqrt(x * x + y * y + z * z);
    if (!Number.isFinite(mag) || mag < 5 || mag > 25) {
      return { stepped: false, steps, cadenceHz: getCadenceHz() };
    }

    gravityBaseline =
      gravityBaseline == null ? mag : gravityBaseline * GRAVITY_ALPHA + mag * (1 - GRAVITY_ALPHA);
    const linear = mag - gravityBaseline;

    const hpRaw = HP_ALPHA * (hp + linear - hpPrev);
    hpPrev = linear;
    hp = hpRaw;

    band = BP_ALPHA * band + (1 - BP_ALPHA) * (hp - bandPrev);
    bandPrev = hp;

    const signal = Math.abs(band);
    const dynamicTh = Math.max(peakThreshold, lastPeak * 0.42);

    if (!wasAbove && signal > dynamicTh) {
      wasAbove = true;
      lastPeak = signal;
    } else if (wasAbove) {
      if (signal > lastPeak) lastPeak = signal;
      if (signal < dynamicTh * 0.55) {
        wasAbove = false;
        const dt = lastStepAt > 0 ? now - lastStepAt : maxIntervalMs;
        const inCadence =
          lastStepAt === 0 || (dt >= MIN_INTERVAL_MS && dt <= MAX_INTERVAL_MS);
        const resumeAfterPause = lastStepAt > 0 && dt > MAX_INTERVAL_MS && dt < 2200;

        if (inCadence || resumeAfterPause) {
          if (lastStepAt > 0 && dt >= minIntervalMs) {
            recordInterval(dt);
          }
          steps += 1;
          lastStepAt = now;
          lastPeak = 0;
          return { stepped: true, steps, cadenceHz: getCadenceHz() };
        }
        lastPeak = 0;
      }
    }

    return { stepped: false, steps, cadenceHz: getCadenceHz() };
  };

  return {
    feed,
    reset,
    getStepCount: () => steps,
    getCadenceHz,
    hasStableCadence,
    setStepCount: (n) => {
      steps = Math.max(0, Math.floor(Number(n) || 0));
    }
  };
}
