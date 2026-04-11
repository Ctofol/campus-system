import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  base: '/admin/',
  plugins: [vue()],
  server: {
    proxy: {
      '/auth': 'http://localhost:8002',
      '/admin-api': 'http://localhost:8002',
      '/upload': 'http://localhost:8002'
    }
  }
})
