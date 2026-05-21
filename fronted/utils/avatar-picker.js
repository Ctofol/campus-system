/**
 * 微信小程序换头像：相册/拍照选图（chooseImage）
 * 须在公众平台隐私指引中声明「选中的照片或视频」「摄像头」，而非「用户信息-头像」。
 */

const PRIVACY_HINT =
  '换头像使用相册/拍照，请在微信公众平台 → 设置 → 服务内容声明 → 用户隐私保护指引中勾选：\n\n' +
  '· 选中的照片或视频（必选）\n' +
  '· 摄像头（若允许拍照）\n\n' +
  '无需勾选「用户信息」里的头像。保存后约 5 分钟生效；开发工具可「清除模拟器缓存-清除授权数据」后重试。';

const isPrivacyScopeError = (errMsg = '') => {
  const m = String(errMsg);
  return (
    m.includes('privacy') ||
    m.includes('隐私') ||
    m.includes('scope is not declared') ||
    m.includes('api scope is not declared')
  );
};

const isUserCancel = (err) => {
  const errMsg = (err && err.errMsg) || (err && err.message) || '';
  return String(errMsg).includes('cancel') || err === 'cancel';
};

/** 调用 chooseImage 前先走微信隐私授权（与课程上传页一致） */
export const ensureWeixinPrivacyAuthorized = () => {
  return new Promise((resolve, reject) => {
    // #ifdef MP-WEIXIN
    if (typeof wx === 'undefined' || typeof wx.getPrivacySetting !== 'function') {
      resolve();
      return;
    }
    wx.getPrivacySetting({
      success: (res) => {
        if (!res.needAuthorization) {
          resolve();
          return;
        }
        if (typeof wx.requirePrivacyAuthorize !== 'function') {
          reject(new Error('need privacy authorization'));
          return;
        }
        wx.requirePrivacyAuthorize({
          success: () => resolve(),
          fail: (err) => reject(err || new Error('privacy authorize fail'))
        });
      },
      fail: () => resolve()
    });
    // #endif
    // #ifndef MP-WEIXIN
    resolve();
    // #endif
  });
};

/** 可取消的说明弹窗，不阻塞返回上一页 */
export const showPrivacyConfigModal = (extra = '') => {
  return new Promise((resolve) => {
    uni.showModal({
      title: '相册接口未生效',
      content: PRIVACY_HINT + (extra ? `\n\n${extra}` : ''),
      confirmText: '查看协议',
      cancelText: '稍后再说',
      success: (res) => {
        if (res.confirm && typeof wx !== 'undefined' && wx.openPrivacyContract) {
          wx.openPrivacyContract({ complete: () => resolve(false) });
        } else {
          resolve(false);
        }
      },
      fail: () => resolve(false)
    });
  });
};

/**
 * 正方形裁剪（微信原生裁剪页，带 1:1 取景框，可拖动缩放）
 * 基础库 2.26+；不支持时回退为原图
 */
export const cropAvatarSquare = (src) => {
  if (!src) return Promise.reject(new Error('no image'));

  return new Promise((resolve, reject) => {
    const onFail = (err) => {
      if (isUserCancel(err)) {
        reject(Object.assign(err || new Error('cancel'), { cancelled: true }));
        return;
      }
      console.warn('avatar crop unavailable, use original', err);
      resolve(src);
    };

    // #ifdef MP-WEIXIN
    if (typeof wx !== 'undefined' && typeof wx.cropImage === 'function') {
      wx.cropImage({
        src,
        cropScale: '1:1',
        success: (res) => resolve(res.tempFilePath || src),
        fail: onFail
      });
      return;
    }
    // #endif

    // #ifdef APP-PLUS
    if (typeof uni.cropImage === 'function') {
      uni.cropImage({
        src,
        cropScale: '1:1',
        success: (res) => resolve(res.tempFilePath || src),
        fail: onFail
      });
      return;
    }
    // #endif

    resolve(src);
  });
};

/**
 * 相册/拍照选图，可选进入方形裁剪（默认开启）
 * @param {{ crop?: boolean }} options
 */
export const pickAvatarFromAlbum = async (options = {}) => {
  const { crop = true } = options;

  try {
    await ensureWeixinPrivacyAuthorized();
  } catch (e) {
    await showPrivacyConfigModal('请先在首页同意《用户隐私保护指引》');
    throw Object.assign(new Error('privacy not authorized'), { type: 'privacy' });
  }

  const filePath = await new Promise((resolve, reject) => {
    uni.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const path = res.tempFilePaths && res.tempFilePaths[0];
        if (path) resolve(path);
        else reject(new Error('未选择图片'));
      },
      fail: (err) => {
        if (isUserCancel(err)) {
          reject(Object.assign(err || new Error('cancel'), { cancelled: true }));
          return;
        }
        const errMsg = (err && err.errMsg) || '';
        if (isPrivacyScopeError(errMsg)) {
          showPrivacyConfigModal(errMsg).finally(() => {
            reject(Object.assign(err, { type: 'privacy' }));
          });
          return;
        }
        uni.showToast({ title: '打开相册失败', icon: 'none' });
        reject(err);
      }
    });
  });

  if (!crop) return filePath;
  return cropAvatarSquare(filePath);
};

/** chooseAvatar 按钮 @error（若页面仍使用 open-type="chooseAvatar"） */
export const onChooseAvatarButtonError = (event, onPicked) => {
  const errMsg = (event && event.detail && event.detail.errMsg) || '';
  console.warn('chooseAvatar error:', errMsg);
  if (!isPrivacyScopeError(errMsg)) {
    uni.showToast({ title: '打开头像选择失败', icon: 'none' });
    return;
  }
  uni.showModal({
    title: '请使用相册换头像',
    content: PRIVACY_HINT + '\n\n是否改用相册选图？',
    confirmText: '用相册',
    cancelText: '稍后再说',
    success: (res) => {
      if (res.confirm) {
        pickAvatarFromAlbum()
          .then((fp) => {
            if (typeof onPicked === 'function') onPicked(fp);
          })
          .catch(() => {});
      }
    }
  });
};
