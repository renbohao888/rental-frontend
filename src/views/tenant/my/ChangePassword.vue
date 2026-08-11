<template>
  <div class="change-password-page">
    <el-card class="password-card">
      <h2>🔐 修改密码</h2>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        style="max-width: 500px;"
      >
        <el-form-item label="当前密码" prop="oldPassword">
          <el-input
            v-model="form.oldPassword"
            type="password"
            show-password
            placeholder="请输入当前密码"
          />
        </el-form-item>

        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="form.newPassword"
            type="password"
            show-password
            placeholder="请输入新密码（8-20位）"
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            show-password
            placeholder="请再次输入新密码"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">
            确认修改
          </el-button>
          <el-button @click="resetForm">取消</el-button>
        </el-form-item>
      </el-form>

      <div class="password-tips">
        <h4>密码安全提示：</h4>
        <ul>
          <li>密码长度：8-20个字符</li>
          <li>建议包含大小写字母、数字和特殊符号</li>
          <li>避免使用生日、手机号等易猜的信息</li>
          <li>定期修改密码可以提高账户安全性</li>
        </ul>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 验证新密码和确认密码是否相同
const validatePasswordSame = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

// 验证密码格式
const validatePasswordFormat = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入新密码'))
  } else if (value.length < 8 || value.length > 20) {
    callback(new Error('密码长度必须为8-20个字符'))
  } else {
    callback()
  }
}

const rules = {
  oldPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { validator: validatePasswordFormat, trigger: 'blur' }
  ],
  confirmPassword: [
    { validator: validatePasswordSame, trigger: 'blur' }
  ]
}

// 提交修改
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  loading.value = true
  try {
    const res = await request({
      url: '/user/changePassword',
      method: 'post',
      data: {
        oldPassword: form.oldPassword,
        newPassword: form.newPassword
      }
    })

    if (res.code === 200) {
      ElMessage.success('密码修改成功，请重新登录')
      // 清除登录信息，跳转到登录页
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      setTimeout(() => {
        window.location.href = '/login'
      }, 1500)
    } else {
      ElMessage.error(res.message || '修改失败')
    }
  } catch (error) {
    console.error('修改密码失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
}

// 重置表单
const resetForm = () => {
  form.oldPassword = ''
  form.newPassword = ''
  form.confirmPassword = ''
  formRef.value?.clearValidate()
}
</script>

<style scoped>
.change-password-page {
  background: var(--bg-card);
  padding: 20px;
}

.password-card {
  max-width: 600px;
}

.password-card h2 {
  margin-bottom: 24px;
}

.password-tips {
  margin-top: 32px;
  padding: 16px;
  background-color: #f0f9ff;
  border-radius: 8px;
  border-left: 3px solid #409eff;
}

.password-tips h4 {
  margin: 0 0 12px 0;
  color: #409eff;
}

.password-tips ul {
  margin: 0;
  padding-left: 20px;
  color: #666;
  font-size: 13px;
  line-height: 1.8;
}

.password-tips li {
  margin-bottom: 6px;
}

@media (max-width: 768px) {
  .change-password-page {
    padding: 12px;
  }

  .password-card {
    max-width: 100%;
  }
}
</style>
