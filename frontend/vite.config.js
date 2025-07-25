import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '0.0.0.0',
    allowedHosts: [
      'localhost', 
      '127.0.0.1', 
      '.cpolar.cn', 
      '.r20.vip.cpolar.cn',
      // 花生壳域名配置
      'mi3qm328989.vicp.fun' 
    ]
  },
  build: {
    outDir: 'dist'
  }
})