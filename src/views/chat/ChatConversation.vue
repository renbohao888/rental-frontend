<template>
  <div class="chat-conversation-page">
    <header class="conv-header">
      <el-button link class="conv-back" @click="goBack">← 返回消息列表</el-button>
      <div class="conv-user" v-if="friend">
        <img class="conv-avatar" :src="friend.avatar || defaultAvatar" />
        <div class="conv-user-info">
          <div class="conv-name">{{ friend.nickname }}</div>
          <div class="conv-account">账号：{{ friend.accountNo }}</div>
        </div>
      </div>
      <div class="conv-actions">
        <el-button link type="danger" size="small" @click="confirmRemoveFriend">删除好友</el-button>
      </div>
    </header>

    <div class="conv-messages" ref="msgListRef">
      <div v-if="!messages.length" class="conv-empty">打个招呼吧～</div>
      <div
        v-for="msg in messages" :key="msg.id" class="conv-msg-row"
        :class="String(msg.fromUserId) === String(myId) ? 'mine' : 'theirs'"
      >
        <img class="conv-msg-avatar"
          :src="(String(msg.fromUserId) === String(myId) ? myAvatar : friend?.avatar) || defaultAvatar" />
        <div class="conv-msg-content">
          <div class="conv-msg-time">{{ formatTime(msg.createTime) }}</div>
          <div v-if="!msg.roomInfo" class="conv-msg-bubble">{{ msg.content }}</div>
          <div v-else class="conv-msg-room-card" @click="viewRoom(msg.roomInfo.id)">
            <img class="room-card-cover" :src="msg.roomInfo.cover || placeholder(msg.roomInfo.id)" />
            <div class="room-card-body">
              <div class="room-card-title">{{ msg.roomInfo.title }}</div>
              <div class="room-card-addr">{{ msg.roomInfo.address }}</div>
              <div class="room-card-price">¥{{ msg.roomInfo.price }}<span>/晚</span></div>
            </div>
          </div>
          <div v-if="msg.roomInfo && msg.content" class="conv-msg-bubble conv-msg-text">{{ msg.content }}</div>
        </div>
      </div>
    </div>

    <div class="conv-input-area">
      <div class="conv-toolbar">
        <el-button link type="primary" @click="showShareDialog = true">🏠 分享房源</el-button>
      </div>
      <div class="conv-input-row">
        <el-input v-model="draft" type="textarea" :rows="2" resize="none" maxlength="1000"
          placeholder="输入消息内容，Enter 发送" @keyup.enter.exact.prevent="sendMessage" />
        <el-button type="primary" :loading="sending" @click="sendMessage" class="conv-send-btn">发送</el-button>
      </div>
    </div>

    <el-dialog v-model="showShareDialog" :title="'分享房源给 ' + (friend?.nickname || '')" width="550px" top="8vh">
      <div class="share-search-box">
        <el-input v-model="roomSearchKeyword" placeholder="搜索房源标题或地址" clearable
          @keyup.enter="searchRooms" @clear="searchRooms">
          <template #append><el-button @click="searchRooms">搜索</el-button></template>
        </el-input>
      </div>
      <div v-loading="roomLoading" class="share-room-list">
        <el-empty v-if="!roomLoading && !rooms.length" description="没有找到房源" :image-size="60" />
        <div v-for="room in rooms" :key="room.id" class="share-room-item"
          :class="{ selected: selectedRoom && selectedRoom.id === room.id }" @click="selectedRoom = room">
          <img class="share-room-cover" :src="room.cover || placeholder(room.id)" />
          <div class="share-room-info">
            <div class="share-room-title">{{ room.title }}</div>
            <div class="share-room-addr">{{ room.address }}</div>
            <div class="share-room-price">¥{{ room.price }}<span>/晚</span></div>
          </div>
          <el-checkbox :model-value="selectedRoom && selectedRoom.id === room.id" />
        </div>
      </div>
      <div class="share-message-box">
        <el-input v-model="shareMessage" type="textarea" :rows="2" placeholder="附加留言（选填）" maxlength="200" show-word-limit />
      </div>
      <template #footer>
        <el-button @click="showShareDialog = false">取 消</el-button>
        <el-button type="primary" :disabled="!selectedRoom" :loading="sharing" @click="doShareRoom">发 送</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getFriendList, removeFriend, sendChatMessage, getChatHistory, markChatRead } from '@/api/chat'
import { getRoomList, getMyRooms } from '@/api/room'

const router = useRouter()
const route = useRoute()
const defaultAvatar = 'https://ui-avatars.com/api/?name=User&background=ff6a00&color=fff'
const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
const myId = userInfo.id
const myAvatar = userInfo.avatar

const friend = ref(null)
const messages = ref([])
const draft = ref('')
const sending = ref(false)
const msgListRef = ref(null)

const showShareDialog = ref(false)
const roomSearchKeyword = ref('')
const rooms = ref([])
const roomLoading = ref(false)
const selectedRoom = ref(null)
const shareMessage = ref('')
const sharing = ref(false)

