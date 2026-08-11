import request from '@/utils/request'

// 获取轮播图列表（公开）
export function getBannerList() {
  return request({
    url: '/banner/list',
    method: 'get'
  })
}