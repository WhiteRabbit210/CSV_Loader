<template>
  <div class="field-mapping-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>フィールドマッピング設定</h2>
          <el-steps :active="1" align-center>
            <el-step title="アップロード" />
            <el-step title="マッピング" />
            <el-step title="確認" />
            <el-step title="完了" />
          </el-steps>
        </div>
      </template>

      <div class="mapping-section">
        <div class="saved-mappings">
          <el-select
            v-model="selectedSavedMapping"
            placeholder="保存済み設定を選択"
            clearable
            @change="loadSavedMapping"
            style="width: 300px; margin-right: 10px;"
          >
            <el-option
              v-for="mapping in savedMappings"
              :key="mapping.id"
              :label="mapping.name"
              :value="mapping.id"
            />
          </el-select>
          <el-button @click="usePreviousMapping" :disabled="!hasPreviousMapping">
            <el-icon><refresh /></el-icon>
            前回の割り当て内容を利用
          </el-button>
        </div>

        <div class="mapping-table">
          <h3>CSVフィールドをシステムフィールドに割り当ててください</h3>
          <p class="mapping-note">
            <el-icon><info-filled /></el-icon>
            <span class="required-mark">*</span>印のついた項目は必須です。メールアドレスはユーザー識別のキーとして使用されます。
          </p>
          
          <div class="mapping-grid">
            <div class="mapping-row" v-for="field in systemFields" :key="field.key">
              <div class="system-field">
                <el-tag :type="field.required ? 'danger' : 'info'">
                  {{ field.label }}
                  <span v-if="field.required">*</span>
                </el-tag>
              </div>
              <div class="arrow">
                <el-icon><arrow-left /></el-icon>
              </div>
              <div class="csv-field">
                <div v-if="!field.multiple || !mappingConfig[field.key] || !Array.isArray(mappingConfig[field.key])">
                  <!-- 単一フィールド選択 -->
                  <el-select
                    v-model="mappingConfig[field.key]"
                    :placeholder="`${field.label}に対応するCSVカラムを選択`"
                    clearable
                    style="width: calc(100% - 40px); margin-right: 5px;"
                    popper-class="field-mapping-dropdown"
                  >
                    <el-option
                      v-for="(header, index) in csvHeaders"
                      :key="index"
                      :label="header"
                      :value="index"
                    >
                      <div class="option-content">
                        <span class="column-name">{{ header }}</span>
                        <el-tag size="small" type="info" class="sample-data">{{ getSampleData(index) }}</el-tag>
                      </div>
                    </el-option>
                  </el-select>
                  <el-button
                    v-if="field.multiple"
                    type="primary"
                    size="small"
                    circle
                    @click="enableMultipleFields(field.key)"
                  >
                    <el-icon><plus /></el-icon>
                  </el-button>
                </div>
                <div v-else class="multiple-fields">
                  <!-- 複数フィールド選択 -->
                  <div v-for="(value, idx) in mappingConfig[field.key]" :key="idx" class="field-row">
                    <el-select
                      v-model="mappingConfig[field.key][idx]"
                      :placeholder="`フィールド${idx + 1}を選択`"
                      clearable
                      style="width: calc(100% - 80px); margin-right: 5px;"
                      popper-class="field-mapping-dropdown"
                    >
                      <el-option
                        v-for="(header, index) in csvHeaders"
                        :key="index"
                        :label="header"
                        :value="index"
                      >
                        <div class="option-content">
                          <span class="column-name">{{ header }}</span>
                          <el-tag size="small" type="info" class="sample-data">{{ getSampleData(index) }}</el-tag>
                        </div>
                      </el-option>
                    </el-select>
                    <el-button
                      v-if="idx === mappingConfig[field.key].length - 1"
                      type="primary"
                      size="small"
                      circle
                      @click="addField(field.key)"
                    >
                      <el-icon><plus /></el-icon>
                    </el-button>
                    <el-button
                      v-if="mappingConfig[field.key].length > 1"
                      type="danger"
                      size="small"
                      circle
                      @click="removeField(field.key, idx)"
                    >
                      <el-icon><minus /></el-icon>
                    </el-button>
                    <el-button
                      v-if="mappingConfig[field.key].length === 1"
                      size="small"
                      circle
                      @click="disableMultipleFields(field.key)"
                    >
                      <el-icon><close /></el-icon>
                    </el-button>
                  </div>
                  <div class="concat-preview" v-if="getConcatenatedPreview(field.key)">
                    <el-tag type="success">
                      結合プレビュー: {{ getConcatenatedPreview(field.key) }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="mapping-preview" v-if="hasMapping">
          <h3>マッピングプレビュー</h3>
          <el-table :data="previewData" style="width: 100%" max-height="300">
            <el-table-column prop="name" label="名前" width="200" />
            <el-table-column prop="email" label="メールアドレス" width="250" />
            <el-table-column prop="position" label="役職" width="150" />
            <el-table-column prop="department" label="所属" />
          </el-table>
        </div>

        <div class="save-mapping">
          <el-input
            v-model="mappingName"
            placeholder="マッピング設定名を入力"
            style="width: 300px; margin-right: 10px;"
          />
          <el-button @click="saveMapping" :disabled="!mappingName || !isValidMapping">
            <el-icon><document /></el-icon>
            設定を保存
          </el-button>
        </div>
      </div>

      <div class="action-buttons">
        <el-button @click="goBack">
          <el-icon class="el-icon--left"><arrow-left /></el-icon>
          戻る
        </el-button>
        <el-button type="primary" @click="proceedToConfirm" :disabled="!isValidMapping" :loading="loading">
          次へ：同期内容確認
          <el-icon class="el-icon--right"><arrow-right /></el-icon>
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, getCurrentInstance } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useCsvStore } from '@/stores/csv'

