/**
 * 跑步轨迹轻量滤波：短窗中值 + 自适应低通。
 *
 * 不使用“对旧估计值取中值”的方式，那种做法会让三个
 * 样本的跑步路线明显滞后，在操场往返时特别容易被画成直线。
 * 滤波输出只用于展示、轨迹与里程的坐标稳定化，不会换算或虚构任何距离。
 */

/**
 * @param {object} [options]
 * @param {number} [options.medianWindow] 中值窗口长度（≥3 时启用）
 * @param {number} [options.processNoise] 过程噪声
 * @param {number} [options.measurementNoiseBase] 测量噪声基数（随精度放大）
 */
export function createTrajectoryFilter(options = {}) {
  const medianWindow = Math.max(1, options.medianWindow ?? 3);
  const baseAlpha = options.baseAlpha ?? 0.72;

  let initialized = false;
  let estLat = 0;
  let estLng = 0;
  const recent = [];

  const reset = () => {
    initialized = false;
    recent.length = 0;
  };

  /**
   * @param {number} latIn
   * @param {number} lngIn
   * @param {number} [accuracyM] 水平精度（米），越大越不信测量
   * @returns {{ latitude: number, longitude: number }}
   */
  const filter = (latIn, lngIn, accuracyM = NaN) => {
    if (!Number.isFinite(latIn) || !Number.isFinite(lngIn)) {
      return { latitude: latIn, longitude: lngIn };
    }

    if (!initialized) {
      estLat = latIn;
      estLng = lngIn;
      initialized = true;
      recent.push({ latitude: latIn, longitude: lngIn });
      return { latitude: latIn, longitude: lngIn };
    }

    recent.push({ latitude: latIn, longitude: lngIn });
    while (recent.length > medianWindow) recent.shift();

    const mid = Math.floor(recent.length / 2);
    const lats = recent.map((p) => p.latitude).sort((a, b) => a - b);
    const lngs = recent.map((p) => p.longitude).sort((a, b) => a - b);
    const targetLat = lats[mid];
    const targetLng = lngs[mid];

    // 精度越差越平滑，但保留最小跟随速度，避免人已经转弯而箭头还留在旧路段。
    const accuracyFactor = Number.isFinite(accuracyM) && accuracyM > 0
      ? Math.max(0.38, Math.min(1, 14 / accuracyM))
      : 1;
    const alpha = Math.max(0.38, Math.min(0.82, baseAlpha * accuracyFactor));
    estLat += alpha * (targetLat - estLat);
    estLng += alpha * (targetLng - estLng);
    return { latitude: estLat, longitude: estLng };
  };

  return { filter, reset };
}
