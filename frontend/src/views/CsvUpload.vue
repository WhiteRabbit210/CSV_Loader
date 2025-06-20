<template>
  <div class="csv-upload-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>CSVファイルアップロード</h2>
          <el-steps :active="0" align-center>
            <el-step title="アップロード" />
            <el-step title="マッピング" />
            <el-step title="確認" />
            <el-step title="完了" />
          </el-steps>
        </div>
      </template>

      <el-upload
        v-if="!fileUploaded"
        class="upload-demo"
        drag
        :action="uploadUrl"
        :before-upload="beforeUpload"
        :on-success="handleSuccess"
        :on-error="handleError"
        :on-change="handleChange"
        :file-list="fileList"
        :limit="1"
        :auto-upload="false"
        accept=".csv"
        ref="uploadRef"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          CSVファイルをドラッグ＆ドロップ<br>または<em>クリックして選択</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            CSV形式のファイルのみアップロード可能です
          </div>
        </template>
      </el-upload>

      <div v-if="fileUploaded && !csvPreview.length" class="upload-status">
        <el-icon class="is-loading"><loading /></el-icon>
        <p>ファイルを処理中...</p>
      </div>

      <div v-if="fileUploaded && csvPreview.length > 0" class="upload-status success">
        <el-icon><circle-check /></el-icon>
        <p>アップロード完了: {{ fileList[0]?.name || 'CSVファイル' }}</p>
      </div>

      <div v-if="csvPreview.length > 0" class="csv-preview">
        <h3>CSVプレビュー（先頭10行）</h3>
        <el-table :data="csvPreview" style="width: 100%" max-height="400">
          <el-table-column
            v-for="(header, index) in csvHeaders"
            :key="index"
            :prop="String(index)"
            :label="header"
            min-width="150"
          />
        </el-table>
      </div>

      <div class="action-buttons" v-if="fileUploaded">
        <el-button type="primary" @click="proceedToMapping" :loading="loading">
          次へ：フィールドマッピング
          <el-icon class="el-icon--right"><arrow-right /></el-icon>
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, getCurrentInstance } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { UploadFilled, ArrowRight, Loading, CircleCheck } from '@element-plus/icons-vue'
import { useCsvStore } from '@/stores/csv'
import http from '@/utils/http'
import { apiConfig } from '@/config/api'

const router = useRouter()
const csvStore = useCsvStore()
const instance = getCurrentInstance()
const logger = instance.appContext.config.globalProperties.$logger

const uploadUrl = ref(apiConfig.endpoints.csvUpload)
const fileList = ref([])
const fileUploaded = ref(false)
const loading = ref(false)
const csvHeaders = ref([])
const csvPreview = ref([])
const uploadRef = ref(null)

const beforeUpload = (file) => {
  const isCSV = file.type === 'text/csv' || file.name.endsWith('.csv')
  if (!isCSV) {
    ElMessage.error('CSVファイルのみアップロード可能です')
    return false
  }
  
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('ファイルサイズは10MB以下にしてください')
    return false
  }
  
  return true
}

const handleChange = async (file, fileListParam) => {
  if (file.raw) {
    logger.info('File selected', { filename: file.name, size: file.size })
    fileList.value = fileListParam
    await uploadFile(file.raw)
  }
}

const uploadFile = async (file) => {
  loading.value = true
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    logger.info('Starting file upload', { filename: file.name })
    
    const response = await http.post(uploadUrl.value, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    if (response.data.success) {
      fileUploaded.value = true
      csvHeaders.value = response.data.headers
      csvPreview.value = response.data.preview
      
      // session_idを含めてストアに保存
      csvStore.setUploadData({
        ...response.data,
        session_id: response.data.session_id
      })
      
      ElMessage.success('ファイルアップロード成功')
      logger.info('CSV upload successful', {
        filename: file.name,
        rows: response.data.total_rows,
        headers: response.data.headers,
        session_id: response.data.session_id
      })
    } else {
      throw new Error(response.data.message || 'アップロードに失敗しました')
    }
  } catch (error) {
    logger.error('CSV upload failed', error, {
      filename: file.name,
      message: error.message
    })
    ElMessage.error(error.message || 'ファイルアップロードに失敗しました')
  } finally {
    loading.value = false
  }
}

const handleSuccess = (response) => {
  // auto-upload=falseなので使用しない
}

const handleError = (error) => {
  // auto-upload=falseなので使用しない
}

const proceedToMapping = () => {
  loading.value = true
  setTimeout(() => {
    router.push('/mapping')
  }, 500)
}
</script>

<style lang="scss" scoped>
.csv-upload-container {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  h2 {
    margin: 0 0 20px 0;
  }
}

.upload-demo {
  margin: 20px 0;
}

.upload-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin: 40px 0;
  font-size: 16px;
  color: #606266;
  
  .el-icon {
    font-size: 24px;
  }
  
  &.success {
    color: #67c23a;
    
    .el-icon {
      color: #67c23a;
    }
  }
}

.csv-preview {
  margin-top: 30px;
  
  h3 {
    margin-bottom: 15px;
    color: #333;
  }
}

.action-buttons {
  margin-top: 30px;
  text-align: right;
}
</style>