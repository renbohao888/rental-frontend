<template>
  <div class="notice-detail-page">
    <el-card v-loading="loading">
      <template v-if="notice">
        <div class="detail-header">
          <h2 class="detail-title">
            <el-tag v-if="notice.isTop === 1" type="danger" size="small" class="top-tag">置顶</el-tag>
            {{ notice.title }}
          </h2>
          <div class="detail-meta">
            <el-tag size="small">{{ typeName(notice.type) }}</el-tag>
            <span>发布时间：{{ notice.publishTime || notice.createTime }}</span>
          </div>
        </div>
        <el-divider />
        <div class="detail-content">{{ notice.content }}</div>
      </template>
      <el-empty v-else-if="!loading" description="公告不存在或未发布" />

      <div class="back-row">
        <el-button @click="$router.push('/notices')">← 返回公告列表</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import request from '@/utils/request'

const route = useRoute()
const loading = ref(false)
const notice = ref(null)

const typeName = (type) => {
  const map = { '0': '系统公告', '1': '活动通知', '2': '重要通知' }
  return map[String(type)] || '公告'
}

const loadDetail = async () => {
  loading.value = true
  try {
    const res = await request({ url: `/notice/detail/${route.params.id}`, method: 'get' })
    if (res.code === 200) {
      notice.value = res.data
    }
  } catch (error) {
    console.error('加载公告详情失败', error)
  } finally {
    loading.value = false
  }
}

onMounted(loadDetail)
</script>

<style scoped>
.notice-detail-page { animation: slideUp 0.3s ease; }
.detail-title { margin: 0 0 12px; font-size: 20px; }
.top-tag { vertical-align: middle; }
.detail-meta { display: flex; align-items: center; gap: 12px; color: #999; font-size: 13px; }
.detail-content {
  white-space: pre-wrap;
  line-height: 1.9;
  font-size: 14px;
  color: #333;
  min-height: 120px;
}
.back-row { margin-top: 20px; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>