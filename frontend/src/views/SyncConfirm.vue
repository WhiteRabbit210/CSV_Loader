<template>
  <div class="sync-confirm-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>同期内容確認</h2>
          <el-steps :active="2" align-center>
            <el-step title="アップロード" />
            <el-step title="マッピング" />
            <el-step title="確認" />
            <el-step title="完了" />
          </el-steps>
        </div>
      </template>

      <div class="sync-summary">
        <el-alert
          title="以下の内容で同期を実行します"
          type="info"
          :closable="false"
          show-icon
        />
        
        <div class="summary-cards">
          <el-card 
            shadow="hover" 
            class="summary-card add-card" 
            :class="{ active: activeTab === 'add' }"
            @click="handleCardClick('add')"
          >
            <div class="card-content">
              <el-icon class="card-icon"><user-filled /></el-icon>
              <div class="card-info">
                <div class="card-number">{{ syncSummary.toAdd }}</div>
                <div class="card-label">新規追加</div>
              </div>
            </div>
          </el-card>
          
          <el-card 
            shadow="hover" 
            class="summary-card update-card"
            :class="{ active: activeTab === 'update' }"
            @click="handleCardClick('update')"
          >
            <div class="card-content">
              <el-icon class="card-icon"><refresh /></el-icon>
              <div class="card-info">
                <div class="card-number">{{ syncSummary.toUpdate }}</div>
                <div class="card-label">更新</div>
              </div>
            </div>
          </el-card>
          
          <el-card 
            shadow="hover" 
            class="summary-card delete-card"
            :class="{ active: activeTab === 'delete' }"
            @click="handleCardClick('delete')"
          >
            <div class="card-content">
              <el-icon class="card-icon"><delete /></el-icon>
              <div class="card-info">
                <div class="card-number">{{ syncSummary.toDelete }}</div>
                <div class="card-label">削除</div>
              </div>
            </div>
          </el-card>
        </div>
      </div>

      <el-tabs v-model="activeTab" class="sync-details">
        <el-tab-pane label="新規追加ユーザー" name="add" v-if="newUsers.length > 0">
          <el-table :data="newUsers" style="width: 100%" max-height="400">
            <el-table-column prop="name" label="名前" width="200" />
            <el-table-column prop="email" label="メールアドレス" width="250" />
            <el-table-column prop="position" label="役職" width="150" />
            <el-table-column prop="department" label="所属" />
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="更新対象ユーザー" name="update" v-if="updateUsers.length > 0">
          <el-table :data="updateUsers" style="width: 100%" max-height="400">
            <el-table-column prop="email" label="メールアドレス" width="250" />
            <el-table-column label="変更内容">
              <template #default="scope">
                <div class="change-details">
                  <div v-if="scope.row.changes.name" class="change-item">
                    <span class="change-field">名前:</span>
                    <span class="old-value">{{ scope.row.changes.name.old }}</span>
                    <el-icon><arrow-right /></el-icon>
                    <span class="new-value">{{ scope.row.changes.name.new }}</span>
                  </div>
                  <div v-if="scope.row.changes.position" class="change-item">
                    <span class="change-field">役職:</span>
                    <span class="old-value">{{ scope.row.changes.position.old }}</span>
                    <el-icon><arrow-right /></el-icon>
                    <span class="new-value">{{ scope.row.changes.position.new }}</span>
                  </div>
                  <div v-if="scope.row.changes.department" class="change-item">
                    <span class="change-field">所属:</span>
                    <span class="old-value">{{ scope.row.changes.department.old }}</span>
                    <el-icon><arrow-right /></el-icon>
                    <span class="new-value">{{ scope.row.changes.department.new }}</span>
                  </div>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="削除対象ユーザー" name="delete" v-if="deleteUsers.length > 0">
          <el-table :data="deleteUsers" style="width: 100%" max-height="400">
            <el-table-column prop="name" label="名前" width="200" />
            <el-table-column prop="email" label="メールアドレス" width="250" />
            <el-table-column prop="position" label="役職" width="150" />
            <el-table-column prop="department" label="所属" />
          </el-table>
        </el-tab-pane>
      </el-tabs>

      <div class="action-buttons">
        <el-button @click="goBack">
          <el-icon class="el-icon--left"><arrow-left /></el-icon>
          戻る
        </el-button>
        <el-popconfirm
          title="同期を実行しますか？"
          confirm-button-text="実行"
          cancel-button-text="キャンセル"
          @confirm="executeSync"
        >
          <template #reference>
            <el-button type="primary" :loading="loading">
              同期を実行
              <el-icon class="el-icon--right"><check /></el-icon>
            </el-button>
          </template>
        </el-popconfirm>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, getCurrentInstance } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useCsvStore } from '@/stores/csv'
import http from '@/utils/http'
import { apiConfig } from '@/config/api'

const router = useRouter()
const csvStore = useCsvStore()
const instance = getCurrentInstance()
const logger = instance.appContext.config.globalProperties.$logger

const activeTab = ref('add')
const loading = ref(false)

const syncSummary = ref({
  toAdd: 0,
  toUpdate: 0,
  toDelete: 0
})

const newUsers = ref([])
const updateUsers = ref([])
const deleteUsers = ref([])

