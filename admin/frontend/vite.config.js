import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  base: '/admin/',
  plugins: [vue()],
  server: {
    proxy: {
      // 管理端接口与后端公开路径保持一致，不做额外路径改写。
      '/manage': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true,
      },
      '/common': 'http://127.0.0.1:8002',
      '/auth': 'http://127.0.0.1:8002',
      '/upload': 'http://127.0.0.1:8002',
      '/system': 'http://127.0.0.1:8002',
    },
  },
})
