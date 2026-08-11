<template>
  <div class="chat-page">
    <!-- 顶部栏 -->
    <header class="chat-header">
      <el-button link class="back-btn" @click="goBack">← 返回</el-button>
      <div class="header-tabs">
        <span class="header-tab" :class="{ active: activeTab === 'chat' }" @click="activeTab = 'chat'">💬 好友聊天</span>
        <span class="header-tab" :class="{ active: activeTab === 'messages' }" @click="switchToMessages">📋 系统消息</span>
      </div>
      <div class="header-unread" v-if="activeTab === 'chat' && totalUnread > 0">
        <span class="unread-dot"></span> 共 {{ totalUnread }} 条未读
      </div>
    </header>

    <div class="chat-body">
      <!-- ===== 左侧：好友面板 ===== -->
      <aside class="friend-panel">
        <!-- 搜索添加好友 -->
        <div class="search-box">
          <el-input
            v-model="searchAccount"
            placeholder="输入账号添加好友"
            clearable
            @keyup.enter="doSearch"
            @clear="clearSearch"
          >
            <template #append>
              <el-button :icon="Search" @click="doSearch" />
            </template>
          </el-input>
        </div>

        <!-- 搜索结果 -->
        <div v-if="searchResult" class="search-result rc-card">
          <template v-if="searchResult.id">
            <div class="sr-row">
              <img class="sr-avatar" :src="searchResult.avatar || defaultAvatar" />
              <div class="sr-info">
                <div class="sr-name">{{ searchResult.nickname || '未设置昵称' }}</div>
                <div class="sr-account">账号：{{ searchResult.accountNo }}</div>
              </div>
              <el-button
                v-if="searchResult.relationship === 0"
                size="small"
                type="primary"
                @click="addFriend(searchResult)"
              >+ 加好友</el-button>
              <span v-else-if="searchResult.relationship === 1" class="sr-status">已是好友</span>
              <span v-else-if="searchResult.relationship === 2" class="sr-status">已申请</span>
              <span v-else-if="searchResult.relationship === 3" class="sr-status">对方已申请</span>
              <span v-else-if="searchResult.relationship === -1" class="sr-status">用户不存在</span>
              <span v-else-if="searchResult.relationship === -2" class="sr-status">这是你自己</span>
            </div>
          </template>
          <div v-else class="sr-empty">未找到该账号的用户</div>
        </div>

        <!-- 好友申请 -->
        <div v-if="pendingRequests.length" class="section-block">
          <div class="section-title">
            好友申请 <span class="req-badge">{{ pendingRequests.length }}</span>
          </div>
          <div v-for="req in pendingRequests" :key="'req-' + req.requestId" class="request-item">
            <img class="sr-avatar" :src="req.avatar || defaultAvatar" />
            <div class="sr-info">
              <div class="sr-name">{{ req.nickname }}</div>
              <div class="sr-account">{{ req.accountNo }}</div>
            </div>
            <div class="req-actions">
              <el-button size="small" type="primary" @click="acceptRequest(req)">接受</el-button>
              <el-button size="small" @click="rejectRequest(req)">拒绝</el-button>
            </div>
          </div>
        </div>

        <!-- 好友列表 -->
        <div class="section-block">
          <div class="section-title">我的好友（{{ friends.length }}）</div>
          <div class="friend-list">
            <div
              v-for="f in friends"
              :key="'f-' + f.id"
              class="friend-item"
              :class="{ active: currentFriend && currentFriend.id === f.id }"
              @click="selectFriend(f)"
            >
              <img class="sr-avatar" :src="f.avatar || defaultAvatar" />
              <div class="sr-info">
                <div class="sr-name">{{ f.nickname }}</div>
                <div class="sr-account ellipsis">{{ f.lastMessage || '暂无聊天记录' }}</div>
              </div>
              <div class="friend-meta">
                <div class="friend-time" v-if="f.lastMessageTime">{{ formatTime(f.lastMessageTime) }}</div>
                <el-badge v-if="f.unreadCount > 0" :value="f.unreadCount" :max="99" class="friend-badge" />
              </div>
            </div>
            <el-empty v-if="!friends.length" description="还没有好友，用上面搜索框添加吧" :image-size="70" />
          </div>
        </div>
      </aside>

      <!-- ===== 右侧：好友聊天窗口（点击好友跳转独立对话页） ===== -->
      <main class="chat-window" v-if="activeTab === 'chat'">
        <div class="chat-placeholder">
          <div class="placeholder-icon">💬</div>
          <p>点击左侧好友，开始聊天吧</p>
        </div>
      </main>

      <!-- ===== 右侧：系统消息面板 ===== -->
      <main class="chat-window sys-msg-panel" v-else>
        <div class="sys-msg-toolbar">
          <el-radio-group v-model="msgFilter" size="small" @change="loadSysMessages">
            <el-radio-button value="all">全 部</el-radio-button>
            <el-radio-button value="share">房源分享</el-radio-button>
            <el-radio-button value="repair">报修反馈</el-radio-button>
            <el-radio-button value="dispute">纠纷消息</el-radio-button>
            <el-radio-button value="landlord">房东消息</el-radio-button>
          </el-radio-group>
        </div>
        <div class="sys-msg-list" v-loading="sysMsgLoading">
          <div v-if="sysMessages.length === 0" class="chat-placeholder">
            <div class="placeholder-icon">📋</div>
            <p>暂无系统消息</p>
          </div>
          <div
            v-for="msg in sysMessages"
            :key="msg.id"
            class="sys-msg-item"
            :class="{ unread: msg.isRead === 0 }"
          >
            <img class="sys-msg-avatar" :src="msg.senderAvatar || defaultAvatar" />
            <div class="sys-msg-body">
              <div class="sys-msg-header">
                <span class="sys-msg-sender">{{ msg.senderName || '系统' }}</span>
                <span class="sys-msg-time">{{ formatTime(msg.createTime) }}</span>
              </div>
              <div class="sys-msg-content">{{ msg.content }}</div>
              <el-tag size="small" type="info" v-if="msg.type">{{ typeMap[msg.type] || msg.type }}</el-tag>
            </div>
          </div>
        </div>
        <div class="sys-msg-pager" v-if="sysMsgTotal > pageSize">
          <el-pagination
            background
            layout="prev, pager, next"
            :total="sysMsgTotal"
            :page-size="pageSize"
            :current-page="sysMsgPage"
            @current-change="sysMsgPageChange"
          />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import {
  searchUser,
  sendFriendRequest,
  getFriendList,
  getFriendRequests,
  handleFriendRequest,
  getChatUnreadCount
} from '@/api/chat'
import { getMessages } from '@/api/message'