const router = useRouter()
const csvStore = useCsvStore()
const instance = getCurrentInstance()
const logger = instance.appContext.config.globalProperties.$logger

const selectedSavedMapping = ref(null)
const mappingName = ref('')
const loading = ref(false)

// Initialize with existing mapping config from store if available
const storedConfig = csvStore.mappingConfig
logger.info('Initializing mapping config from store', {
  storedConfig,
  emailValue: storedConfig?.email,
  emailType: typeof storedConfig?.email
})

const mappingConfig = ref({
  name: storedConfig.name !== undefined ? storedConfig.name : null,
  email: storedConfig.email !== undefined ? storedConfig.email : null,
  position: storedConfig.position !== undefined ? storedConfig.position : null,
  department: storedConfig.department !== undefined ? storedConfig.department : null
})

const systemFields = [
  { key: 'name', label: '名前', required: false, multiple: true },
  { key: 'email', label: 'メールアドレス', required: true, multiple: false },
  { key: 'position', label: '役職', required: false, multiple: true },
  { key: 'department', label: '所属', required: false, multiple: true }
]

const csvHeaders = computed(() => csvStore.uploadData?.headers || [])
const csvPreview = computed(() => csvStore.uploadData?.preview || [])
const savedMappings = computed(() => csvStore.savedMappings)
const hasPreviousMapping = computed(() => savedMappings.value.length > 0)

const hasMapping = computed(() => {
  return mappingConfig.value.email !== null
})

const isValidMapping = computed(() => {
  return mappingConfig.value.email !== null
})

const enableMultipleFields = (key) => {
  const currentValue = mappingConfig.value[key]
  // 現在の値を配列に変換し、2つ目のフィールドを追加
  mappingConfig.value[key] = currentValue !== null ? [currentValue, null] : [null, null]
}

const disableMultipleFields = (key) => {
  const currentValue = mappingConfig.value[key]
  mappingConfig.value[key] = Array.isArray(currentValue) && currentValue.length > 0 ? currentValue[0] : null
}

const addField = (key) => {
  if (Array.isArray(mappingConfig.value[key])) {
    mappingConfig.value[key].push(null)
  }
}

const removeField = (key, index) => {
  if (Array.isArray(mappingConfig.value[key]) && mappingConfig.value[key].length > 1) {
    mappingConfig.value[key].splice(index, 1)
  }
}

const getConcatenatedPreview = (key) => {
  if (!Array.isArray(mappingConfig.value[key]) || csvPreview.value.length === 0) {
    return ''
  }
  
  const firstRow = csvPreview.value[0]
  const values = mappingConfig.value[key]
    .filter(idx => idx !== null && idx !== undefined)
    .map(idx => firstRow[idx] || '')
    .filter(val => val !== '')
  
  return values.length > 0 ? values.join(' ') : ''
}

const getFieldValue = (row, fieldConfig) => {
  if (fieldConfig === null || fieldConfig === undefined) {
    return ''
  }
  
  if (Array.isArray(fieldConfig)) {
    const values = fieldConfig
      .filter(idx => idx !== null && idx !== undefined)
      .map(idx => row[idx] || '')
      .filter(val => val !== '')
    return values.join(' ')
  }
  
  return row[fieldConfig] || ''
}

const previewData = computed(() => {
  if (!hasMapping.value || csvPreview.value.length === 0) return []
  
  return csvPreview.value.slice(0, 5).map(row => ({
    name: getFieldValue(row, mappingConfig.value.name),
    email: getFieldValue(row, mappingConfig.value.email),
    position: getFieldValue(row, mappingConfig.value.position),
    department: getFieldValue(row, mappingConfig.value.department)
  }))
})

const getSampleData = (index) => {
  const firstRow = csvPreview.value[0]
  return firstRow ? firstRow[index] : ''
}

const loadSavedMapping = () => {
  if (selectedSavedMapping.value) {
    csvStore.loadSavedMapping(selectedSavedMapping.value)
    mappingConfig.value = { ...csvStore.mappingConfig }
    ElMessage.success('保存済み設定を読み込みました')
  }
}

