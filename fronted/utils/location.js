// 定位工具类 - 封装统一的定位逻辑
// 优先 App 端优化

const LAST_LOC_KEY = 'lastLocation';
const LAST_LOC_MAX_AGE_MS = 30 * 60 * 1000;

/** 进入首页等场景时静默预热 GPS，减轻跑步页「定位太慢」体感 */
export const warmUpLocationCache = (options = {}) => {
  const last = uni.getStorageSync(LAST_LOC_KEY);
  const ts = last && last.ts ? Number(last.ts) : 0;
  if (last && last.lat != null && last.lng != null && Date.now() - ts < LAST_LOC_MAX_AGE_MS) {
    return Promise.resolve(last);
  }
  return getCurrentLocation({ fastFix: true, timeout: 12000, ...options })
    .then((res) => {
      if (res && res.success) {
        uni.setStorageSync(LAST_LOC_KEY, {
          lat: res.latitude,
          lng: res.longitude,
          ts: Date.now()
        });
      }
      return res;
    })
    .catch(() => null);
};

export const getCurrentLocation = (options = {}) => {
  return new Promise((resolve, reject) => {
    const useFastFix = options.fastFix === true;
    // 默认配置
    const config = {
      type: 'gcj02', // 默认 gcj02，兼容性好
      isHighAccuracy: !useFastFix,
      timeout: 8000,
      highAccuracyExpireTime: useFastFix ? 3000 : 5000,
      // 高度会拖慢真机 getLocation，易导致轮询兜底超时、里程不涨；跑步里程不依赖海拔
      altitude: false,
      ...options
    };
    delete config.fastFix;
    // #ifdef MP-WEIXIN
    if (useFastFix) {
      if (options.timeout == null) config.timeout = 14000;
    } else if (options.timeout == null) {
      config.timeout = 22000;
      if (options.highAccuracyExpireTime == null) config.highAccuracyExpireTime = 14000;
    }
    // #endif

    uni.getLocation({
      type: config.type,
      isHighAccuracy: config.isHighAccuracy,
      highAccuracyExpireTime: config.highAccuracyExpireTime,
      altitude: config.altitude,
      timeout: config.timeout,
      success: (res) => {
        console.log('定位成功:', res);
        resolve({
          success: true,
          latitude: res.latitude,
          longitude: res.longitude,
          speed: res.speed,
          accuracy: res.accuracy,
          altitude: res.altitude,
          direction: res.direction,
          originalRes: res
        });
      },
      fail: (err) => {
        console.error('定位失败:', err);
        // 错误分析
        let errorType = 'system'; // system, permission, timeout
        let errorMsg = '定位失败';

        const errMsg = err.errMsg || '';
        const errCode = err.code || 0; // uni-app docs say errCode is sometimes available

        // 权限判断 (App/小程序)
        if (
          errMsg.includes('auth') ||
          errMsg.includes('denied') ||
          errMsg.includes('permission') ||
          errCode === 12 // App端 12: lacking permission
        ) {
          errorType = 'permission';
          errorMsg = '定位权限被拒绝，请前往设置开启';
        }
        // 超时判断
        else if (errMsg.includes('timeout')) {
          errorType = 'timeout';
          errorMsg = '定位超时，请检查网络或GPS信号';
        }
        // 系统服务判断
        else if (errMsg.includes('service') || errMsg.includes('unavailable')) {
          errorType = 'system';
          errorMsg = '定位服务不可用，请检查手机GPS开关';
        } else {
          errorMsg = `定位失败: ${errMsg}`;
        }

        reject({
          success: false,
          type: errorType,
          message: errorMsg,
          originalErr: err
        });
      }
    });
  });
};
