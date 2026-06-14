import path from 'path';
import { defineConfig } from 'vite';
import uni from '@dcloudio/vite-plugin-uni';

export default defineConfig({
  // 确保 .env.development / .env.production 从 fronted 根目录加载
  envDir: path.resolve(process.cwd()),
  plugins: [uni()],
  assetsInclude: ['**/*.PNG'],
  server: {
    // 强制设置响应头，解决腾讯地图等第三方资源的跨域阻断问题 (COEP)
    headers: {
      'Cross-Origin-Opener-Policy': 'unsafe-none',
      'Cross-Origin-Embedder-Policy': 'unsafe-none'
    }
  }
});