let historyTimer = null

const placeholder = (id) => `https://loremflickr.com/300/200/house?random=${id}`

const goBack = () => { router.push('/chat') }

const loadFriend = async () => {
  const friendId = route.params.friendId
  try {
    const res = await getFriendList()
    if (res.code === 200) {
      const list = res.data || []
      friend.value = list.find(f => String(f.id) === String(friendId))
      if (!friend.value) { ElMessage.warning('好友不存在'); router.push('/chat') }
    }
  } catch (e) { /* ignore */ }
}

const scrollToBottom = async () => {
  await nextTick()
  if (msgListRef.value) msgListRef.value.scrollTop = msgListRef.value.scrollHeight
}

const loadHistory = async () => {
  if (!friend.value) return
  try {
    const res = await getChatHistory(friend.value.id)
    if (res.code === 200) { messages.value = res.data || []; scrollToBottom() }
  } catch (e) { /* ignore */ }
}

const sendMessage = async () => {
  const content = (draft.value || '').trim()
  if (!content) { ElMessage.warning('请输入消息内容'); return }
  if (!friend.value) return
  sending.value = true
  try {
    const res = await sendChatMessage(friend.value.id, content)
    if (res.code === 200) { draft.value = ''; await loadHistory() }
  } catch (e) { /* ignore */ }
  finally { sending.value = false }
}

