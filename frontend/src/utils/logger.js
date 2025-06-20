/**
 * フロントエンド用のデバッグログユーティリティ
 */

class DebugLogger {
  constructor() {
    this.logs = {
      info: [],
      error: [],
      debug: [],
      network: []
    }
    this.maxLogs = 1000
    this.enabled = true
    
    // ローカルストレージから設定を読み込み
    const savedSettings = localStorage.getItem('debugLogSettings')
    if (savedSettings) {
      const settings = JSON.parse(savedSettings)
      this.enabled = settings.enabled !== false
    }
  }
  
  _getTimestamp() {
    return new Date().toISOString()
  }
  
  _addLog(type, message, data = null) {
    if (!this.enabled) return
    
    const logEntry = {
      timestamp: this._getTimestamp(),
      message,
      data,
      stackTrace: new Error().stack
    }
    
    // メモリ内に保存
    this.logs[type].push(logEntry)
    
    // 最大ログ数を超えたら古いものを削除
    if (this.logs[type].length > this.maxLogs) {
      this.logs[type].shift()
    }
    
    // コンソールに出力
    const consoleMethod = type === 'error' ? 'error' : 'log'
    console[consoleMethod](`[${type.toUpperCase()}] ${message}`, data)
    
    // ローカルストレージに保存（エラーのみ）
    if (type === 'error') {
      this._saveErrorToLocalStorage(logEntry)
    }
  }
  
  _saveErrorToLocalStorage(errorLog) {
    try {
      const errors = JSON.parse(localStorage.getItem('debugErrors') || '[]')
      errors.push(errorLog)
      
      // 最新100件のみ保持
      const recentErrors = errors.slice(-100)
      localStorage.setItem('debugErrors', JSON.stringify(recentErrors))
    } catch (e) {
      console.error('Failed to save error to localStorage:', e)
    }
  }
  
  info(message, data = null) {
    this._addLog('info', message, data)
  }
  
  error(message, error = null, data = null) {
    const errorData = {
      ...data,
      errorMessage: error?.message,
      errorStack: error?.stack,
      errorType: error?.constructor?.name
    }
    this._addLog('error', message, errorData)
  }
  
  debug(message, data = null) {
    this._addLog('debug', message, data)
  }
  
  network(method, url, status, responseTime, data = null) {
    const networkLog = {
      method,
      url,
      status,
      responseTime,
      data,
      timestamp: this._getTimestamp()
    }
    
    this.logs.network.push(networkLog)
    if (this.logs.network.length > this.maxLogs) {
      this.logs.network.shift()
    }
    
    const statusClass = status >= 200 && status < 300 ? 'success' : 'error'
    console.log(
      `[NETWORK] ${method} ${url} - ${status} (${responseTime}ms)`,
      data
    )
  }
  
  getLogs(type = 'all') {
    if (type === 'all') {
      return this.logs
    }
    return this.logs[type] || []
  }
  
  clearLogs(type = 'all') {
    if (type === 'all') {
      Object.keys(this.logs).forEach(key => {
        this.logs[key] = []
      })
      localStorage.removeItem('debugErrors')
    } else if (this.logs[type]) {
      this.logs[type] = []
      if (type === 'error') {
        localStorage.removeItem('debugErrors')
      }
    }
  }
  
  exportLogs() {
    const exportData = {
      timestamp: this._getTimestamp(),
      logs: this.logs,
      userAgent: navigator.userAgent,
      url: window.location.href
    }
    
    const blob = new Blob(
      [JSON.stringify(exportData, null, 2)],
      { type: 'application/json' }
    )
    
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `debug-logs-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
  }
  
  enable() {
    this.enabled = true
    localStorage.setItem('debugLogSettings', JSON.stringify({ enabled: true }))
  }
  
  disable() {
    this.enabled = false
    localStorage.setItem('debugLogSettings', JSON.stringify({ enabled: false }))
  }
}

// シングルトンインスタンス
const logger = new DebugLogger()

// Axiosインターセプターを設定（axios使用時）
export function setupAxiosLogging(axios) {
  // リクエストインターセプター
  axios.interceptors.request.use(
    config => {
      config.metadata = { startTime: Date.now() }
      logger.debug(`API Request: ${config.method?.toUpperCase()} ${config.url}`, {
        headers: config.headers,
        data: config.data,
        params: config.params
      })
      return config
    },
    error => {
      logger.error('API Request Error', error)
      return Promise.reject(error)
    }
  )
  
  // レスポンスインターセプター
  axios.interceptors.response.use(
    response => {
      const responseTime = Date.now() - response.config.metadata.startTime
      logger.network(
        response.config.method?.toUpperCase(),
        response.config.url,
        response.status,
        responseTime,
        {
          data: response.data,
          headers: response.headers
        }
      )
      return response
    },
    error => {
      const responseTime = Date.now() - error.config?.metadata?.startTime || 0
      logger.network(
        error.config?.method?.toUpperCase() || 'UNKNOWN',
        error.config?.url || 'UNKNOWN',
        error.response?.status || 0,
        responseTime,
        {
          error: error.message,
          response: error.response?.data
        }
      )
      logger.error('API Response Error', error, {
        url: error.config?.url,
        status: error.response?.status
      })
      return Promise.reject(error)
    }
  )
}

// Vue用のエラーハンドラー
export function setupVueErrorHandler(app) {
  app.config.errorHandler = (err, instance, info) => {
    logger.error('Vue Error', err, {
      componentInfo: info,
      componentName: instance?.$options.name || 'Unknown'
    })
  }
  
  // 未処理のPromiseエラーをキャッチ
  window.addEventListener('unhandledrejection', event => {
    logger.error('Unhandled Promise Rejection', event.reason, {
      promise: event.promise
    })
  })
  
  // 一般的なJavaScriptエラーをキャッチ
  window.addEventListener('error', event => {
    logger.error('Global Error', event.error || new Error(event.message), {
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno
    })
  })
}

export default logger