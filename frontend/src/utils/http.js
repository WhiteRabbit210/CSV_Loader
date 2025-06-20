/**
 * HTTPクライアントの設定
 * Axiosのインスタンスを作成し、共通設定を適用
 */
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { apiConfig } from '@/config/api'

// Axiosインスタンスの作成
const http = axios.create({
  baseURL: apiConfig.baseURL,
  timeout: 30000, // 30秒
  headers: {
    'Content-Type': 'application/json'
  }
})

// リクエストインターセプター
http.interceptors.request.use(
  config => {
    // 必要に応じて認証トークンなどを追加
    // const token = localStorage.getItem('token')
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }
    
    // ログ用のメタデータを追加
    config.metadata = { startTime: Date.now() }
    
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// レスポンスインターセプター
http.interceptors.response.use(
  response => {
    return response
  },
  error => {
    // エラーメッセージの表示
    if (error.response) {
      const message = error.response.data?.message || 'サーバーエラーが発生しました'
      ElMessage.error(message)
    } else if (error.request) {
      ElMessage.error('サーバーに接続できません')
    } else {
      ElMessage.error('リクエストエラーが発生しました')
    }
    
    return Promise.reject(error)
  }
)

export default http