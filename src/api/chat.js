import request from '@/utils/request'

// ==================== 好友 ====================

// 按系统账号搜索用户
export function searchUser(account) {
  return request({
    url: '/friend/search',
    method: 'get',
    params: { account }
  })
}

// 发送好友申请
export function sendFriendRequest(friendId) {
  return request({
    url: '/friend/request',
    method: 'post',
    params: { friendId }
  })
}

// 好友列表（含最近消息、未读数）
export function getFriendList() {
  return request({
    url: '/friend/list',
    method: 'get'
  })
}

// 收到的好友申请列表
export function getFriendRequests() {
  return request({
    url: '/friend/requests',
    method: 'get'
  })
}

// 处理好友申请
export function handleFriendRequest(requestId, accept) {
  return request({
    url: '/friend/handle',
    method: 'post',
    params: { requestId, accept }
  })
}

// 删除好友
export function removeFriend(friendId) {
  return request({
    url: `/friend/remove/${friendId}`,
    method: 'delete'
  })
}

// ==================== 聊天 ====================

// 发送聊天消息
export function sendChatMessage(toUserId, content) {
  return request({
    url: '/chat/send',
    method: 'post',
    data: { toUserId, content }
  })
}

// 与某好友的聊天记录
export function getChatHistory(friendId) {
  return request({
    url: '/chat/history',
    method: 'get',
    params: { friendId }
  })
}

// 未读消息总数（导航栏红点）
export function getChatUnreadCount() {
  return request({
    url: '/chat/unread/count',
    method: 'get'
  })
}

// 标记与某好友的聊天为已读
export function markChatRead(friendId) {
  return request({
    url: '/chat/read',
    method: 'post',
    params: { friendId }
  })
}
