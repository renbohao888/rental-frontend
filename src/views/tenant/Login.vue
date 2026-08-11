<template>
  <div class="login-container">
    <div class="login-bg">
      <div class="login-box" v-reveal>
        <!-- Logo -->
        <div class="logo-area">
          <div class="logo-icon">🏠</div>
          <h1>安居房屋租赁</h1>
          <p>安全 · 便捷 · 值得信赖</p>
        </div>

        <el-tabs v-model="activeTab" class="login-tabs">
          <!-- 账号密码登录 -->
          <el-tab-pane label="账号登录" name="password">
            <el-form :model="form" :rules="rules" ref="formRef" @keyup.enter="handleLogin">
              <el-form-item prop="accountNo">
                <el-input 
                  v-model="form.accountNo" 
                  placeholder="请输入账号" 
                  prefix-icon="User" 
                  size="large"
                />
              </el-form-item>
              <el-form-item prop="password">
                <el-input 
                  v-model="form.password" 
                  type="password" 
                  placeholder="请输入密码" 
                  prefix-icon="Lock" 
                  show-password
                  size="large"
                />
              </el-form-item>
              <el-button type="primary" size="large" style="width:100%" @click="handleLogin" :loading="loading">
                登 录
              </el-button>
              <div class="link-row">
                <router-link to="/register">还没有账号？立即注册</router-link>
                <router-link to="/forgot-password" class="forgot-link">忘记密码？</router-link>
              </div>
            </el-form>
          </el-tab-pane>

          <!-- 手机号密码登录 -->
          <el-tab-pane label="手机号登录" name="phone">
            <el-form :model="phoneForm" :rules="phoneRules" ref="phoneFormRef" @keyup.enter="handlePhoneLogin">
              <el-form-item prop="phone">
                <el-input 
                  v-model="phoneForm.phone" 
                  placeholder="请输入手机号" 
                  prefix-icon="Phone" 
                  maxlength="11"
                  size="large"
                />
              </el-form-item>
              <el-form-item prop="password">
                <el-input 
                  v-model="phoneForm.password" 
                  type="password" 
                  placeholder="请输入密码" 
                  prefix-icon="Lock" 
                  show-password
                  size="large"
                />
              </el-form-item>
              <el-button type="primary" size="large" style="width:100%" @click="handlePhoneLogin" :loading="loading">
                登 录
              </el-button>
              <div class="link-row">
                <router-link to="/register">还没有账号？立即注册</router-link>
                <router-link to="/forgot-password" class="forgot-link">忘记密码？</router-link>
              </div>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login, loginByPhone, getUserInfo } from '@/api/user'

const router = useRouter()
const formRef = ref()
const phoneFormRef = ref()
const loading = ref(false)
const activeTab = ref('password')

const form = reactive({
  accountNo: '',
  password: ''
})

const rules = {
  accountNo: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const phoneForm = reactive({
  phone: '',
  password: ''
})

const phoneRules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

// 登录成功后的统一处理：保存 Token 并跳转对应角色页面
const handleLoginSuccess = async (token) => {
  let actualToken = token
  if (typeof actualToken === 'string' && actualToken.startsWith('Bearer ')) {
    actualToken = actualToken.replace('Bearer ', '')
  }

  localStorage.setItem('token', actualToken)

  try {
    const userRes = await getUserInfo()
    if (userRes.code === 200) {
      const userInfo = userRes.data
      localStorage.setItem('userInfo', JSON.stringify(userInfo))

      ElMessage.success('登录成功')

      if (userInfo.role === 0) {
        router.push('/admin/dashboard')
      } else if (userInfo.role === 1) {
        router.push('/landlord/dashboard')
      } else {
        router.push('/')
      }
    } else {
      ElMessage.success('登录成功')
      router.push('/')
    }
  } catch (error) {
    ElMessage.success('登录成功')
    router.push('/')
  }
}

const handleLogin = async () => {
  if (!formRef.value) return
  await formRef.value.validate()

  loading.value = true
  try {
    const res = await login(form)
    if (res.code === 200 || res.code === 0) {
      await handleLoginSuccess(res.data?.token || res.data)
    } else {
      ElMessage.error(res.message || '登录失败')
    }
  } catch (error) {
    console.error('登录异常', error)
  } finally {
    loading.value = false
  }
}

const handlePhoneLogin = async () => {
  if (!phoneFormRef.value) return
  await phoneFormRef.value.validate()

  loading.value = true
  try {
    const res = await loginByPhone({
      phone: phoneForm.phone,
      password: phoneForm.password
    })
    if (res.code === 200 || res.code === 0) {
      await handleLoginSuccess(res.data?.token || res.data)
    } else {
      ElMessage.error(res.message || '登录失败')
    }
  } catch (error) {
    console.error('手机号登录异常', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  position: relative;
  overflow: hidden;
}

/* 背景装饰圆 */
.login-container::before {
  content: '';
  position: absolute;
  width: 600px;
  height: 600px;
  border-radius: 50%;
  background: rgba(255,255,255,0.08);
  top: -200px;
  right: -200px;
}
.login-container::after {
  content: '';
  position: absolute;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  background: rgba(255,255,255,0.06);
  bottom: -150px;
  left: -150px;
}

.login-bg {
  width: 100%;
  max-width: 420px;
  padding: 20px;
  position: relative;
  z-index: 1;
}

.login-box {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  padding: 48px 40px 40px;
  border-radius: 20px;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.login-box:hover {
  transform: translateY(-2px);
  box-shadow: 0 30px 70px rgba(0, 0, 0, 0.25);
}

/* 与滚动入场动画的过渡合并，避免 transition 冲突 */
.login-box.reveal-init,
.login-box.reveal-init.reveal-in {
  transition: opacity 0.7s cubic-bezier(0.22, 0.61, 0.36, 1),
    transform 0.7s cubic-bezier(0.22, 0.61, 0.36, 1),
    box-shadow 0.3s ease;
}

.logo-area {
  text-align: center;
  margin-bottom: 32px;
}

.logo-icon {
  font-size: 48px;
  margin-bottom: 8px;
}

.logo-area h1 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-main);
  margin: 0 0 4px 0;
  letter-spacing: 2px;
}

.logo-area p {
  font-size: 14px;
  color: var(--text-sub);
  margin: 0;
  letter-spacing: 4px;
}

.login-box :deep(.el-input__wrapper) {
  border-radius: 10px;
  padding: 4px 16px;
  transition: all 0.3s ease;
}

.login-box :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.login-box :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3);
}

.login-box :deep(.el-button) {
  border-radius: 10px;
  font-weight: 600;
  letter-spacing: 2px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
}

.login-box :deep(.el-button:hover) {
  transform: translateY(-1px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
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

.login-tabs :deep(.el-tabs__item) {
  font-size: 15px;
}

.login-tabs :deep(.el-tabs__active-bar) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-tabs :deep(.el-tabs__item.is-active) {
  color: #667eea;
}

/* 手机端适配 */
@media (max-width: 768px) {
  .login-bg { max-width: 100%; padding: 12px; }
  .login-box { padding: 32px 20px 24px; }
  .logo-area { margin-bottom: 20px; }
  .logo-area h1 { font-size: 20px; }
  .logo-icon { font-size: 36px; }
  .link-row { flex-direction: column; gap: 8px; text-align: center; }
}
</style>