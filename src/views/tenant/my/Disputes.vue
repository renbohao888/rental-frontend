<template>
  <div class="disputes-page">
    <div class="page-header">
      <h2>⚖️ 纠纷管理</h2>
      <el-button type="primary" @click="showDisputeDialog">+ 申请纠纷处理</el-button>
    </div>

    <el-empty v-if="disputes.length === 0 && !loading" description="暂无纠纷记录" />

    <div v-if="loading" class="loading">
      <el-skeleton :rows="3" animated />
    </div>

    <div v-for="dispute in disputes" :key="dispute.id" class="dispute-card">
      <div class="dispute-header">
        <div>
          <div class="dispute-title">{{ dispute.title }}</div>
          <el-tag :type="getStatusType(dispute.status)">{{ getStatusName(dispute.status) }}</el-tag>
        </div>
        <div class="dispute-time">{{ formatDate(dispute.createTime) }}</div>
      </div>
      <div class="dispute-content">{{ dispute.description }}</div>
      <div class="dispute-info">
        <div>订单号：{{ dispute.orderNo }}</div>
        <div>金额：¥{{ dispute.amount }}</div>
      </div>
      <div v-if="dispute.remark" class="dispute-remark">
        <div class="remark-label">管理员备注：</div>
        <div class="remark-text">{{ dispute.remark }}</div>
      </div>
      <div class="dispute-actions">
        <el-button type="primary" size="small" @click="viewDetail(dispute.id)">查看详情</el-button>
      </div>
    </div>

    <!-- 申请纠纷对话框 -->
    <el-dialog v-model="disputeDialogVisible" title="申请纠纷处理" width="500px">
      <el-form :model="disputeForm" label-width="80px">
        <el-form-item label="订单号">
          <el-select v-model="disputeForm.orderId" placeholder="选择订单">
            <el-option v-for="order in orders" :key="order.id" :label="order.orderNo" :value="order.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="纠纷类型">
          <el-select v-model="disputeForm.type" placeholder="选择纠纷类型">
            <el-option label="房东违约" value="landlord_breach" />
            <el-option label="房屋问题" value="room_issue" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="问题描述">
          <el-input v-model="disputeForm.description" type="textarea" placeholder="请详细描述问题" rows="4" />
        </el-form-item>
        <el-form-item label="索赔金额">
          <el-input v-model.number="disputeForm.amount" type="number" placeholder="请输入要求赔偿金额" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="disputeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitDispute" :loading="submitting">提交申请</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const disputes = ref([])
const orders = ref([])
const disputeDialogVisible = ref(false)
const submitting = ref(false)

const disputeForm = reactive({
  orderId: '',
  type: '',
  description: '',
  amount: 0
})

const getStatusType = (status) => {
  const map = { '0': 'warning', '1': 'info', '2': 'success', '3': 'danger' }
  return map[String(status)] || 'default'
}

const getStatusName = (status) => {
  const map = { '0': '待审核', '1': '处理中', '2': '已解决', '3': '已驳回' }
  return map[String(status)] || '未知'
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString()
}

const loadDisputes = async () => {
  loading.value = true
  try {
    const res = await request({
      url: '/dispute/list',
      method: 'get'
    })

    if (res.code === 200) {
      disputes.value = res.data || []
    }
  } catch (error) {
    console.error('加载纠纷列表失败', error)
  } finally {
    loading.value = false
  }
}

const showDisputeDialog = async () => {
  // 加载可用订单
  try {
    const res = await request({
      url: '/order/tenant/list',
      method: 'get',
      params: { pageSize: 100 }
    })
    if (res.code === 200) {
      orders.value = res.data?.records || []
    }
  } catch (error) {
    console.error('加载订单失败', error)
  }

  disputeForm.orderId = ''
  disputeForm.type = ''
  disputeForm.description = ''
  disputeForm.amount = 0
  disputeDialogVisible.value = true
}

const submitDispute = async () => {
  if (!disputeForm.orderId || !disputeForm.type || !disputeForm.description) {
    ElMessage.warning('请填写必要信息')
    return
  }

  submitting.value = true
  try {
    const res = await request({
      url: '/dispute/add',
      method: 'post',
      data: disputeForm
    })

    if (res.code === 200) {
      ElMessage.success('纠纷申请已提交')
      disputeDialogVisible.value = false
      loadDisputes()
    } else {
      ElMessage.error(res.message || '提交失败')
    }
  } catch (error) {
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}

const viewDetail = (id) => {
  ElMessage.info('纠纷详情页面开发中...')
}

onMounted(() => {
  loadDisputes()
})
</script>

<style scoped>
.disputes-page {
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

.dispute-card {
  padding: 16px;
  margin-bottom: 12px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
}

.dispute-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.dispute-title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 6px;
}

.dispute-time {
  font-size: 12px;
  color: #999;
}

.dispute-content {
  padding: 12px;
  background-color: #f9f9f9;
  border-radius: 4px;
  margin-bottom: 12px;
  font-size: 13px;
  line-height: 1.6;
  color: #666;
}

.dispute-info {
  display: flex;
  gap: 20px;
  margin-bottom: 12px;
  font-size: 13px;
  color: #666;
}

.dispute-remark {
  padding: 12px;
  background-color: #fff7e6;
  border-radius: 4px;
  margin-bottom: 12px;
  border-left: 3px solid #ffa726;
}

.remark-label {
  font-weight: 600;
  font-size: 12px;
  color: #ffa726;
  margin-bottom: 6px;
}

.remark-text {
  font-size: 13px;
  color: #666;
  line-height: 1.6;
}

.dispute-actions {
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

@media (max-width: 768px) {
  .disputes-page {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
