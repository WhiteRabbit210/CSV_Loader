<template>
  <div class="debug-panel" v-if="visible">
    <div class="debug-header">
      <h3>Debug Logs</h3>
      <div class="debug-controls">
        <el-select v-model="selectedLogType" size="small" style="width: 120px">
          <el-option label="All" value="all" />
          <el-option label="Info" value="info" />
          <el-option label="Error" value="error" />
          <el-option label="Network" value="network" />
          <el-option label="Debug" value="debug" />
        </el-select>
        <el-button size="small" @click="clearLogs">Clear</el-button>
        <el-button size="small" @click="exportLogs">Export</el-button>
        <el-button size="small" @click="visible = false" circle>
          <el-icon><close /></el-icon>
        </el-button>
      </div>
    </div>
    
    <div class="debug-content">
      <div v-if="selectedLogType === 'all' || selectedLogType === 'info'" class="log-section">
        <h4>Info Logs</h4>
        <div class="log-entries">
          <div v-for="(log, index) in infoLogs" :key="`info-${index}`" class="log-entry info">
            <span class="log-time">{{ formatTime(log.timestamp) }}</span>
            <span class="log-message">{{ log.message }}</span>
            <pre v-if="log.data" class="log-data">{{ JSON.stringify(log.data, null, 2) }}</pre>
          </div>
        </div>
      </div>
      
      <div v-if="selectedLogType === 'all' || selectedLogType === 'error'" class="log-section">
        <h4>Error Logs</h4>
        <div class="log-entries">
          <div v-for="(log, index) in errorLogs" :key="`error-${index}`" class="log-entry error">
            <span class="log-time">{{ formatTime(log.timestamp) }}</span>
            <span class="log-message">{{ log.message }}</span>
            <pre v-if="log.data" class="log-data">{{ JSON.stringify(log.data, null, 2) }}</pre>
          </div>
        </div>
      </div>
      
      <div v-if="selectedLogType === 'all' || selectedLogType === 'network'" class="log-section">
        <h4>Network Logs</h4>
        <div class="log-entries">
          <div v-for="(log, index) in networkLogs" :key="`network-${index}`" class="log-entry network">
            <span class="log-time">{{ formatTime(log.timestamp) }}</span>
            <span class="log-method">{{ log.method }}</span>
            <span class="log-url">{{ log.url }}</span>
            <span :class="['log-status', getStatusClass(log.status)]">{{ log.status }}</span>
            <span class="log-time">{{ log.responseTime }}ms</span>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- デバッグパネル開くボタン -->
  <el-button 
    v-if="!visible"
    class="debug-toggle"
    @click="visible = true"
    circle
    size="small"
    type="info"
  >
    <el-icon><view /></el-icon>
  </el-button>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  logger: {
    type: Object,
    required: true
  }
})

const visible = ref(false)
const selectedLogType = ref('all')
const logs = ref({
  info: [],
  error: [],
  network: [],
  debug: []
})

const infoLogs = computed(() => logs.value.info)
const errorLogs = computed(() => logs.value.error)
const networkLogs = computed(() => logs.value.network)

const refreshLogs = () => {
  const allLogs = props.logger.getLogs()
  logs.value = { ...allLogs }
}

const clearLogs = () => {
  props.logger.clearLogs(selectedLogType.value)
  refreshLogs()
}

const exportLogs = () => {
  props.logger.exportLogs()
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString()
}

const getStatusClass = (status) => {
  if (status >= 200 && status < 300) return 'success'
  if (status >= 400 && status < 500) return 'warning'
  if (status >= 500) return 'error'
  return 'info'
}

let interval
onMounted(() => {
  refreshLogs()
  // 定期的にログを更新
  interval = setInterval(refreshLogs, 1000)
})

onUnmounted(() => {
  if (interval) {
    clearInterval(interval)
  }
})
</script>

<style lang="scss" scoped>
.debug-panel {
  position: fixed;
  bottom: 0;
  right: 0;
  width: 600px;
  height: 400px;
  background: white;
  border: 1px solid #ddd;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  
  .debug-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    border-bottom: 1px solid #eee;
    background: #f5f5f5;
    
    h3 {
      margin: 0;
      font-size: 16px;
    }
    
    .debug-controls {
      display: flex;
      gap: 10px;
      align-items: center;
    }
  }
  
  .debug-content {
    flex: 1;
    overflow-y: auto;
    padding: 10px;
    
    .log-section {
      margin-bottom: 20px;
      
      h4 {
        margin: 0 0 10px 0;
        font-size: 14px;
        color: #666;
      }
    }
    
    .log-entries {
      font-family: monospace;
      font-size: 12px;
      
      .log-entry {
        padding: 4px 8px;
        margin-bottom: 4px;
        border-radius: 3px;
        
        &.info {
          background: #f0f9ff;
          color: #0369a1;
        }
        
        &.error {
          background: #fef2f2;
          color: #dc2626;
        }
        
        &.network {
          background: #f7fee7;
          color: #65a30d;
          
          .log-status {
            font-weight: bold;
            
            &.success { color: #22c55e; }
            &.warning { color: #f59e0b; }
            &.error { color: #ef4444; }
          }
        }
        
        .log-time {
          color: #999;
          margin-right: 10px;
        }
        
        .log-method {
          font-weight: bold;
          margin-right: 10px;
        }
        
        .log-url {
          margin-right: 10px;
        }
        
        .log-data {
          margin-top: 5px;
          padding: 5px;
          background: rgba(0,0,0,0.05);
          border-radius: 3px;
          overflow-x: auto;
        }
      }
    }
  }
}

.debug-toggle {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 9998;
}
</style>