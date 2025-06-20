<template>
  <div class="process-result-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>処理結果</h2>
          <el-steps :active="3" align-center finish-status="success">
            <el-step title="アップロード" />
            <el-step title="マッピング" />
            <el-step title="確認" />
            <el-step title="完了" />
          </el-steps>
        </div>
      </template>

      <div class="result-content">
        <el-result
          :icon="resultIcon"
          :title="resultTitle"
          :sub-title="resultSubTitle"
        >
          <template #extra>
            <div class="result-summary">
              <el-descriptions :column="3" border>
                <el-descriptions-item label="処理開始時刻">
                  {{ formatDate(syncResults?.startTime) }}
                </el-descriptions-item>
                <el-descriptions-item label="処理終了時刻">
                  {{ formatDate(syncResults?.endTime) }}
                </el-descriptions-item>
                <el-descriptions-item label="処理時間">
                  {{ processingTime }}
                </el-descriptions-item>
                <el-descriptions-item label="新規追加">
                  <el-tag type="success">{{ syncResults?.added || 0 }}件</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="更新">
                  <el-tag type="primary">{{ syncResults?.updated || 0 }}件</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="削除">
                  <el-tag type="danger">{{ syncResults?.deleted || 0 }}件</el-tag>
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </template>
        </el-result>

        <div v-if="hasErrors" class="error-section">
          <h3>エラー詳細</h3>
          <el-table :data="errorDetails" style="width: 100%" max-height="300">
            <el-table-column prop="email" label="メールアドレス" width="250" />
            <el-table-column prop="operation" label="操作" width="100">
              <template #default="scope">
                <el-tag :type="getOperationType(scope.row.operation)" size="small">
                  {{ scope.row.operation }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="error" label="エラー内容" />
          </el-table>
        </div>

        <div class="action-section">
          <el-button @click="downloadLog" :loading="downloadingLog">
            <el-icon><download /></el-icon>
            処理ログをダウンロード
          </el-button>
          <el-button type="primary" @click="startNewProcess">
            <el-icon><refresh /></el-icon>
            新規処理を開始
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useCsvStore } from '@/stores/csv'
import http from '@/utils/http'
import { apiConfig } from '@/config/api'

const router = useRouter()
const csvStore = useCsvStore()

const downloadingLog = ref(false)

const syncResults = computed(() => csvStore.syncResults)
const hasErrors = computed(() => errorDetails.value.length > 0)
const errorDetails = ref([])

const resultIcon = computed(() => {
  if (!syncResults.value) return 'warning'
  return hasErrors.value ? 'warning' : 'success'
})

const resultTitle = computed(() => {
  if (!syncResults.value) return '処理結果がありません'
  return hasErrors.value ? '処理は部分的に成功しました' : '処理が正常に完了しました'
})

const resultSubTitle = computed(() => {
  if (!syncResults.value) return ''
  const total = (syncResults.value.added || 0) + 
                (syncResults.value.updated || 0) + 
                (syncResults.value.deleted || 0)
  return `合計 ${total} 件のユーザー情報を処理しました`
})

const processingTime = computed(() => {
  if (!syncResults.value?.startTime || !syncResults.value?.endTime) return '-'
  const start = new Date(syncResults.value.startTime)
  const end = new Date(syncResults.value.endTime)
  const diff = end - start
  return `${Math.round(diff / 1000)} 秒`
})

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('ja-JP')
}

const getOperationType = (operation) => {
  switch (operation) {
    case '追加': return 'success'
    case '更新': return 'primary'
    case '削除': return 'danger'
    default: return 'info'
  }
}

const downloadLog = async () => {
  downloadingLog.value = true
  
  try {
    const response = await http.post(apiConfig.endpoints.syncDownloadLog, {
      resultId: syncResults.value?.id
    }, {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `sync-log-${new Date().toISOString()}.csv`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    
    ElMessage.success('ログファイルをダウンロードしました')
  } catch (error) {
    console.error('Failed to download log:', error)
    ElMessage.error('ログファイルのダウンロードに失敗しました')
  } finally {
    downloadingLog.value = false
  }
}

const startNewProcess = () => {
  csvStore.reset()
  router.push('/upload')
}

onMounted(() => {
  if (!syncResults.value) {
    ElMessage.warning('処理結果がありません')
    router.push('/upload')
    return
  }
  
  if (syncResults.value.errors) {
    errorDetails.value = syncResults.value.errors
  }
})
</script>

<style lang="scss" scoped>
.process-result-container {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  h2 {
    margin: 0 0 20px 0;
  }
}

.result-content {
  .result-summary {
    margin-top: 20px;
  }
  
  .error-section {
    margin: 30px 0;
    padding: 20px;
    background-color: #fef0f0;
    border-radius: 4px;
    
    h3 {
      margin: 0 0 15px 0;
      color: #f56c6c;
    }
  }
  
  .action-section {
    margin-top: 30px;
    display: flex;
    justify-content: center;
    gap: 20px;
  }
}
</style>