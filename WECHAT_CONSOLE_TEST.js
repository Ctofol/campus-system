// 在微信开发者工具的Console中运行此代码来测试网络连接
// 复制整段代码，粘贴到Console中，按回车执行

console.log('=== 开始网络连接测试 ===');
console.log('后端地址: http://192.168.0.216:8000');
console.log('');

// 测试1: 验证码接口
console.log('[测试1] 测试验证码接口...');
wx.request({
  url: 'http://192.168.0.216:8000/common/captcha',
  method: 'GET',
  success: (res) => {
    console.log('✓ 验证码接口成功!');
    console.log('  状态码:', res.statusCode);
    console.log('  返回数据:', res.data);
  },
  fail: (err) => {
    console.error('✗ 验证码接口失败!');
    console.error('  错误信息:', err);
    console.error('  错误代码:', err.errMsg);
  }
});

// 测试2: 登录接口
console.log('[测试2] 测试登录接口...');
wx.request({
  url: 'http://192.168.0.216:8000/auth/login',
  method: 'POST',
  data: {
    phone: '13800138000',
    password: '123456'
  },
  header: {
    'Content-Type': 'application/json'
  },
  success: (res) => {
    console.log('✓ 登录接口成功!');
    console.log('  状态码:', res.statusCode);
    console.log('  返回数据:', res.data);
  },
  fail: (err) => {
    console.error('✗ 登录接口失败!');
    console.error('  错误信息:', err);
    console.error('  错误代码:', err.errMsg);
  }
});

console.log('');
console.log('=== 测试已发送，请查看上方结果 ===');
console.log('');
console.log('如果看到 "✗ 失败" 信息：');
console.log('1. 检查是否勾选了"不校验合法域名"');
console.log('2. 检查后端服务是否正在运行');
console.log('3. 检查IP地址是否正确（当前: 192.168.0.216）');
console.log('4. 检查防火墙设置');
