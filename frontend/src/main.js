import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import logger, { setupAxiosLogging, setupVueErrorHandler } from './utils/logger'
import http from './utils/http'

const app = createApp(App)

// ログシステムの初期化
logger.info('Application starting', {
  userAgent: navigator.userAgent,
  timestamp: new Date().toISOString(),
  environment: import.meta.env.VITE_APP_ENV
})

// HTTPクライアントのログ設定
setupAxiosLogging(http)

// Vueエラーハンドラーの設定
setupVueErrorHandler(app)

app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: 'ja' })

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// グローバルプロパティとしてloggerを追加
app.config.globalProperties.$logger = logger

app.mount('#app')

logger.info('Application mounted successfully')