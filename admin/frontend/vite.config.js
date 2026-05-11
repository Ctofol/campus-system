import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  base: '/admin/',
  plugins: [vue()],
  server: {
    proxy: {
      // 前端 api 使用 /manage/*，避免与静态资源路径 /admin/* 冲突；转发到后端 /admin/*
      '/manage': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/manage/, '/admin'),
      },
      '/common': 'http://127.0.0.1:8002',
      '/auth': 'http://127.0.0.1:8002',
      '/upload': 'http://127.0.0.1:8002',
    },
  },
})
