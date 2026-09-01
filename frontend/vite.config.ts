/// <reference types="vitest" />
import type { ProxyOptions } from 'vite'
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

const backend = 'http://127.0.0.1:8000'

const apiProxy: Record<string, ProxyOptions> = {
  '/api': {
    target: backend,
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, '') || '/',
  },
}

// host 固定 IPv4：默认 'localhost' 在 Node 18+ 只绑 ::1，
// 走系统代理的 IPv4 客户端会得到 502 upstream connect failed
export default defineConfig({
  plugins: [react()],
  server: { host: '127.0.0.1', proxy: apiProxy },
  preview: { host: '127.0.0.1', proxy: apiProxy },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    css: true,
  },
})
