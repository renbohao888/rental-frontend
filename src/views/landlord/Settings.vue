<template>
  <div class="settings-page">
    <el-card>
      <el-tabs>
        <el-tab-pane label="🔔 通知设置">
          <el-form :model="notificationSettings" label-width="180px">
            <el-form-item label="新订单提醒">
              <el-switch v-model="notificationSettings.newOrder" />
            </el-form-item>
            <el-form-item label="新消息提醒">
              <el-switch v-model="notificationSettings.newMessage" />
            </el-form-item>
            <el-form-item label="维修报告提醒">
              <el-switch v-model="notificationSettings.repair" />
            </el-form-item>
            <el-form-item label="订单评价提醒">
              <el-switch v-model="notificationSettings.evaluation" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSettings">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="🔐 账户安全">
          <el-form label-width="180px">
            <el-form-item label="修改密码">
              <el-button @click="showPasswordDialog = true">修改密码</el-button>
            </el-form-item>
            <el-form-item label="绑定手机">
              <span>{{ form.phone }}</span>
              <el-button link type="primary" @click="changePhone">更改</el-button>
            </el-form-item>
            <el-form-item label="登录记录">
              <el-button @click="viewLoginLog">查看登录记录</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="⚙️ 高级设置">
          <el-form :model="advancedSettings" label-width="180px">
            <el-form-item label="自动接单">
              <el-switch v-model="advancedSettings.autoAccept" />
            </el-form-item>
            <el-form-item label="隐藏手机号">
              <el-switch v-model="advancedSettings.hidePhone" />
            </el-form-item>
            <el-form-item label="数据导出">
              <el-button @click="exportData">导出数据</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const notificationSettings = ref({
  newOrder: true,
  newMessage: true,
  repair: true,
  evaluation: true
})

const advancedSettings = ref({
  autoAccept: false,
  hidePhone: false
})

const form = ref({
  phone: '13800138000'
})

const showPasswordDialog = ref(false)

const saveSettings = () => ElMessage.success('设置已保存')
const changePhone = () => ElMessage.info('修改手机号')
const viewLoginLog = () => ElMessage.info('查看登录记录')
const exportData = () => ElMessage.success('数据导出已开始')
</script>

<style scoped>
.settings-page {
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