const router = useRouter()
const route = useRoute()
const defaultAvatar = 'https://ui-avatars.com/api/?name=User&background=ff6a00&color=fff'

const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')

const searchAccount = ref('')
const searchResult = ref(null)
const pendingRequests = ref([])
const friends = ref([])
const totalUnread = ref(0)

let unreadTimer = null

// ==================== 系统消息 ====================
const activeTab = ref('chat')
const msgFilter = ref('all')
const sysMessages = ref([])
const sysMsgLoading = ref(false)
const sysMsgPage = ref(1)
const sysMsgTotal = ref(0)
const pageSize = 10

const typeMap = { share: '房源分享', repair: '报修反馈', dispute: '纠纷消息', landlord: '房东消息' }

const switchToMessages = () => {
  activeTab.value = 'messages'
  sysMsgPage.value = 1
  loadSysMessages()
}

const loadSysMessages = async () => {
  sysMsgLoading.value = true
  try {
    const params = { pageNum: sysMsgPage.value, pageSize }
    if (msgFilter.value !== 'all') params.type = msgFilter.value
    const res = await getMessages(params)
    if (res.code === 200) {
      sysMessages.value = res.data?.records || []
      sysMsgTotal.value = res.data?.total || 0
    }
  } catch (e) { /* 静默 */ }
  finally { sysMsgLoading.value = false }
}

const sysMsgPageChange = (page) => {
  sysMsgPage.value = page
  loadSysMessages()
}

// ==================== 数据加载 ====================

const loadFriends = async () => {
  try {
    const res = await getFriendList()
    if (res.code === 200) {
      friends.value = res.data || []
    }
  } catch (e) { /* 已由拦截器统一提示 */ }
}

const loadRequests = async () => {
  try {
    const res = await getFriendRequests()
    if (res.code === 200) {
      pendingRequests.value = res.data || []
    }
  } catch (e) { /* ignore */ }
}

const loadUnread = async () => {
  try {
    const res = await getChatUnreadCount()
    if (res.code === 200) {
      totalUnread.value = res.data || 0
    }
  } catch (e) { /* ignore */ }
}

const loadAll = () => {
  loadFriends()
  loadRequests()
  loadUnread()
}

// ==================== 搜索 & 加好友 ====================