const confirmRemoveFriend = async () => {
  if (!friend.value) return
  try { await ElMessageBox.confirm(`确定删除好友「${friend.value.nickname}」吗？`, '提示', { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' }) }
  catch (e) { return }
  try {
    const res = await removeFriend(friend.value.id)
    if (res.code === 200) { ElMessage.success('已删除好友'); router.push('/chat') }
  } catch (e) { /* ignore */ }
}

const searchRooms = async () => {
  roomLoading.value = true
  try {
    const params = { pageNum: 1, pageSize: 20 }
    if (roomSearchKeyword.value.trim()) params.keyword = roomSearchKeyword.value.trim()
    const role = userInfo.role
    if (role === 1) {
      const res = await getMyRooms()
      if (res.code === 200) {
        let list = res.data || []
        if (roomSearchKeyword.value.trim()) {
          const kw = roomSearchKeyword.value.trim().toLowerCase()
          list = list.filter(r => (r.title && r.title.toLowerCase().includes(kw)) || (r.address && r.address.toLowerCase().includes(kw)))
        }
        rooms.value = list.slice(0, 20)
      }
    } else {
      const res = await getRoomList(params)
      if (res.code === 200 || res.code === 0) rooms.value = res.data?.records || res.data?.list || []
    }
  } catch (e) { /* ignore */ }
  finally { roomLoading.value = false }
}

const doShareRoom = async () => {
  if (!selectedRoom.value || !friend.value) return
  sharing.value = true
  try {
    const room = selectedRoom.value
    const msgText = shareMessage.value.trim()
      ? `[房源分享] ${room.title} - ¥${room.price}/晚\n${shareMessage.value.trim()}`
      : `[房源分享] ${room.title} - ¥${room.price}/晚`
    const { shareRoom } = await import('@/api/message')
    await shareRoom({ roomId: room.id, recipientPhone: friend.value.accountNo, message: shareMessage.value.trim() || `推荐「${room.title}」给你！` }).catch(() => {})
    const res = await sendChatMessage(friend.value.id, msgText)
    if (res.code === 200) {
      ElMessage.success('房源已分享')
      showShareDialog.value = false
      selectedRoom.value = null; shareMessage.value = ''; roomSearchKeyword.value = ''
      await loadHistory()
    }
  } catch (e) { /* ignore */ }
  finally { sharing.value = false }
}

watch(showShareDialog, (val) => {
  if (val) { selectedRoom.value = null; shareMessage.value = ''; roomSearchKeyword.value = ''; searchRooms() }
})

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  if (isNaN(date.getTime())) return String(time)
  const now = new Date()
  const sameDay = date.toDateString() === now.toDateString()
  const pad = (n) => String(n).padStart(2, '0')
  if (sameDay) return `${pad(date.getHours())}:${pad(date.getMinutes())}`
  return `${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

const viewRoom = (roomId) => { if (roomId) router.push(`/room/${roomId}`) }

const startHistoryTimer = () => { stopHistoryTimer(); historyTimer = setInterval(() => { if (friend.value) loadHistory() }, 3000) }
const stopHistoryTimer = () => { if (historyTimer) { clearInterval(historyTimer); historyTimer = null } }

onMounted(async () => {
  await loadFriend()
  if (friend.value) {
    await loadHistory()
    await markChatRead(friend.value.id)
    startHistoryTimer()
  }
})

onUnmounted(() => { stopHistoryTimer() })
</script>



<style scoped>
.chat-conversation-page { display: flex; flex-direction: column; height: 100vh; background: var(--bg-page); }
.conv-header { display: flex; align-items: center; gap: 12px; height: 56px; padding: 0 16px; background: var(--bg-card); box-shadow: 0 2px 8px rgba(255, 106, 0, 0.12); z-index: 10; flex-shrink: 0; }
.conv-back { font-size: 14px; color: var(--text-sub); flex-shrink: 0; }
.conv-user { display: flex; align-items: center; gap: 10px; flex: 1; min-width: 0; }
.conv-avatar { width: 38px; height: 38px; border-radius: 50%; object-fit: cover; flex-shrink: 0; }
.conv-name { font-size: 15px; font-weight: 600; color: var(--text-main); }
.conv-account { font-size: 11px; color: var(--text-sub); }
.conv-actions { flex-shrink: 0; }
.conv-messages { flex: 1; overflow-y: auto; padding: 16px 20px; display: flex; flex-direction: column; gap: 14px; }
.conv-empty { text-align: center; color: var(--text-light); margin-top: 60px; font-size: 14px; }
.conv-msg-row { display: flex; gap: 10px; max-width: 75%; }
.conv-msg-row.mine { align-self: flex-end; flex-direction: row-reverse; }
.conv-msg-row.theirs { align-self: flex-start; }
.conv-msg-avatar { width: 34px; height: 34px; border-radius: 50%; object-fit: cover; flex-shrink: 0; }
.conv-msg-content { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.conv-msg-row.mine .conv-msg-content { align-items: flex-end; }
.conv-msg-row.theirs .conv-msg-content { align-items: flex-start; }
.conv-msg-time { font-size: 11px; color: var(--text-light); }
.conv-msg-bubble { padding: 10px 14px; border-radius: 10px; font-size: 14px; line-height: 1.5; word-break: break-word; }
.conv-msg-row.theirs .conv-msg-bubble { background: var(--bg-card); border: 1px solid var(--border-color); color: var(--text-main); border-top-left-radius: 2px; }
.conv-msg-row.mine .conv-msg-bubble { background: linear-gradient(135deg, #ff8b3d, #ff6a00); color: #fff; border-top-right-radius: 2px; }
.conv-msg-room-card { display: flex; gap: 10px; align-items: center; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 10px; cursor: pointer; transition: box-shadow 0.2s, transform 0.2s; max-width: 280px; }
.conv-msg-room-card:hover { box-shadow: 0 4px 14px var(--shadow-strong); transform: translateY(-1px); }
.room-card-cover { width: 70px; height: 56px; border-radius: 8px; object-fit: cover; flex-shrink: 0; }
.room-card-body { flex: 1; min-width: 0; }
.room-card-title { font-size: 13px; font-weight: 600; color: var(--text-main); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.room-card-addr { font-size: 11px; color: var(--text-sub); margin: 2px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.room-card-price { font-size: 14px; font-weight: 700; color: #ff6a00; }
.room-card-price span { font-size: 11px; font-weight: 400; color: var(--text-sub); }
.conv-msg-text { margin-top: 0; }
.conv-input-area { background: var(--bg-card); border-top: 1px solid var(--border-color); padding: 8px 12px 12px; flex-shrink: 0; }
.conv-toolbar { padding-bottom: 6px; }
.conv-input-row { display: flex; gap: 10px; align-items: flex-end; }
.conv-send-btn { flex-shrink: 0; }
.share-search-box { margin-bottom: 12px; }
.share-room-list { max-height: 300px; overflow-y: auto; margin-bottom: 12px; }
.share-room-item { display: flex; align-items: center; gap: 10px; padding: 10px; border: 1px solid var(--border-color); border-radius: 10px; margin-bottom: 8px; cursor: pointer; transition: all 0.2s; }
.share-room-item:hover { box-shadow: 0 2px 10px var(--shadow-color); }
.share-room-item.selected { border-color: #ff6a00; background: rgba(255, 106, 0, 0.06); }
.share-room-cover { width: 64px; height: 48px; border-radius: 6px; object-fit: cover; flex-shrink: 0; }
.share-room-info { flex: 1; min-width: 0; }
.share-room-title { font-size: 13px; font-weight: 600; color: var(--text-main); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.share-room-addr { font-size: 11px; color: var(--text-sub); margin: 2px 0; }
.share-room-price { font-size: 14px; font-weight: 700; color: #ff6a00; }
.share-room-price span { font-size: 11px; font-weight: 400; color: var(--text-sub); }
.share-message-box { margin-top: 8px; }
@media (max-width: 767px) {
  .conv-messages { padding: 10px 12px; }
  .conv-msg-row { max-width: 88%; }
  .conv-msg-room-card { max-width: 240px; }
  .conv-header { padding: 0 10px; gap: 8px; }
  .conv-back { font-size: 13px; }
  .conv-name { font-size: 14px; }
  .conv-input-row { flex-direction: column; }
  .conv-send-btn { width: 100%; }
}
</style>
