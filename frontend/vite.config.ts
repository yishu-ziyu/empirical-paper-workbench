/// <reference types="vitest" />
import { defineConfig, type ProxyOptions } from 'vite'
import react from '@vitejs/plugin-react'

const backend = 'http://127.0.0.1:8000'

const apiProxy: Record<string, ProxyOptions> = {
  '/api': {
    target: backend,
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, '') || '/',
  },
}

export default defineConfig({
  plugins: [react()],
  server: { proxy: apiProxy },
  preview: { proxy: apiProxy },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    css: true,
  },
})
