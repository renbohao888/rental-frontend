<template>
  <div class="page-container">
    <el-card class="header-card">
      <h2>🏘️ 房东入驻</h2>
      <p>查看您的入驻状态与资料</p>
    </el-card>

    <el-card>
      <div v-loading="loading" class="apply-body">
        <el-result icon="success" title="您已入驻成功" sub-title="您现在可以发布房源、管理订单与报修，享受房东权益">
          <template #extra>
            <el-button type="primary" @click="$router.push('/landlord/rooms')">管理房源</el-button>
            <el-button @click="$router.push('/landlord/dashboard')">查看仪表盘</el-button>
          </template>
        </el-result>

        <el-divider>房东资料</el-divider>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="昵称">{{ userInfo.nickname || '-' }}</el-descriptions-item>
          <el-descriptions-item label="账号">{{ userInfo.accountNo || '-' }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ userInfo.phone || '-' }}</el-descriptions-item>
          <el-descriptions-item label="身份认证">
            <el-tag :type="userInfo.isVerified ? 'success' : 'warning'">{{ userInfo.isVerified ? '已认证' : '未认证' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="角色">
            <el-tag type="warning">房东</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <el-alert
          title="温馨提示"
          type="info"
          :closable="false"
          description="如需补充认证资料或修改房东信息，请联系平台管理员处理。"
          style="margin-top: 20px;"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'

const loading = ref(false)
const userInfo = ref({})

onMounted(async () => {
  loading.value = true
  try {
    const res = await request({ url: '/user/info', method: 'get' })
    if (res.code === 200) {
      userInfo.value = res.data || {}
    }
  } catch (error) {
    console.error('加载用户信息失败', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page-container { animation: slideUp 0.3s ease; }
.header-card { margin-bottom: 20px; }
.header-card h2 { margin: 0 0 8px; }
.header-card p { margin: 0; color: #999; font-size: 13px; }
.apply-body { min-height: 320px; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>