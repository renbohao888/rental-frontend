<template>
  <div class="evaluations-page">
    <div class="page-header">
      <h2>⭐ 我的评价</h2>
      <el-button type="primary" size="small" @click="openDialog">＋ 发表评价</el-button>
    </div>

    <el-empty v-if="evaluations.length === 0 && !loading" description="暂无评价" />

    <div v-if="loading" class="loading">
      <el-skeleton :rows="3" animated />
    </div>

    <div v-for="item in evaluations" :key="item.id" class="evaluation-card">
      <div class="evaluation-header">
        <div class="room-info">
          <img :src="item.roomCover" class="room-thumb" />
          <div class="room-title">{{ item.roomTitle || '房源评价' }}</div>
        </div>
        <div class="evaluation-time">{{ formatDate(item.createTime) }}</div>
      </div>
      <div class="rating">
        <el-rate :model-value="item.rating" disabled />
      </div>
      <div class="content">{{ item.content }}</div>
      <div v-if="item.replyContent" class="reply">
        <div class="reply-label">房东回复：</div>
        <div>{{ item.replyContent }}</div>
        <div class="reply-time">{{ formatDate(item.replyTime) }}</div>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" title="发表评价" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="订单" required>
          <el-select v-model="form.orderId" placeholder="请选择已完成订单" style="width: 100%">
            <el-option
              v-for="order in completedOrders"
              :key="order.id"
              :label="(order.roomTitleSnapshot || '房源') + '（' + order.orderNo + '）'"
              :value="order.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="评分" required>
          <el-rate v-model="form.rating" />
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="4"
            placeholder="分享一下你的入住体验吧～"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitEvaluation">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const route = useRoute()
const loading = ref(false)
const evaluations = ref([])
const completedOrders = ref([])
const dialogVisible = ref(false)
const submitting = ref(false)

const form = reactive({
  orderId: null,
  rating: 5,
  content: ''
})

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString()
}

const loadEvaluations = async () => {
  loading.value = true
  try {
    const res = await request({
      url: '/evaluation/list',
      method: 'get'
    })
    if (res.code === 200) {
      evaluations.value = res.data || []
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

const loadCompletedOrders = async () => {
  try {
    const res = await request({
      url: '/order/tenant/list',
      method: 'get',
      params: { pageNum: 1, pageSize: 100, status: 4 }
    })
    if (res.code === 200) {
      completedOrders.value = res.data?.records || []
    }
  } catch (error) {
    console.error('加载订单失败', error)
  }
}

const openDialog = () => {
  form.orderId = route.query.orderId ? String(route.query.orderId) : null
  form.rating = 5
  form.content = ''
  dialogVisible.value = true
}

const submitEvaluation = async () => {
  if (!form.orderId) {
    ElMessage.warning('请选择已完成订单')
    return
  }
  if (!form.rating || form.rating < 1) {
    ElMessage.warning('请选择评分')
    return
  }
  if (!form.content.trim()) {
    ElMessage.warning('请输入评价内容')
    return
  }

  submitting.value = true
  try {
    const res = await request({
      url: '/evaluation/add',
      method: 'post',
      data: {
        orderId: form.orderId,
        rating: form.rating,
        content: form.content,
        images: ''
      }
    })
    if (res.code === 200) {
      ElMessage.success('评价发表成功')
      dialogVisible.value = false
      loadEvaluations()
      loadCompletedOrders()
    } else {
      ElMessage.error(res.message || '提交失败')
    }
  } catch (error) {
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadEvaluations()
  loadCompletedOrders()
})
</script>
<style scoped>
.evaluations-page {
  background: var(--bg-card);
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}

.evaluation-card {
  padding: 16px;
  margin-bottom: 12px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
}

.eval-header {
  margin-bottom: 12px;
}

.room-name {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 6px;
}

.eval-stars {
  display: flex;
  align-items: center;
  gap: 12px;
}

.eval-date {
  font-size: 12px;
  color: #999;
}

.eval-content {
  padding: 12px;
  background-color: #f9f9f9;
  border-radius: 4px;
  margin-bottom: 12px;
  font-size: 13px;
  line-height: 1.6;
  color: #666;
}

.eval-images {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.eval-image {
  width: 80px;
  height: 80px;
  border-radius: 4px;
  object-fit: cover;
  cursor: pointer;
}

@media (max-width: 768px) {
  .evaluations-page {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
