// 定位工具类 - 封装统一的定位逻辑
// 优先 App 端优化

export const getCurrentLocation = (options = {}) => {
  return new Promise((resolve, reject) => {
    // 默认配置
    const config = {
      type: 'gcj02', // 默认 gcj02，兼容性好
      isHighAccuracy: true, // 开启高精度
      timeout: 15000, // 超时 15秒（增加超时时间）
      altitude: true, // 传入 true 会返回高度信息，由于获取高度需要较高精确度，会减慢接口返回速度
      ...options
    };

    uni.getLocation({
      type: config.type,
      isHighAccuracy: config.isHighAccuracy,
      highAccuracyExpireTime: 5000, // 高精度定位超时时间(ms)，增加到5秒
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
        }
        else {
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

