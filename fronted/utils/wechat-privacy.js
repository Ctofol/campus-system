/**
 * 微信小程序隐私合规：必须在首次调用 getLocation / onLocationChange 等接口之前
 * 注册 wx.onNeedPrivacyAuthorization。若注册晚于首次定位，真机会出现定位失败、里程始终为 0。
 * 在 main.js 入口立即执行 init，UI 由 privacy-popup 通过 bindWeixinPrivacyUI 接入。
 */

let pendingResolves = [];
let uiHandler = null;

export function initWeixinPrivacyListener() {
  // #ifdef MP-WEIXIN
  if (typeof wx === 'undefined' || typeof wx.onNeedPrivacyAuthorization !== 'function') {
    return;
  }
  wx.onNeedPrivacyAuthorization((resolve) => {
    if (typeof uiHandler === 'function') {
      try {
        uiHandler(resolve);
      } catch (e) {
        console.error('privacy UI handler error', e);
      }
    } else {
      pendingResolves.push(resolve);
    }
  });
  // #endif
}

/** 由 privacy-popup 在 onMounted 中调用，挂载前积压的 resolve 会立刻下发 */
export function bindWeixinPrivacyUI(handler) {
  // #ifdef MP-WEIXIN
  uiHandler = handler;
  while (pendingResolves.length) {
    const r = pendingResolves.shift();
    try {
      handler(r);
    } catch (e) {
      console.error('privacy flush error', e);
    }
  }
  // #endif
}
