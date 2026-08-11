<template>
  <div class="notice-list-page">
    <el-card class="header-card" v-reveal>
      <h2>📢 平台公告</h2>
      <p>了解平台最新动态、活动与重要通知</p>
    </el-card>

    <el-card>
      <div class="toolbar">
        <el-radio-group v-model="typeFilter" @change="reload">
          <el-radio-button :value="null">全部</el-radio-button>
          <el-radio-button :value="0">系统公告</el-radio-button>
          <el-radio-button :value="1">活动通知</el-radio-button>
          <el-radio-button :value="2">重要通知</el-radio-button>
        </el-radio-group>
      </div>

      <div v-if="loading" class="loading">
        <el-skeleton :rows="5" animated />
      </div>

      <el-empty v-else-if="notices.length === 0" description="暂无公告" />

      <div v-else>
        <div v-for="(notice, idx) in notices" :key="notice.id" class="notice-item" v-reveal="{ delay: (idx % 5) * 60 }" @click="goDetail(notice.id)">
          <div class="notice-title">
            <el-tag v-if="notice.isTop === 1" type="danger" size="small">置顶</el-tag>
            <el-tag size="small" :type="tagType(notice.type)">{{ typeName(notice.type) }}</el-tag>
            <span class="title-text">{{ notice.title }}</span>
          </div>
          <div class="notice-meta">
            <span>发布时间：{{ notice.publishTime || notice.createTime }}</span>
          </div>
        </div>

        <div class="pagination" v-if="total > 0">
          <el-pagination
            v-model:page-num="pageNum"
            v-model:page-size="pageSize"
            :total="total"
            layout="total, prev, pager, next"
            @current-change="loadNotices"
          />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getNoticeList } from '@/api/notice'

const router = useRouter()
const loading = ref(false)
const notices = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(10)
const typeFilter = ref(null)

const typeName = (type) => {
  const map = { '0': '系统公告', '1': '活动通知', '2': '重要通知' }
  return map[String(type)] || '公告'
}

const tagType = (type) => {
  const map = { '0': 'primary', '1': 'success', '2': 'danger' }
  return map[String(type)] || 'info'
}

const loadNotices = async () => {
  loading.value = true
  try {
    const params = { pageNum: pageNum.value, pageSize: pageSize.value }
    if (typeFilter.value !== null && typeFilter.value !== '') {
      params.type = typeFilter.value
    }
    const res = await getNoticeList(params)
    if (res.code === 200) {
      notices.value = res.data?.records || []
      total.value = res.data?.total || 0
    }
  } catch (error) {
    console.error('加载公告失败', error)
  } finally {
    loading.value = false
  }
}

const reload = () => {
  pageNum.value = 1
  loadNotices()
}

const goDetail = (id) => {
  router.push(`/notice/${id}`)
}

onMounted(loadNotices)
</script>

<style scoped>
.notice-list-page { animation: slideUp 0.3s ease; }
.header-card { margin-bottom: 20px; }
.header-card h2 { margin: 0 0 8px; }
.header-card p { margin: 0; color: #999; font-size: 13px; }
.toolbar { margin-bottom: 16px; }
.notice-item {
  padding: 14px 16px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s;
}
.notice-item:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border-color: #409eff;
}
.notice-title { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.title-text { font-size: 15px; font-weight: 600; color: #333; }
.notice-meta { font-size: 12px; color: #999; }
.pagination { display: flex; justify-content: center; padding: 20px 0; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>