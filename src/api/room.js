import request from '@/utils/request'

// 分页查询房源列表（公开）
export function getRoomList(params) {
  return request({
    url: '/room/list',
    method: 'get',
    params
  })
}

// 🔥 新增：房源详情（公开）
export function getRoomDetail(id) {
  return request({
    url: `/room/detail/${id}`,
    method: 'get'
  })
}

// 热门推荐（公开）
export function getHotRooms(limit = 10) {
  return request({
    url: '/room/recommend/hot',
    method: 'get',
    params: { limit }
  })
}

// 房态日历（公开）：month 格式 yyyy-MM，缺省为当前月
export function getRoomCalendar(roomId, month) {
  return request({
    url: `/room/calendar/${roomId}`,
    method: 'get',
    params: { month: month || undefined }
  })
}

// 房东：查询自己的房源列表
export function getMyRooms() {
  return request({
    url: '/room/my',
    method: 'get'
  })
}

// 房东/管理员：发布房源（初始状态为待审核）
export function addRoom(data) {
  return request({
    url: '/room/add',
    method: 'post',
    data
  })
}

// 房东：编辑房源
export function updateRoom(data) {
  return request({
    url: '/room/update',
    method: 'put',
    data
  })
}

// 房东：上架/下架/重新提交审核（status: 1-上架, 3-下架, 0-重新提交审核）
export function changeRoomStatus(roomId, status) {
  return request({
    url: `/room/status/${roomId}`,
    method: 'post',
    params: { status }
  })
}

// 管理员：房源审核（status: 1-审核通过上架, 3-强制下架, 4-审核驳回；remark: 驳回理由，驳回时必填）
export function auditRoom(roomId, status, remark) {
  return request({
    url: `/room/audit/${roomId}`,
    method: 'post',
    params: { status, remark: remark || '' }
  })
}

// 房东/管理员：删除房源（软删除，仅本人房源或管理员可操作；存在进行中订单时会被拒绝）
export function deleteRoom(roomId) {
  return request({
    url: `/room/delete/${roomId}`,
    method: 'delete'
  })
}