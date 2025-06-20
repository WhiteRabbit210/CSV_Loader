import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCsvStore = defineStore('csv', () => {
  const uploadData = ref(null)
  const mappingConfig = ref({
    name: null,
    email: null,
    position: null,
    department: null
  })
  const savedMappings = ref([])
  const syncResults = ref(null)

  function setUploadData(data) {
    uploadData.value = data
  }

  function setMappingConfig(config) {
    console.log('[CSV Store] Setting mapping config:', {
      config,
      emailValue: config?.email,
      previousValue: mappingConfig.value
    })
    mappingConfig.value = config
  }

  function addSavedMapping(mapping) {
    savedMappings.value.push({
      id: Date.now(),
      name: mapping.name,
      config: mapping.config,
      createdAt: new Date().toISOString()
    })
  }

  function loadSavedMapping(id) {
    const mapping = savedMappings.value.find(m => m.id === id)
    if (mapping) {
      mappingConfig.value = { ...mapping.config }
    }
  }

  function setSyncResults(results) {
    syncResults.value = results
  }

  function reset() {
    uploadData.value = null
    mappingConfig.value = {
      name: null,
      email: null,
      position: null,
      department: null
    }
    syncResults.value = null
  }

  // Debug getter to check mapping config
  const getMappingConfig = () => {
    console.log('[CSV Store] Getting mapping config:', mappingConfig.value)
    return mappingConfig.value
  }

  return {
    uploadData,
    mappingConfig,
    savedMappings,
    syncResults,
    setUploadData,
    setMappingConfig,
    addSavedMapping,
    loadSavedMapping,
    setSyncResults,
    reset,
    getMappingConfig
  }
})