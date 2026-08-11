import request from '@/utils/request'

// 登录
export function login(data) {
  return request({
    url: '/user/login',
    method: 'post',
    data
  })
}

// 注册
export function register(data) {
  return request({
    url: '/user/register',
    method: 'post',
    data
  })
}

// 获取用户信息
export function getUserInfo() {
  return request({
    url: '/user/info',
    method: 'get'
  })
}

// 更新用户信息
export function updateUserInfo(data) {
  return request({
    url: '/user/update',
    method: 'put',
    data
  })
}

// 上传头像（使用 FormData）
export function uploadAvatar(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/user/uploadAvatar',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 发送短信验证码
export function sendSmsCode(phone) {
  return request({
    url: '/user/sendSms',
    method: 'post',
    params: { phone }
  })
}

// 手机号 + 密码登录
export function loginByPhone(data) {
  return request({
    url: '/user/loginByPhone',
    method: 'post',
    data
  })
}

// 找回密码（短信验证码重置密码）
export function resetPassword(data) {
  return request({
    url: '/user/resetPassword',
    method: 'post',
    data
  })
}

// 公开用户信息（房源详情页展示房东等）
export function getUserDetail(userId) {
  return request({
    url: `/user/detail/${userId}`,
    method: 'get'
  })
}