const usePreviousMapping = () => {
  if (savedMappings.value.length > 0) {
    const lastMapping = savedMappings.value[savedMappings.value.length - 1]
    selectedSavedMapping.value = lastMapping.id
    loadSavedMapping()
  }
}

const saveMapping = () => {
  if (!mappingName.value) {
    ElMessage.warning('設定名を入力してください')
    return
  }
  
  csvStore.addSavedMapping({
    name: mappingName.value,
    config: { ...mappingConfig.value }
  })
  
  ElMessage.success('マッピング設定を保存しました')
  mappingName.value = ''
}

const goBack = () => {
  // Save current mapping configuration to store before navigating
  csvStore.setMappingConfig(mappingConfig.value)
  router.push('/upload')
}

const proceedToConfirm = () => {
  if (!isValidMapping.value) {
    ElMessage.warning('メールアドレスフィールドは必須です')
    return
  }
  
  logger.info('Proceeding to confirmation', {
    mappingConfig: mappingConfig.value,
    uploadData: csvStore.uploadData,
    sessionId: csvStore.uploadData?.session_id
  })
  
  csvStore.setMappingConfig(mappingConfig.value)
  
  logger.info('Mapping config saved to store', {
    storedMappingConfig: csvStore.mappingConfig,
    emailMapping: csvStore.mappingConfig.email
  })
  
  loading.value = true
  setTimeout(() => {
    router.push('/confirm')
  }, 500)
}

// Watch for mapping changes and save to store
watch(mappingConfig, (newValue) => {
  logger.debug('Mapping config changed', {
    newValue,
    emailMapping: newValue.email
  })
  csvStore.setMappingConfig(newValue)
}, { deep: true })

onMounted(() => {
  logger.info('FieldMapping mounted', {
    hasUploadData: !!csvStore.uploadData,
    uploadData: csvStore.uploadData,
    existingMappingConfig: csvStore.mappingConfig,
    initialMappingConfig: mappingConfig.value
  })
  
  if (!csvStore.uploadData) {
    ElMessage.warning('CSVファイルがアップロードされていません')
    router.push('/upload')
  }
})

// Save mapping configuration before leaving the component
onBeforeUnmount(() => {
  csvStore.setMappingConfig(mappingConfig.value)
})
</script>

<style lang="scss" scoped>
.field-mapping-container {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  h2 {
    margin: 0 0 20px 0;
  }
}

.mapping-section {
  .saved-mappings {
    margin-bottom: 30px;
    display: flex;
    align-items: center;
  }
  
  .mapping-table {
    h3 {
      margin-bottom: 10px;
      color: #333;
    }
    
    .mapping-note {
      margin: 0 0 20px 0;
      color: #666;
      font-size: 14px;
      display: flex;
      align-items: center;
      gap: 5px;
      
      .el-icon {
        color: #409eff;
      }
      
      .required-mark {
        color: #f56c6c;
        font-weight: bold;
      }
    }
  }
  
  .mapping-grid {
    background-color: #f5f5f5;
    padding: 20px;
    border-radius: 4px;
  }
  
  .mapping-row {
    display: grid;
    grid-template-columns: 200px 50px 1fr;
    align-items: start;
    margin-bottom: 20px;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  .system-field {
    text-align: right;
    padding-top: 5px;
  }
  
  .arrow {
    text-align: center;
    color: #909399;
    padding-top: 5px;
  }
  
  .csv-field {
    .option-content {
      display: flex;
      align-items: center;
      width: 100%;
      gap: 10px;
      
      .column-name {
        flex: 0 0 200px;
        min-width: 200px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      
      .sample-data {
        flex: 1;
        max-width: 250px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
    
    .multiple-fields {
      .field-row {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
      }
      
      .concat-preview {
        margin-top: 10px;
        padding: 10px;
        background-color: #f0f9ff;
        border-radius: 4px;
      }
    }
  }
  
  .mapping-preview {
    margin-top: 30px;
    
    h3 {
      margin-bottom: 15px;
      color: #333;
    }
  }
  
  .save-mapping {
    margin-top: 20px;
    display: flex;
    align-items: center;
  }
}

.action-buttons {
  margin-top: 30px;
  display: flex;
  justify-content: space-between;
}
</style>

<style lang="scss">
// Global styles for dropdown (unscoped)
.field-mapping-dropdown {
  .el-select-dropdown__item {
    height: auto;
    padding: 8px 12px;
    
    .option-content {
      display: flex;
      align-items: center;
      width: 100%;
      gap: 10px;
      
      .column-name {
        flex: 0 0 200px;
        min-width: 200px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        text-align: right;
        padding-right: 10px;
      }
      
      .sample-data {
        flex: 1;
        max-width: 250px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
  }
}
</style>