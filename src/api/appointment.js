import request from '@/utils/request'

// 租客提交看房预约
export function submitAppointment(data) {
  return request({
    url: '/appointment/submit',
    method: 'post',
    data
  })
}

// 租客查询自己的预约列表
export function getMyAppointments(params) {
  return request({
    url: '/appointment/my',
    method: 'get',
    params
  })
}

// 租客取消预约（仅待确认状态）
export function cancelAppointment(id) {
  return request({
    url: `/appointment/cancel/${id}`,
    method: 'post'
  })
}

// 租客标记已看房（已确认的预约）
export function markAsViewed(id) {
  return request({
    url: `/appointment/view/${id}`,
    method: 'post'
  })
}