const doSearch = async () => {
  const account = (searchAccount.value || '').trim()
  if (!account) {
    ElMessage.warning('请输入要搜索的账号')
    return
  }
  try {
    const res = await searchUser(account)
    if (res.code === 200) {
      searchResult.value = res.data
    }
  } catch (e) { /* ignore */ }
}

const clearSearch = () => {
  searchResult.value = null
}

const addFriend = async (user) => {
  try {
    const res = await sendFriendRequest(user.id)
    if (res.code === 200) {
      ElMessage.success(res.data || '好友申请已发送')
      doSearch()
    }
  } catch (e) { /* ignore */ }
}

// ==================== 好友申请处理 ====================

const acceptRequest = async (req) => {
  try {
    const res = await handleFriendRequest(req.requestId, true)
    if (res.code === 200) {
      ElMessage.success('已添加为好友')
      loadAll()
    }
  } catch (e) { /* ignore */ }
}

const rejectRequest = async (req) => {
  try {
    const res = await handleFriendRequest(req.requestId, false)
    if (res.code === 200) {
      ElMessage.success('已拒绝该申请')
      loadAll()
    }
  } catch (e) { /* ignore */ }
}

// ==================== 聊天 ====================

const scrollToBottom = async () => {
  await nextTick()
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}

const selectFriend = async (friend) => {
  // 跳转到独立聊天对话页
  router.push(`/chat/${friend.id}`)
}

