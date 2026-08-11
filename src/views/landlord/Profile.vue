<template>
  <div class="profile-page">
    <el-card class="profile-card">
      <h2>👤 个人资料</h2>
      <p class="sub-tip">维护你的账号基础信息，昵称与头像将展示在平台各页面</p>

      <!-- 头像上传 -->
      <div class="avatar-section">
        <div class="avatar-container">
          <img :src="userInfo?.avatar || 'https://ui-avatars.com/api/?name=Landlord'" class="avatar" />
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
      <el-form :model="form" label-width="110px" style="max-width: 500px;" v-loading="loading">
        <el-form-item label="账号">
          <el-input :value="userInfo?.accountNo || '-'" disabled />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="form.nickname" placeholder="请输入昵称" maxlength="20" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input :value="userInfo?.phone || '-'" disabled />
        </el-form-item>
        <el-form-item label="身份角色">
          <el-tag type="primary">{{ roleText(userInfo?.role) }}</el-tag>
        </el-form-item>
        <el-form-item label="注册时间">
          <span class="plain-text">{{ formatTime(userInfo?.createTime) }}</span>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSave" :loading="saving">保存修改</el-button>
          <el-button @click="initForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getUserInfo, updateUserInfo } from '@/api/user'

const loading = ref(false)
const saving = ref(false)
const userInfo = ref(null)
const avatarUploadRef = ref(null)
const token = localStorage.getItem('token') || ''

const form = reactive({
  nickname: ''
})

const formatTime = (t) => {
  if (!t) return '-'
  const d = new Date(t)
  return isNaN(d.getTime()) ? '-' : d.toLocaleString()
}

const roleText = (role) => (role === 0 ? '管理员' : role === 1 ? '房东' : '租客')

const initForm = () => {
  form.nickname = userInfo.value?.nickname || ''
}

const loadUserInfo = async () => {
  loading.value = true
  try {
    const res = await getUserInfo()
    if (res.code === 200) {
      userInfo.value = res.data
      initForm()
    } else {
      ElMessage.error(res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载用户信息失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
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
    const avatarUrl = res.data?.avatarUrl || res.data
    userInfo.value.avatar = avatarUrl
    localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
    ElMessage.success('头像上传成功')
  } else {
    ElMessage.error(res.message || '上传失败')
  }
}

// 保存修改
const handleSave = async () => {
  saving.value = true
  try {
    const res = await updateUserInfo({ nickname: form.nickname })
    if (res.code === 200) {
      ElMessage.success('修改成功')
      userInfo.value.nickname = form.nickname
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

onMounted(loadUserInfo)
</script>

<style scoped>
.profile-card {
  max-width: 700px;
}

.profile-card h2 {
  margin: 0 0 4px;
}

.sub-tip {
  color: #999;
  font-size: 13px;
  margin: 0 0 24px;
}

.avatar-section {
  margin-bottom: 32px;
  text-align: center;
}

.avatar-container {
  position: relative;
  width: 96px;
  height: 96px;
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

.plain-text {
  color: #333;
}

@media (max-width: 768px) {
  .profile-page {
    padding: 12px;
  }
}
</style>
