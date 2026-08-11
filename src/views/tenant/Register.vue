<template>
  <div class="register-container">
    <div class="register-bg">
      <div class="register-box" v-reveal>
        <!-- Logo -->
        <div class="logo-area">
          <div class="logo-icon">🏠</div>
          <h1>安居房屋租赁</h1>
          <p>安全 · 便捷 · 值得信赖</p>
        </div>

        <!-- 选择角色 -->
        <div class="role-selector">
          <p class="role-label">选择账户类型</p>
          <div class="role-buttons">
            <el-button
              :type="form.role === 2 ? 'primary' : 'default'"
              @click="form.role = 2"
              class="role-btn"
            >
              🏠 租客
            </el-button>
            <el-button
              :type="form.role === 1 ? 'primary' : 'default'"
              @click="form.role = 1"
              class="role-btn"
            >
              🏘️ 房东
            </el-button>
          </div>
        </div>

        <!-- 注册表单 -->
        <el-form
          :model="form"
          :rules="rules"
          ref="formRef"
          @keyup.enter="handleRegister"
        >
          <!-- 头像 -->
          <el-form-item prop="avatar">
            <div class="avatar-uploader">
              <div class="avatar-circle" @click="triggerUpload">
                <img v-if="form.avatar" :src="form.avatar" class="avatar-img" alt="头像预览" />
                <span v-else class="avatar-placeholder">📷</span>
              </div>
              <div class="avatar-meta">
                <p class="avatar-label">上传头像（可选）</p>
                <p class="avatar-tip">点击选择图片，无格式与大小限制</p>
              </div>
              <input ref="avatarInputRef" type="file" class="avatar-input" @change="handleAvatarChange" />
            </div>
          </el-form-item>

          <!-- 手机号 -->
          <el-form-item prop="phone">
            <el-input
              v-model="form.phone"
              placeholder="手机号"
              prefix-icon="Phone"
              maxlength="11"
              size="large"
              clearable
            />
          </el-form-item>

          <!-- 密码 -->
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="密码 (至少6位)"
              prefix-icon="Lock"
              show-password
              maxlength="20"
              size="large"
            />
          </el-form-item>

          <!-- 确认密码 -->
          <el-form-item prop="confirmPassword">
            <el-input
              v-model="form.confirmPassword"
              type="password"
              placeholder="确认密码"
              prefix-icon="Lock"
              show-password
              maxlength="20"
              size="large"
            />
          </el-form-item>

          <!-- 昵称 -->
          <el-form-item prop="nickname">
            <el-input
              v-model="form.nickname"
              placeholder="昵称"
              prefix-icon="User"
              maxlength="20"
              size="large"
              clearable
            />
          </el-form-item>

          <!-- 同意条款 -->
          <el-form-item prop="agreement">
            <el-checkbox v-model="form.agreement">
              我已阅读并同意《用户服务协议》和《隐私政策》
            </el-checkbox>
          </el-form-item>

          <!-- 注册按钮 -->
          <el-button
            type="primary"
            size="large"
            style="width:100%"
            @click="handleRegister"
            :loading="loading"
          >
            立即注册
          </el-button>

          <!-- 登录链接 -->
          <div class="login-link">
            已有账号？<router-link to="/login">立即登录</router-link>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { register } from '@/api/user'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const avatarInputRef = ref(null)

const form = reactive({
  phone: '',
  avatar: '',
  password: '',
  confirmPassword: '',
  nickname: '',
  role: 2, // 默认租客
  agreement: false
})

const validatePhone = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入手机号'))
  } else if (!/^1[3-9]\d{9}$/.test(value)) {
    callback(new Error('请输入有效的手机号'))
  } else {
    callback()
  }
}

const validatePassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入密码'))
  } else if (value.length < 6 || value.length > 20) {
    callback(new Error('密码长度6-20位'))
  } else {
    callback()
  }
}

const validateConfirmPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请确认密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const validateNickname = (rule, value, callback) => {
  if (!value || !value.trim()) {
    callback(new Error('请输入昵称'))
  } else if (value.length > 20) {
    callback(new Error('昵称长度不能超过20字符'))
  } else {
    callback()
  }
}

