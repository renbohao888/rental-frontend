import request from '@/utils/request'

// 🔥 创建订单（需要登录）
export function createOrder(data) {
  return request({
    url: '/order/create',
    method: 'post',
    data
  })
}

// 查询我的订单（需要登录）
export function getMyOrders() {
  return request({
    url: '/order/my',
    method: 'get'
  })
}