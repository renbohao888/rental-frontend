import request from '@/utils/request'

/** 获取系统消息列表 */
export function getMessages(params) {
  return request({
    url: '/message/list',
    method: 'get',
    params
  })
}

/** 分享房源给租客 */
export function shareRoom(data) {
  return request({
    url: '/message/share',
    method: 'post',
    data
  })
}

/** 删除消息 */
export function deleteMessage(messageId) {
  return request({
    url: `/message/${messageId}`,
    method: 'delete'
  })
}
