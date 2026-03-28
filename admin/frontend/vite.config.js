import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/auth': 'http://localhost:8080',
      '/admin': 'http://localhost:8080',
      '/upload': 'http://localhost:8080'
    }
  }
})