// ==================== 工具函数 ====================

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  if (isNaN(date.getTime())) return String(time)
  const now = new Date()
  const sameDay = date.toDateString() === now.toDateString()
  const pad = (n) => String(n).padStart(2, '0')
  if (sameDay) {
    return `${pad(date.getHours())}:${pad(date.getMinutes())}`
  }
  return `${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

const goBack = () => {
  const role = userInfo.role
  if (role === 2) {
    router.push('/tenant/home')
  } else if (role === 1) {
    router.push('/landlord/dashboard')
  } else if (role === 0) {
    router.push('/admin/dashboard')
  } else {
    router.push('/')
  }
}

const startUnreadTimer = () => {
  stopUnreadTimer()
  unreadTimer = setInterval(loadUnread, 5000)
}

const stopUnreadTimer = () => {
  if (unreadTimer) { clearInterval(unreadTimer); unreadTimer = null }
}

// ==================== 生命周期 ====================

onMounted(async () => {
  await loadFriends()
  await loadRequests()
  loadUnread()
  startUnreadTimer()

  // 从房源详情「联系房东」跳转过来：直接导航到对话页
  const friendIdParam = route.query.friendId
  if (friendIdParam) {
    router.push(`/chat/${friendIdParam}`)
  }
})

onUnmounted(() => {
  stopUnreadTimer()
})
</script>


<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--bg-page);
}

/* ===== 顶部栏 ===== */
.chat-header {
  display: flex;
  align-items: center;
  gap: 16px;
  height: 56px;
  padding: 0 20px;
  background: var(--bg-card);
  box-shadow: 0 2px 8px rgba(255, 106, 0, 0.15);
  z-index: 10;
  position: relative;
}
.back-btn {
  font-size: 15px;
  color: var(--text-sub);
}
.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 17px;
  font-weight: 700;
  color: var(--text-main);
}
.logo-dot {
  color: #ff6a00;
}
.header-unread {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #e8341e;
}
.unread-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #e8341e;
  animation: pulse 1.2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

/* ===== 主体 ===== */
.chat-body {
  flex: 1;
  display: flex;
  min-height: 0;
}

/* ===== 左侧面板 ===== */
.friend-panel {
  width: 320px;
  min-width: 320px;
  background: var(--bg-card);
  border-right: 1px solid var(--border-color);
  overflow-y: auto;
  padding: 12px;
}
.search-box {
  margin-bottom: 10px;
}
.search-result {
  padding: 10px;
  margin-bottom: 10px;
}
.sr-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.sr-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}
.sr-info {
  flex: 1;
  min-width: 0;
}
.sr-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.sr-account {
  font-size: 12px;
  color: var(--text-sub);
  margin-top: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.sr-status {
  font-size: 12px;
  color: var(--text-sub);
  flex-shrink: 0;
}
.sr-empty {
  text-align: center;
  color: var(--text-sub);
  font-size: 13px;
  padding: 6px 0;
}
.ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 区块标题 */
.section-block {
  margin-top: 8px;
}
.section-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-sub);
  padding: 6px 4px;
  border-bottom: 1px solid var(--border-color);
}
.req-badge {
  display: inline-block;
  min-width: 18px;
  height: 18px;
  line-height: 18px;
  text-align: center;
  border-radius: 9px;
  background: #e8341e;
  color: #fff;
  font-size: 12px;
  padding: 0 5px;
}

/* 好友申请条目 */
.request-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 4px;
  border-bottom: 1px solid var(--border-color);
}
.req-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

/* 好友列表 */
.friend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}
.friend-item:hover {
  background: var(--bg-hover);
}
.friend-item.active {
  background: rgba(255, 106, 0, 0.18);
}
.friend-item .sr-avatar {
  width: 44px;
  height: 44px;
}
.friend-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  flex-shrink: 0;
}
.friend-time {
  font-size: 11px;
  color: var(--text-light);
}
.friend-badge {
  --el-badge-bg-color: #e8341e;
}

/* ===== 右侧聊天窗口 ===== */
.chat-window {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: var(--bg-page);
}
.chat-window-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 20px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
}
.cw-user {
  display: flex;
  align-items: center;
  gap: 12px;
}
.cw-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}
.cw-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-main);
}
.cw-account {
  font-size: 12px;
  color: var(--text-sub);
}

/* 消息列表 */
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.message-row {
  display: flex;
  gap: 10px;
  max-width: 72%;
}
.message-row.mine {
  align-self: flex-end;
  flex-direction: row-reverse;
}
.message-row.theirs {
  align-self: flex-start;
}
.msg-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}
.msg-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.message-row.mine .msg-content {
  align-items: flex-end;
}
.message-row.theirs .msg-content {
  align-items: flex-start;
}
.msg-time {
  font-size: 11px;
  color: var(--text-light);
}
.msg-bubble {
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 14px;
  line-height: 1.5;
  word-break: break-word;
}
.message-row.theirs .msg-bubble {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  color: var(--text-main);
  border-top-left-radius: 2px;
}
.message-row.mine .msg-bubble {
  background: linear-gradient(135deg, #ff8b3d, #ff6a00);
  color: #fff;
  border-top-right-radius: 2px;
}
.no-msg {
  text-align: center;
  color: var(--text-light);
  margin-top: 40px;
  font-size: 13px;
}

/* 输入区 */
.input-area {
  background: var(--bg-card);
  border-top: 1px solid var(--border-color);
  padding: 12px 16px;
}
.input-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}
.toolbar-tip {
  font-size: 12px;
  color: var(--text-light);
}

/* 空状态 */
.chat-placeholder {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-light);
}
.placeholder-icon {
  font-size: 56px;
}
.chat-placeholder p {
  font-size: 14px;
  margin-top: 12px;
}

/* 顶部标签切换 */
.header-tabs {
  display: flex;
  gap: 24px;
}
.header-tab {
  font-size: 15px;
  color: var(--text-sub);
  cursor: pointer;
  padding: 4px 0;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}
.header-tab:hover { color: #ff6a00; }
.header-tab.active {
  color: #ff6a00;
  font-weight: 600;
  border-bottom-color: #ff6a00;
}

/* 系统消息面板 */
.sys-msg-panel {
  flex-direction: column;
  display: flex;
  background: var(--bg-page);
}
.sys-msg-toolbar {
  padding: 12px 16px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
}
.sys-msg-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}
.sys-msg-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: var(--bg-card);
  border-radius: 8px;
  margin-bottom: 8px;
  transition: background 0.2s;
}
.sys-msg-item.unread { background: rgba(255, 106, 0, 0.12); border-left: 3px solid #ff6a00; }
.sys-msg-item:hover { box-shadow: 0 2px 8px var(--shadow-color); }
.sys-msg-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}
.sys-msg-body { flex: 1; min-width: 0; }
.sys-msg-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.sys-msg-sender { font-size: 13px; font-weight: 600; color: var(--text-main); }
.sys-msg-time { font-size: 11px; color: var(--text-light); }
.sys-msg-content {
  font-size: 13px;
  color: var(--text-main);
  line-height: 1.5;
  margin-bottom: 6px;
  word-break: break-word;
}
.sys-msg-pager {
  padding: 10px 16px;
  display: flex;
  justify-content: center;
  background: var(--bg-card);
  border-top: 1px solid var(--border-color);
}

/* 响应式 */
@media (max-width: 768px) {
  .friend-panel {
    width: 100%;
    min-width: 0;
    border-right: none;
    border-bottom: 1px solid var(--border-color);
    max-height: 45vh;
  }
  .chat-body {
    flex-direction: column;
  }
}
</style>