const validateAgreement = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请同意用户协议'))
  } else {
    callback()
  }
}

const rules = {
  phone: [{ validator: validatePhone, trigger: 'change' }],
  password: [{ validator: validatePassword, trigger: 'change' }],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'change' }],
  nickname: [{ validator: validateNickname, trigger: 'change' }],
  agreement: [{ validator: validateAgreement, trigger: 'change' }]
}

// 选择头像文件（读为 base64，用于预览与提交）
const triggerUpload = () => {
  avatarInputRef.value?.click()
}

const handleAvatarChange = (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  // 不限制大小与格式，仅对明显非图片文件做提示
  if (file.type && !file.type.startsWith('image/')) {
    ElMessage.warning('请选择图片文件')
    e.target.value = ''
    return
  }
  const reader = new FileReader()
  reader.onload = (ev) => {
    form.avatar = ev.target.result
  }
  reader.readAsDataURL(file)
  e.target.value = ''
}

// 注册处理
const handleRegister = async () => {
  try {
    await formRef.value?.validate()

    loading.value = true
    const res = await register({
      phone: form.phone,
      avatar: form.avatar || null,
      password: form.password,
      nickname: form.nickname,
      role: form.role
    })

    if (res.code === 200 || res.code === 0) {
      const accountNo = res.data?.accountNo
      if (accountNo) {
        ElMessageBox.alert(
          `恭喜注册成功！\n您的登录账号为：${accountNo}\n请牢记该账号，使用「账号 + 密码」登录。`,
          '注册成功',
          {
            confirmButtonText: '去登录',
            type: 'success',
            callback: () => {
              router.push('/login')
            }
          }
        )
      } else {
        ElMessage.success('注册成功，请登录')
        setTimeout(() => {
          router.push('/login')
        }, 1500)
      }
    } else {
      ElMessage.error(res.message || '注册失败')
    }
  } catch (error) {
    if (error.message && error.message !== '请同意用户协议') {
      console.error('注册失败', error)
    }
  } finally {
    loading.value = false
  }
}
</script>
<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-bg {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.register-box {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 40px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.logo-area {
  text-align: center;
  margin-bottom: 32px;
}

.logo-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.logo-area h1 {
  margin: 0 0 8px;
  font-size: 24px;
  color: var(--text-main);
  font-weight: 600;
}

.logo-area p {
  margin: 0;
  font-size: 14px;
  color: var(--text-sub);
}

.role-selector {
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
}

.role-label {
  margin: 0 0 12px;
  font-size: 14px;
  color: var(--text-sub);
  font-weight: 500;
}

.role-buttons {
  display: flex;
  gap: 12px;
}

.role-btn {
  flex: 1;
}

.el-form {
  margin-top: 16px;
}

:deep(.el-form-item) {
  margin-bottom: 16px;
}

.login-link {
  text-align: center;
  margin-top: 16px;
  font-size: 14px;
  color: var(--text-sub);
}

.login-link a {
  color: #409eff;
  text-decoration: none;
}

.login-link a:hover {
  color: #66b1ff;
  text-decoration: underline;
}

@media (max-width: 768px) {
  .register-box {
    padding: 24px;
    max-width: 100%;
  }
  .register-bg { padding: 12px; }
  .logo-area h1 { font-size: 20px; }
  .logo-icon { font-size: 40px; }
  .role-buttons { flex-direction: column; }
}
.avatar-uploader {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar-circle {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  border: 2px dashed #c0c4cc;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  overflow: hidden;
  flex-shrink: 0;
  background: var(--bg-soft);
  transition: all 0.3s ease;
}

.avatar-circle:hover {
  border-color: #409eff;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  font-size: 28px;
  color: #c0c4cc;
}

.avatar-label {
  margin: 0 0 4px;
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.avatar-tip {
  margin: 0;
  font-size: 12px;
  color: #999;
}

.avatar-input {
  display: none;
}
</style>