/**
 * 微信小程序用户头像选择：优先 chooseAvatar；隐私未声明时降级相册并提示后台配置。
 */

const PRIVACY_CONFIG_HINT =
  '请在微信公众平台 → 设置 → 服务内容声明 → 用户隐私保护指引中，勾选「用户信息」里的头像；若用相册选图，还需声明相册/摄像头。保存后约 5 分钟生效，开发工具可「清除模拟器缓存-清除授权数据」后重试。';

const isPrivacyScopeError = (errMsg = '') => {
  const m = String(errMsg);
  return (
    m.includes('privacy') ||
    m.includes('隐私') ||
    m.includes('scope is not declared') ||
    m.includes('api scope is not declared')
  );
};

/** 相册/拍照选图（需在隐私指引中声明相册、摄像头） */
export const pickAvatarFromAlbum = () => {
  return new Promise((resolve, reject) => {
    uni.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const filePath = res.tempFilePaths && res.tempFilePaths[0];
        if (filePath) resolve(filePath);
        else reject(new Error('未选择图片'));
      },
      fail: (err) => {
        const errMsg = (err && err.errMsg) || '';
        if (isPrivacyScopeError(errMsg)) {
          uni.showModal({
            title: '隐私接口未配置',
            content: PRIVACY_CONFIG_HINT,
            showCancel: false,
            confirmText: '知道了'
          });
        }
        reject(err);
      }
    });
  });
};

/** chooseAvatar 按钮 @error 回调；onPicked(filePath) 可选，用于选图后继续上传 */
export const onChooseAvatarButtonError = (event, onPicked) => {
  const errMsg = (event && event.detail && event.detail.errMsg) || '';
  console.warn('chooseAvatar error:', errMsg);
  if (!isPrivacyScopeError(errMsg)) {
    uni.showToast({ title: '打开头像选择失败', icon: 'none' });
    return;
  }
  uni.showModal({
    title: '头像接口未在隐私指引中声明',
    content: PRIVACY_CONFIG_HINT + '\n\n是否改用相册选图？（相册也需在隐私指引中声明）',
    confirmText: '用相册',
    cancelText: '取消',
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
