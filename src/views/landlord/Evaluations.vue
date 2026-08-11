<template>
  <div class="page-container">
    <el-card class="header-card">
      <h2>⭐ 评价管理</h2>
      <p>查看租客评价并回复</p>
    </el-card>

    <el-card>
      <el-empty v-if="evaluations.length === 0 && !loading" description="暂无评价" />

      <div v-for="item in evaluations" :key="item.id" class="eval-card">
        <div class="eval-head">
          <el-avatar :src="item.userAvatar" :size="36">{{ (item.userNickname || '客')[0] }}</el-avatar>
          <div class="eval-user">
            <div class="name">{{ item.userNickname || '租客' }}</div>
            <el-rate :model-value="item.rating" disabled size="small" />
          </div>
          <span class="eval-time">{{ item.createTime }}</span>
        </div>
        <div class="eval-room">🏠 {{ item.roomTitle }}</div>
        <div class="eval-content">{{ item.content }}</div>
        <div class="eval-reply" v-if="item.replyContent">
          <b>房东回复：</b>{{ item.replyContent }}<span class="reply-time">（{{ item.replyTime }}）</span>
        </div>
        <el-button v-if="!item.replyContent" type="primary" size="small" plain @click="openReply(item)">回复</el-button>
      </div>

      <div class="pagination" v-if="total > 0">
        <el-pagination v-model:page-num="pageNum" v-model:page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="loadEvaluations" />
      </div>
    </el-card>

    <el-dialog v-model="replyVisible" title="回复评价" width="480px">
      <el-input v-model="replyContent" type="textarea" :rows="4" placeholder="请输入回复内容" />
      <template #footer>
        <el-button @click="replyVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReply">提交回复</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const evaluations = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(10)
const replyVisible = ref(false)
const replyContent = ref('')
const currentEval = ref(null)

const loadEvaluations = async () => {
  loading.value = true
  try {
    const res = await request({
      url: '/evaluation/landlord/list',
      method: 'get',
      params: { pageNum: pageNum.value, pageSize: pageSize.value }
    })
    if (res.code === 200) {
      evaluations.value = res.data?.records || []
      total.value = res.data?.total || 0
    } else {
      ElMessage.error(res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载评价失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
}

const openReply = (item) => {
  currentEval.value = item
  replyContent.value = ''
  replyVisible.value = true
}

const submitReply = async () => {
  if (!replyContent.value.trim()) {
    ElMessage.warning('请输入回复内容')
    return
  }
  try {
    const res = await request({
      url: '/evaluation/reply',
      method: 'post',
      data: { evaluationId: currentEval.value.id, replyContent: replyContent.value }
    })
    if (res.code === 200) {
      ElMessage.success('回复成功')
      replyVisible.value = false
      loadEvaluations()
    } else {
      ElMessage.error(res.message || '回复失败')
    }
  } catch (error) {
    ElMessage.error('网络请求失败')
  }
}

onMounted(loadEvaluations)
</script>

<style scoped>
.page-container { animation: slideUp 0.3s ease; }
.header-card { margin-bottom: 20px; }
.header-card h2 { margin: 0 0 8px; }
.header-card p { margin: 0; color: #999; font-size: 13px; }
.eval-card { border-bottom: 1px solid #eee; padding: 16px 0; }
.eval-card:last-child { border-bottom: none; }
.eval-head { display: flex; align-items: center; gap: 12px; }
.eval-user .name { font-weight: 600; }
.eval-time { margin-left: auto; color: #999; font-size: 12px; }
.eval-room { margin: 10px 0 6px; color: #409eff; font-size: 13px; }
.eval-content { color: #333; line-height: 1.6; margin-bottom: 8px; }
.eval-reply { background: var(--bg-soft); border-radius: 6px; padding: 10px 12px; font-size: 13px; color: var(--text-sub); margin-bottom: 8px; }
.reply-time { color: #999; font-size: 12px; }
.pagination { display: flex; justify-content: center; padding: 20px 0; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>