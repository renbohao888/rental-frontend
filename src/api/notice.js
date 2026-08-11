import request from '@/utils/request'

// 公告列表（公开）
export function getNoticeList(params) {
  return request({
    url: '/notice/list',
    method: 'get',
    params
  })
}

// ===== 管理员公告管理 =====

// 管理员分页查询公告（可筛选状态/标题）
export function getAdminNoticeList(params) {
  return request({
    url: '/notice/admin/list',
    method: 'get',
    params
  })
}

// 新增公告
export function addNotice(data) {
  return request({
    url: '/notice/add',
    method: 'post',
    data
  })
}

// 更新公告
export function updateNotice(data) {
  return request({
    url: '/notice/update',
    method: 'put',
    data
  })
}

// 删除公告
export function deleteNotice(noticeId) {
  return request({
    url: `/notice/admin/delete/${noticeId}`,
    method: 'delete'
  })
}