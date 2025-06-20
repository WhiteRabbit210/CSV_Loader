import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      // 開発環境でのプロキシ設定
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    // 本番ビルド設定
    outDir: 'dist',
    assetsDir: 'assets',
    // 相対パスでビルド（同じサーバーにデプロイする場合）
    base: './'
  }
})