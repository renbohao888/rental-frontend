<template>
  <router-view />
  <!-- 全局 AI 租赁助手悬浮窗 -->
  <AiAssistant />
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AiAssistant from '@/components/AiAssistant.vue'
import { autoRevealScan } from '@/utils/autoReveal'

const router = useRouter()
// 每次路由切换后自动为页面主要区块添加滚动入场动画（基本所有网页都有动效）
router.afterEach(autoRevealScan)
onMounted(autoRevealScan)
</script>

<style>
html, body, #app {
  margin: 0;
  padding: 0;
  height: 100%;
}

body {
  color: var(--text-main, #1a1a2e);
  background: var(--bg-page, #f5f5f5);
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-thumb {
  background: rgba(255, 106, 0, 0.35);
  border-radius: 4px;
}
::-webkit-scrollbar-track {
  background: transparent;
}

/* 手机端全局表格横向滚动 */
@media (max-width: 768px) {
  .el-table {
    overflow-x: auto !important;
    display: block !important;
  }
  .el-table .el-table__inner-wrapper {
    min-width: 600px;
  }
  .el-pagination {
    flex-wrap: wrap;
    justify-content: center;
  }
  .el-dialog {
    width: 92% !important;
    margin: 10px auto !important;
  }
}
</style>