const loadSyncPreview = async () => {
  try {
    logger.info('Loading sync preview', {
      hasUploadData: !!csvStore.uploadData,
      sessionId: csvStore.uploadData?.session_id,
      mappingConfig: csvStore.mappingConfig
    })
    
    const response = await http.post(apiConfig.endpoints.syncPreview, {
      csvData: {
        session_id: csvStore.uploadData.session_id,
        headers: csvStore.uploadData.headers,
        preview: csvStore.uploadData.preview
      },
      mapping: csvStore.mappingConfig
    })
    
    logger.info('Sync preview response', {
      success: response.data.success,
      summary: response.data.summary
    })
    
    if (response.data.success) {
      syncSummary.value = response.data.summary
      newUsers.value = response.data.newUsers || []
      updateUsers.value = response.data.updateUsers || []
      deleteUsers.value = response.data.deleteUsers || []
      
      // 最初のタブを自動的に選択
      if (newUsers.value.length > 0) {
        activeTab.value = 'add'
      } else if (updateUsers.value.length > 0) {
        activeTab.value = 'update'
      } else if (deleteUsers.value.length > 0) {
        activeTab.value = 'delete'
      }
    }
  } catch (error) {
    logger.error('Failed to load sync preview', error, {
      uploadData: csvStore.uploadData,
      mappingConfig: csvStore.mappingConfig
    })
    ElMessage.error('同期プレビューの読み込みに失敗しました')
  }
}

const goBack = () => {
  router.push('/mapping')
}

const handleCardClick = (tabName) => {
  // タブが存在する場合のみアクティブにする
  if (
    (tabName === 'add' && newUsers.value.length > 0) ||
    (tabName === 'update' && updateUsers.value.length > 0) ||
    (tabName === 'delete' && deleteUsers.value.length > 0)
  ) {
    activeTab.value = tabName
  }
}

const executeSync = async () => {
  loading.value = true
  
  try {
    const response = await http.post(apiConfig.endpoints.syncExecute, {
      csvData: {
        session_id: csvStore.uploadData.session_id,
        headers: csvStore.uploadData.headers,
        preview: csvStore.uploadData.preview
      },
      mapping: csvStore.mappingConfig
    })
    
    if (response.data.success) {
      csvStore.setSyncResults(response.data.results)
      ElMessage.success('同期処理が完了しました')
      router.push('/result')
    } else {
      ElMessage.error(response.data.message || '同期処理に失敗しました')
    }
  } catch (error) {
    console.error('Sync execution failed:', error)
    ElMessage.error('同期処理中にエラーが発生しました')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // Check sessionStorage directly
  const sessionData = sessionStorage.getItem('csv')
  let parsedSessionData = null
  try {
    parsedSessionData = sessionData ? JSON.parse(sessionData) : null
  } catch (e) {
    logger.error('Failed to parse session data', e)
  }
  
  logger.info('SyncConfirm mounted', {
    hasUploadData: !!csvStore.uploadData,
    uploadData: csvStore.uploadData,
    mappingConfig: csvStore.mappingConfig,
    emailMapping: csvStore.mappingConfig?.email,
    sessionStorageData: parsedSessionData,
    directMappingConfig: csvStore.getMappingConfig()
  })
  
  if (!csvStore.uploadData) {
    logger.error('Missing upload data', {
      uploadData: csvStore.uploadData,
      storeState: {
        uploadData: csvStore.uploadData,
        mappingConfig: csvStore.mappingConfig,
        savedMappings: csvStore.savedMappings
      }
    })
    ElMessage.warning('必要な情報が不足しています：CSVデータがありません')
    router.push('/upload')
    return
  }
  
  if (!csvStore.mappingConfig.email && csvStore.mappingConfig.email !== 0) {
    logger.error('Missing email mapping', {
      mappingConfig: csvStore.mappingConfig,
      emailValue: csvStore.mappingConfig?.email,
      emailType: typeof csvStore.mappingConfig?.email,
      allMappingValues: {
        name: csvStore.mappingConfig?.name,
        email: csvStore.mappingConfig?.email,
        position: csvStore.mappingConfig?.position,
        department: csvStore.mappingConfig?.department
      }
    })
    ElMessage.warning('必要な情報が不足しています：メールアドレスのマッピングが設定されていません')
    router.push('/upload')
    return
  }
  
  loadSyncPreview()
})
</script>

<style lang="scss" scoped>
.sync-confirm-container {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  h2 {
    margin: 0 0 20px 0;
  }
}

.sync-summary {
  margin-bottom: 30px;
  
  .summary-cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-top: 20px;
  }
  
  .summary-card {
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    &.active {
      border-width: 2px;
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    &.add-card {
      --el-card-border-color: #67c23a;
      .card-icon { color: #67c23a; }
      
      &.active {
        background-color: #f0f9ff;
      }
    }
    
    &.update-card {
      --el-card-border-color: #409eff;
      .card-icon { color: #409eff; }
      
      &.active {
        background-color: #f0f9ff;
      }
    }
    
    &.delete-card {
      --el-card-border-color: #f56c6c;
      .card-icon { color: #f56c6c; }
      
      &.active {
        background-color: #fef0f0;
      }
    }
    
    .card-content {
      display: flex;
      align-items: center;
      padding: 10px;
    }
    
    .card-icon {
      font-size: 48px;
      margin-right: 20px;
    }
    
    .card-info {
      flex: 1;
      
      .card-number {
        font-size: 32px;
        font-weight: bold;
        line-height: 1.2;
      }
      
      .card-label {
        color: #909399;
        font-size: 14px;
      }
    }
  }
}

.sync-details {
  margin-bottom: 30px;
  
  .change-details {
    .change-item {
      display: flex;
      align-items: center;
      margin-bottom: 5px;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      .change-field {
        font-weight: bold;
        margin-right: 10px;
        min-width: 50px;
      }
      
      .old-value {
        color: #f56c6c;
        text-decoration: line-through;
        margin-right: 10px;
      }
      
      .new-value {
        color: #67c23a;
        margin-left: 10px;
      }
      
      .el-icon {
        color: #909399;
      }
    }
  }
}

.action-buttons {
  display: flex;
  justify-content: space-between;
}
</style>