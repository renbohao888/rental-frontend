<template>
  <div class="evaluations-page">
    <h2>⭐ 我的评价</h2>
    <div v-for="item in evaluations" :key="item.id" class="eval-item">
      <el-card>
        <div class="eval-header">
          <span class="room-title">{{ item.roomTitle }}</span>
          <el-rate v-model="item.rating" disabled />
          <span class="time">{{ item.createTime?.slice(0,10) }}</span>
        </div>
        <div class="eval-content">{{ item.content }}</div>
        <div v-if="item.replyContent" class="eval-reply">
          <span class="reply-label">房东回复：</span>
          {{ item.replyContent }}
        </div>
      </el-card>
    </div>
    <el-empty v-if="evaluations.length === 0" description="暂无评价" />
    <div class="pagination">
      <el-pagination
        v-model:page-num="pageNum"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="loadEvaluations"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'

const evaluations = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(8)

const loadEvaluations = async () => {
  try {
    const res = await request({
      url: '/evaluation/my',
      method: 'get',
      params: { pageNum: pageNum.value, pageSize: pageSize.value }
    })
    if (res.code === 200) {
      evaluations.value = res.data.records || []
      total.value = res.data.total || 0
    }
  } catch (error) {
    console.error('加载评价失败', error)
  }
}

onMounted(loadEvaluations)
</script>

<style scoped>
.evaluations-page { max-width: 800px; margin: 0 auto; padding: 20px; }
.eval-item { margin-bottom: 16px; }
.eval-header { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.room-title { font-weight: bold; font-size: 16px; }
.time { color: #999; font-size: 13px; margin-left: auto; }
.eval-content { margin: 10px 0; }
.eval-reply { background: var(--bg-soft); padding: 10px; border-radius: 4px; }
.reply-label { color: #409eff; }
.pagination { display: flex; justify-content: center; padding: 20px 0; }
</style>