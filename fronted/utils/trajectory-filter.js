/**
 * 计程轨迹轻量滤波：2D 卡尔曼 + 短窗中值，抑制单点 GPS 跳变。
 * 仅用于写入 trajectoryPoints 的坐标，展示层仍走 trajectory-smooth。
 */

/**
 * @param {object} [options]
 * @param {number} [options.medianWindow] 中值窗口长度（≥3 时启用）
 * @param {number} [options.processNoise] 过程噪声
 * @param {number} [options.measurementNoiseBase] 测量噪声基数（随精度放大）
 */
export function createTrajectoryFilter(options = {}) {
  const medianWindow = Math.max(1, options.medianWindow ?? 3);
  const processNoise = options.processNoise ?? 2e-8;
  const measurementNoiseBase = options.measurementNoiseBase ?? 8e-8;

  let initialized = false;
  let estLat = 0;
  let estLng = 0;
  let variance = 1;
  const recent = [];

  const reset = () => {
    initialized = false;
    variance = 1;
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

    const rScale =
      Number.isFinite(accuracyM) && accuracyM > 0
        ? Math.max(1, Math.pow(accuracyM / 18, 2))
        : 1;
    const measurementNoise = measurementNoiseBase * rScale;

    variance += processNoise;
    const gain = variance / (variance + measurementNoise);
    estLat += gain * (latIn - estLat);
    estLng += gain * (lngIn - estLng);
    variance *= 1 - gain;

    recent.push({ latitude: estLat, longitude: estLng });
    while (recent.length > medianWindow) recent.shift();

    if (recent.length < 3 || medianWindow < 3) {
      return { latitude: estLat, longitude: estLng };
    }

    const mid = Math.floor(recent.length / 2);
    const lats = recent.map((p) => p.latitude).sort((a, b) => a - b);
    const lngs = recent.map((p) => p.longitude).sort((a, b) => a - b);
    return { latitude: lats[mid], longitude: lngs[mid] };
  };

  return { filter, reset };
}
