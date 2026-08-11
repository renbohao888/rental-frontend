import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  build: {
    // 禁用 CSS 代码分割：全部样式合并为一个文件由 index.html 同步加载，
    // 避免首屏动态注入样式延迟导致的排版闪烁（FOUC）
    cssCodeSplit: false
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8080', // 替换为你实际的后端服务地址和端口
        changeOrigin: true
      },
      // 上传文件静态资源（后端 /uploads/** 映射到上传目录）
      '/uploads': {
        target: 'http://localhost:8080',
        changeOrigin: true
      }
    }
  }
})