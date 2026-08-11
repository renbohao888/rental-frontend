<template>
  <div class="profile-page">
    <el-card class="profile-card">
      <h2>👤 个人资料</h2>

      <!-- 头像上传 -->
      <div class="avatar-section">
        <div class="avatar-container">
          <img :src="userInfo?.avatar || 'https://ui-avatars.com/api/?name=User'" class="avatar" />
          <el-button 
            type="primary" 
            text 
            @click="avatarUploadRef?.$el.querySelector('input').click()"
            style="position: absolute; bottom: 0; right: 0;"
          >
            📷 更换
          </el-button>
        </div>
        <el-upload
          ref="avatarUploadRef"
          action="/api/user/uploadAvatar"
          :headers="{ Authorization: token }"
          :show-file-list="false"
          :on-success="handleAvatarSuccess"
          :before-upload="beforeAvatarUpload"
          style="display: none"
        />
        <div class="avatar-tip">点击更换头像</div>
      </div>

      <!-- 个人信息表单 -->
      <el-form 
        ref="formRef"
        :model="form" 
        label-width="100px" 
        style="max-width: 500px;"
      >
        <el-form-item label="账号">
          <el-input :value="userInfo?.accountNo" disabled />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="form.nickname" placeholder="请输入昵称" maxlength="20" />
        </el-form-item>
        <el-form-item label="手机号">
          <div class="phone-row">
            <el-input v-model="form.phone" placeholder="请输入手机号" maxlength="11" :disabled="phoneLocked" />
            <el-button 
              v-if="!phoneLocked"
              size="small" 
              type="primary" 
              :disabled="phoneCountdown > 0"
              @click="sendBindCode"
              style="margin-left: 8px; white-space: nowrap;"
            >
              {{ phoneCountdown > 0 ? `${phoneCountdown}s后重发` : '获取验证码' }}
            </el-button>
            <el-button v-if="phoneLocked" size="small" type="warning" @click="phoneLocked = false" style="margin-left: 8px;">修改</el-button>
          </div>
        </el-form-item>
        <el-form-item v-if="!phoneLocked && form.phone !== userInfo?.phone" label="验证码" prop="phoneCode">
          <el-input v-model="form.phoneCode" placeholder="请输入短信验证码" maxlength="6" style="width: 200px;" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" type="email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="form.gender">
            <el-radio value="M">男</el-radio>
            <el-radio value="F">女</el-radio>
            <el-radio value="">保密</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="身份证号">
          <el-input v-model="form.idCard" placeholder="用于身份验证" maxlength="18" />
        </el-form-item>
        <el-form-item label="认证状态">
          <el-tag :type="userInfo?.isVerified ? 'success' : 'warning'">
            {{ userInfo?.isVerified ? '已认证' : '未认证' }}
          </el-tag>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSave" :loading="saving">保存修改</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { getUserInfo, updateUserInfo, sendSmsCode } from '@/api/user'
import request from '@/utils/request'

const token = localStorage.getItem('token') || ''
const userInfo = ref(null)
const saving = ref(false)
const avatarUploadRef = ref(null)
const phoneLocked = ref(true)
const phoneCountdown = ref(0)
let countdownTimer = null

const form = reactive({
  nickname: '',
  email: '',
  gender: '',
  idCard: '',
  phone: '',
  phoneCode: ''
})

// 初始化表单
const initForm = () => {
  if (userInfo.value) {
    form.nickname = userInfo.value.nickname || ''
    form.email = userInfo.value.email || ''
    form.gender = userInfo.value.gender || ''
    form.idCard = userInfo.value.idCard || ''
    form.phone = userInfo.value.phone || ''
    form.phoneCode = ''
    phoneLocked.value = !!userInfo.value.phone
  }
}

// 加载用户信息
const loadUserInfo = async () => {
  try {
    const res = await getUserInfo()
    if (res.code === 200) {
      userInfo.value = res.data
      initForm()
    } else {
      ElMessage.error('加载用户信息失败')
    }
  } catch (error) {
    console.error('加载用户信息失败', error)
    ElMessage.error('网络请求失败')
  }
}

// 发送绑定手机号验证码
const sendBindCode = async () => {
  if (!form.phone || !/^1[3-9]\d{9}$/.test(form.phone)) {
    ElMessage.warning('请输入有效的手机号')
    return
  }
  try {
    const res = await sendSmsCode(form.phone)
    if (res.code === 200 || res.code === 0) {
      ElMessage.success('验证码已发送，请查看控制台（测试模式）')
      phoneCountdown.value = 60
      countdownTimer = setInterval(() => {
        phoneCountdown.value--
        if (phoneCountdown.value <= 0) {
          clearInterval(countdownTimer)
          countdownTimer = null
        }
      }, 1000)
    } else {
      ElMessage.error(res.message || '验证码发送失败')
    }
  } catch (error) {
    console.error('发送验证码异常', error)
    ElMessage.error('验证码发送失败，请检查后端控制台')
  }
}

// 头像上传前校验
const beforeAvatarUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt10M = file.size / 1024 / 1024 < 10
  
  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('图片大小不能超过10MB')
    return false
  }
  return true
}

// 头像上传成功
const handleAvatarSuccess = (res) => {
  if (res.code === 200) {
    userInfo.value.avatar = res.data.avatarUrl || res.data
    localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
    ElMessage.success('头像上传成功')
  } else {
    ElMessage.error(res.message || '上传失败')
  }
}

// 保存修改
const handleSave = async () => {
  // 如果手机号有变化，需要验证码
  if (!phoneLocked.value && form.phone !== userInfo.value?.phone) {
    if (!form.phoneCode || form.phoneCode.trim() === '') {
      ElMessage.warning('请输入手机验证码')
      return
    }
  }

  saving.value = true
  try {
    const updateData = {
      nickname: form.nickname,
      email: form.email,
      gender: form.gender,
      idCard: form.idCard,
      phone: form.phone
    }
    // 如果手机号变了，带上验证码
    if (!phoneLocked.value && form.phone !== userInfo.value?.phone) {
      updateData.phoneCode = form.phoneCode
    }

    const res = await updateUserInfo(updateData)

    if (res.code === 200) {
      ElMessage.success('修改成功')
      phoneLocked.value = true
      // 更新本地缓存
      Object.assign(userInfo.value, form)
      localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
    } else {
      ElMessage.error(res.message || '修改失败')
    }
  } catch (error) {
    console.error('修改失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    saving.value = false
  }
}

// 重置表单
const resetForm = () => {
  initForm()
}

onMounted(() => {
  loadUserInfo()
})

onBeforeUnmount(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
})
</script>

<style scoped>
.profile-page {
  background: var(--bg-card);
  padding: 20px;
}

.profile-card {
  max-width: 600px;
}

.profile-card h2 {
  margin-bottom: 24px;
}

.avatar-section {
  margin-bottom: 32px;
  text-align: center;
}

.avatar-container {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto 12px;
}

.avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #409eff;
}

.avatar-tip {
  font-size: 12px;
  color: #999;
}

.phone-row {
  display: flex;
  align-items: center;
  width: 100%;
}

@media (max-width: 768px) {
  .profile-page {
    padding: 12px;
  }
}
</style>
