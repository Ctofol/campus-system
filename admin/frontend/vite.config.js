import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/auth': 'http://101.33.210.169:8002',
      '/admin': 'http://101.33.210.169:8002',
      '/upload': 'http://101.33.210.169:8002'
    }
  }
})
