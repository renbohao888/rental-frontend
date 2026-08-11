<template>
  <div class="profile-page">
    <el-card class="profile-card">
      <h2>👤 个人中心</h2>
      
      <!-- 头像 -->
      <div class="avatar-section">
        <el-upload
  class="avatar-uploader"
  action="/api/user/uploadAvatar"
  :headers="{ Authorization: 'Bearer ' + token }"
  :show-file-list="false"
  :on-success="handleAvatarSuccess"
  :before-upload="beforeAvatarUpload"
>
          <img v-if="userInfo?.avatar" :src="userInfo.avatar" class="avatar" />
          <el-icon v-else class="avatar-placeholder"><UserFilled /></el-icon>
        </el-upload>
        <div class="avatar-tip">点击头像上传</div>
      </div>

      <!-- 表单 -->
      <el-form :model="form" label-width="100px" style="max-width:500px;">
        <el-form-item label="账号">
          <el-input :value="userInfo?.accountNo" disabled />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="form.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input :value="userInfo?.phone" disabled />
        </el-form-item>
        <el-form-item label="角色">
          <el-tag :type="roleTagType(userInfo?.role)">
            {{ roleMap[userInfo?.role] || '未知' }}
          </el-tag>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveProfile">保存修改</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UserFilled } from '@element-plus/icons-vue'
import { getUserInfo, updateUserInfo } from '@/api/user'

const token = localStorage.getItem('token') || ''
const userInfo = ref(null)

const roleMap = { 0: '管理员', 1: '房东', 2: '租客' }
const roleTagType = (role) => {
  const map = { 0: 'danger', 1: 'warning', 2: 'success' }
  return map[role] || 'info'
}

const form = reactive({
  nickname: ''
})

onMounted(async () => {
  try {
    const res = await getUserInfo()
    if (res.code === 200) {
      userInfo.value = res.data
      form.nickname = res.data.nickname || ''
      localStorage.setItem('userInfo', JSON.stringify(res.data))
    }
  } catch (error) {
    console.error('获取用户信息失败', error)
  }
})

const handleAvatarSuccess = (res) => {
  if (res.code === 200) {
    // 更新页面显示的 userInfo
    userInfo.value.avatar = res.data
    // 更新 localStorage 缓存
    localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
    ElMessage.success('头像上传成功')
  } else {
    ElMessage.error(res.message || '上传失败')
  }
}

const beforeAvatarUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isImage) {
    ElMessage.error('只能上传图片')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过2MB')
    return false
  }
  return true
}

const saveProfile = async () => {
  try {
    const res = await updateUserInfo({ nickname: form.nickname })
    if (res.code === 200) {
      ElMessage.success('资料更新成功')
      // 刷新用户信息
      const userRes = await getUserInfo()
      if (userRes.code === 200) {
        userInfo.value = userRes.data
        localStorage.setItem('userInfo', JSON.stringify(userRes.data))
      }
    } else {
      ElMessage.error(res.message)
    }
  } catch (error) {
    console.error('更新失败', error)
  }
}
</script>

<style scoped>
.profile-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
.profile-card {
  padding: 30px;
}
.profile-card h2 {
  text-align: center;
  margin-bottom: 30px;
}
.avatar-section {
  text-align: center;
  margin-bottom: 30px;
}
.avatar-uploader {
  display: inline-block;
}
.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  cursor: pointer;
  border: 3px solid #409eff;
}
.avatar-placeholder {
  font-size: 80px;
  color: #ccc;
  cursor: pointer;
}
.avatar-tip {
  margin-top: 8px;
  color: #999;
  font-size: 13px;
}
</style>