import request from '@/utils/request'

/**
 * 租赁助手 AI 对话
 * @param {string} message 用户输入
 * @returns Promise<{code, message, data:{reply, rooms}}>
 */
export function aiChat(message) {
  return request({
    url: '/ai/chat',
    method: 'post',
    data: { message }
  })
}
