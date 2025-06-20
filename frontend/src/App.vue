<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <h1>CSV Loader - ユーザー管理システム</h1>
    </el-header>
    <el-main class="app-main">
      <router-view></router-view>
    </el-main>
  </el-container>
  
  <!-- デバッグパネル -->
  <DebugPanel :logger="logger" />
</template>

<script setup>
import { getCurrentInstance } from 'vue'
import DebugPanel from '@/components/DebugPanel.vue'

const instance = getCurrentInstance()
const logger = instance.appContext.config.globalProperties.$logger
</script>

<style lang="scss">
.app-container {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.app-header {
  background-color: #409eff;
  color: white;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,.12);
  
  h1 {
    margin: 0;
    font-size: 24px;
  }
}

.app-main {
  padding: 20px;
}
</style>