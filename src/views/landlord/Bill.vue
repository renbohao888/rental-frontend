<template>
  <div class="page-container">
    <el-card class="header-card">
      <h2>💳 账单统计</h2>
      <p>按房源维度统计订单与收入（仅统计已完成订单）</p>
    </el-card>

    <el-card>
      <el-empty v-if="bills.length === 0 && !loading" description="暂无账单数据" />

      <el-table v-if="!loading" :data="bills" border stripe style="width: 100%">
        <el-table-column prop="roomId" label="房源ID" width="100" />
        <el-table-column prop="roomTitle" label="房源名称" min-width="200" />
        <el-table-column prop="totalOrders" label="总订单数" width="100" align="center" />
        <el-table-column prop="completedOrders" label="已完成订单" width="110" align="center" />
        <el-table-column label="租金收入" width="130" align="right">
          <template #default="{ row }"><span class="money">¥{{ row.totalRevenue || 0 }}</span></template>
        </el-table-column>
        <el-table-column label="押金总额" width="130" align="right">
          <template #default="{ row }">¥{{ row.totalDeposit || 0 }}</template>
        </el-table-column>
      </el-table>

      <div class="total-bar" v-if="bills.length > 0">
        <span>累计租金收入：<b>¥{{ totalRevenueSum }}</b></span>
        <span>累计订单：<b>{{ totalOrderSum }}</b> 单</span>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const bills = ref([])

const totalRevenueSum = computed(() => bills.value.reduce((s, b) => s + Number(b.totalRevenue || 0), 0))
const totalOrderSum = computed(() => bills.value.reduce((s, b) => s + Number(b.totalOrders || 0), 0))

const loadBills = async () => {
  loading.value = true
  try {
    const res = await request({ url: '/room/bill/rooms', method: 'get' })
    if (res.code === 200) {
      bills.value = Array.isArray(res.data) ? res.data : []
    } else {
      ElMessage.error(res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载账单失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadBills)
</script>

<style scoped>
.page-container { animation: slideUp 0.3s ease; }
.header-card { margin-bottom: 20px; }
.header-card h2 { margin: 0 0 8px; }
.header-card p { margin: 0; color: #999; font-size: 13px; }
.money { color: #e6a23c; font-weight: 600; }
.total-bar { margin-top: 16px; padding: 14px 16px; background: var(--bg-soft); border-radius: 6px; display: flex; gap: 32px; color: var(--text-sub); }
.total-bar b { color: #e6a23c; font-size: 16px; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>