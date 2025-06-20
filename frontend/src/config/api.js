/**
 * API設定
 * 環境に応じてベースURLを自動的に設定
 */

// 環境変数からベースURLを取得、未設定の場合は相対パス
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

/**
 * APIエンドポイントを生成
 * @param {string} path - APIパス（例: '/api/csv/upload'）
 * @returns {string} 完全なAPIエンドポイントURL
 */
export function getApiUrl(path) {
  // pathが/で始まっていない場合は追加
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  
  // 本番環境（相対パス）の場合
  if (!API_BASE_URL) {
    return normalizedPath
  }
  
  // 開発環境（絶対URL）の場合
  return `${API_BASE_URL}${normalizedPath}`
}

/**
 * API設定オブジェクト
 */
export const apiConfig = {
  baseURL: API_BASE_URL,
  endpoints: {
    // CSV関連
    csvUpload: getApiUrl('/api/csv/upload'),
    
    // 同期関連
    syncPreview: getApiUrl('/api/sync/preview'),
    syncExecute: getApiUrl('/api/sync/execute'),
    syncDownloadLog: getApiUrl('/api/sync/download-log'),
    
    // マッピング設定関連
    mappingsGet: getApiUrl('/api/mappings'),
    mappingsPost: getApiUrl('/api/mappings'),
    
    // ログ関連
    logs: (logType) => getApiUrl(`/api/logs/${logType}`),
    logsClear: (logType) => getApiUrl(`/api/logs/clear/${logType}`)
  }
}

export default apiConfig