<template>
  <div class="forgot-container">
    <div class="forgot-box" v-reveal>
      <div class="logo-area">
        <div class="logo-icon">🔑</div>
        <h1>找回密码</h1>
        <p>输入注册手机号，确认后即可重置密码</p>
      </div>

      <el-form :model="form" :rules="rules" ref="formRef" @keyup.enter="handleReset">
        <el-form-item prop="phone">
          <el-input
            v-model="form.phone"
            placeholder="请输入注册手机号"
            prefix-icon="Phone"
            maxlength="11"
            size="large"
          />
        </el-form-item>

        <el-form-item prop="newPassword">
          <el-input
            v-model="form.newPassword"
            type="password"
            placeholder="请输入新密码（不少于6位）"
            prefix-icon="Lock"
            show-password
            size="large"
          />
        </el-form-item>

        <el-form-item prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            prefix-icon="Lock"
            show-password
            size="large"
          />
        </el-form-item>

        <el-button type="primary" size="large" style="width:100%" @click="handleReset" :loading="loading">
          重置密码
        </el-button>

        <div class="link-row">
          <router-link to="/login">返回登录</router-link>
          <router-link to="/register">没有账号？立即注册</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { resetPassword } from '@/api/user'

const router = useRouter()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  phone: '',
  newPassword: '',
  confirmPassword: ''
})

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== form.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const handleReset = async () => {
  if (!formRef.value) return
  await formRef.value.validate()

  loading.value = true
  try {
    const res = await resetPassword({
      phone: form.phone,
      newPassword: form.newPassword
    })
    if (res.code === 200 || res.code === 0) {
      ElMessage.success(res.message || '密码重置成功，请使用新密码登录')
      router.push('/login')
    } else {
      ElMessage.error(res.message || '重置密码失败')
    }
  } catch (error) {
    console.error('重置密码异常', error)
  } finally {
    loading.value = false
  }
}
</script>


<style scoped>
.forgot-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  position: relative;
  overflow: hidden;
}

.forgot-container::before {
  content: '';
  position: absolute;
  width: 600px;
  height: 600px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  top: -200px;
  right: -200px;
}

.forgot-box {
  width: 100%;
  max-width: 420px;
  padding: 20px;
  position: relative;
  z-index: 1;
}

.forgot-box .el-form {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  padding: 40px 36px;
  border-radius: 20px;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.2);
}

.logo-area {
  text-align: center;
  margin-bottom: 28px;
}

.logo-icon {
  font-size: 42px;
  margin-bottom: 8px;
}

.logo-area h1 {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-main);
  margin: 0 0 4px 0;
  letter-spacing: 2px;
}

.logo-area p {
  font-size: 14px;
  color: var(--text-sub);
  margin: 0;
  letter-spacing: 2px;
}

.forgot-box :deep(.el-input__wrapper) {
  border-radius: 10px;
  padding: 4px 16px;
}

.forgot-box :deep(.el-button) {
  border-radius: 10px;
  font-weight: 600;
  letter-spacing: 2px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.link-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
}

.link-row a {
  color: var(--text-sub);
  font-size: 14px;
  text-decoration: none;
  transition: color 0.3s ease;
}

.link-row a:hover {
  color: #667eea;
}
</style>
