import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// API 基础地址：优先读取 .env 的 VITE_API_BASE_URL（部署公网时配置），本地默认 localhost:8080
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api'

const request = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

// 防抖标识
let isRedirecting = false

// 请求拦截器：自动添加 Token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：统一处理错误
request.interceptors.response.use(
  (response) => {
    const res = response.data

    // 1. 业务成功：兼容数字或字符串 200 / 0，或直接返回对象的情况
    if (res.code == 200 || res.code == 0 || res.code === undefined) {
      return res
    }

    // 2. Token 失效或未授权 (401 / 403)
    if (res.code == 401 || res.code == 403) {
      const currentPath = router.currentRoute.value?.path || window.location.pathname

      if (currentPath !== '/login') {
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')

        if (!isRedirecting) {
          isRedirecting = true
          ElMessage.error(res.message || '登录已过期，请重新登录')

          router.push('/login').finally(() => {
            setTimeout(() => { isRedirecting = false }, 1000)
          })
        }
      } else {
        // 登录页收到 401：账号/密码错误、未注册等，直接提示后端返回的错误消息
        ElMessage.error(res.message || '登录失败')
      }
      return Promise.reject(res)
    }

    // 3. 其他业务错误
    ElMessage.error(res.message || '系统业务异常')
    return Promise.reject(res)
  },
  (error) => {
    const status = error.response?.status
    const errMsg = error.response?.data?.message || error.message || '网络请求失败'
    const currentPath = router.currentRoute.value?.path || window.location.pathname

    if ((status === 401 || status === 403) && currentPath !== '/login') {
      // 非登录页收到 401/403：登录态失效，清理并跳转登录
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')

      if (!isRedirecting) {
        isRedirecting = true
        ElMessage.error(errMsg || '登录状态失效，请重新登录')
        router.push('/login').finally(() => {
          setTimeout(() => { isRedirecting = false }, 1000)
        })
      }
    } else {
      // 登录页 401（账号或密码错误）等：直接展示后端返回的错误消息
      ElMessage.error(errMsg)
    }
    return Promise.reject(error)
  }
)

export default request