import { createRouter, createWebHistory } from 'vue-router'
import CsvUpload from '@/views/CsvUpload.vue'
import FieldMapping from '@/views/FieldMapping.vue'
import SyncConfirm from '@/views/SyncConfirm.vue'
import ProcessResult from '@/views/ProcessResult.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/upload'
    },
    {
      path: '/upload',
      name: 'upload',
      component: CsvUpload
    },
    {
      path: '/mapping',
      name: 'mapping',
      component: FieldMapping
    },
    {
      path: '/confirm',
      name: 'confirm',
      component: SyncConfirm
    },
    {
      path: '/result',
      name: 'result',
      component: ProcessResult
    }
  ]
})

export default router