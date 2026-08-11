<template>
  <div class="messages-page">
    <div class="messages-header">
      <h2>💬 消息中心</h2>
      <div class="message-tabs">
        <el-button 
          v-for="tab in messageTabs"
          :key="tab.id"
          :type="activeTab === tab.id ? 'primary' : 'default'"
          @click="activeTab = tab.id; loadMessages()"
          size="small"
        >
          {{ tab.label }}
          <el-badge :value="getUnreadCount(tab.id)" class="item" />
        </el-button>
      </div>
    </div>

    <!-- 消息列表 -->
    <div class="messages-list">
      <el-empty v-if="messages.length === 0 && !loading" description="暂无消息" />
      
      <div v-if="loading" class="loading">
        <el-skeleton :rows="3" animated />
      </div>

      <div v-for="msg in messages" :key="msg.id" class="message-item" :class="{ unread: !msg.isRead }">
        <div class="message-header">
          <div class="sender-info">
            <img :src="msg.senderAvatar || 'https://ui-avatars.com/api/?name=' + msg.senderName" class="avatar" />
            <div class="sender-detail">
              <div class="sender-name">{{ msg.senderName }}</div>
              <div class="message-type-tag">
                <el-tag :type="getMessageTypeColor(msg.type)" size="small">{{ getMessageTypeName(msg.type) }}</el-tag>
              </div>
            </div>
          </div>
          <div class="message-time">{{ formatTime(msg.createTime) }}</div>
        </div>

        <div class="message-content">
          <p>{{ msg.content }}</p>
          <div v-if="msg.roomInfo" class="room-preview">
            <img :src="msg.roomInfo.cover" class="room-thumb" />
            <div class="room-info">
              <div class="room-title">{{ msg.roomInfo.title }}</div>
              <div class="room-price">¥{{ msg.roomInfo.price }}/晚</div>
            </div>
          </div>
        </div>

        <div class="message-actions">
          <el-button v-if="msg.type === 'share'" link type="primary" @click="viewRoom(msg.roomInfo?.id)">
            查看房源
          </el-button>
          <el-button v-if="msg.type === 'share'" link type="primary" @click="shareToFriend(msg)">
            分享给朋友
          </el-button>
          <el-button v-if="msg.type === 'repair'" link type="primary" @click="viewRepairDetail(msg.relationId)">
            查看详情
          </el-button>
          <el-button v-if="msg.type === 'dispute'" link type="primary" @click="viewDisputeDetail(msg.relationId)">
            查看详情
          </el-button>
          <el-button link type="danger" @click="deleteMessage(msg.id)">删除</el-button>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:page-num="pageNum"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 30]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadMessages"
        @current-change="loadMessages"
      />
    </div>

    <!-- 分享对话框 -->
    <el-dialog v-model="shareDialogVisible" title="分享房源" width="500px">
      <div class="share-form">
        <el-form :model="shareForm" label-width="80px">
          <el-form-item label="分享给">
            <el-input v-model="shareForm.recipientPhone" placeholder="输入租客手机号" />
          </el-form-item>
          <el-form-item label="留言">
            <el-input v-model="shareForm.message" type="textarea" placeholder="可选：添加个人留言" rows="3" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="shareDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitShare" :loading="sharing">分享</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const loading = ref(false)
const messages = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(10)
const activeTab = ref('all')
const sharing = ref(false)

const messageTabs = [
  { id: 'all', label: '全部消息' },
  { id: 'landlord', label: '房东消息' },
  { id: 'repair', label: '报修反馈' },
  { id: 'dispute', label: '纠纷消息' },
  { id: 'share', label: '分享房源' }
]

const shareDialogVisible = ref(false)
const shareForm = reactive({
  recipientPhone: '',
  message: '',
  roomId: null
})

// 消息类型颜色映射
const getMessageTypeColor = (type) => {
  const map = {
    'landlord': 'warning',
    'repair': 'info',
    'dispute': 'danger',
    'share': 'success'
  }
  return map[type] || 'default'
}

// 消息类型名称
const getMessageTypeName = (type) => {
  const map = {
    'landlord': '房东消息',
    'repair': '报修反馈',
    'dispute': '纠纷消息',
    'share': '分享房源'
  }
  return map[type] || '消息'
}

// 获取各类型未读消息数
const getUnreadCount = (tabId) => {
  if (tabId === 'all') {
    return messages.value.filter(m => !m.isRead).length
  }
  return messages.value.filter(m => m.type === tabId && !m.isRead).length
}

// 格式化时间
const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
  if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'
  
  return date.toLocaleDateString()
}

// 加载消息
const loadMessages = async () => {
  loading.value = true
  try {
    const params = {
      pageNum: pageNum.value,
      pageSize: pageSize.value
    }
    if (activeTab.value !== 'all') {
      params.type = activeTab.value
    }

    const res = await request({
      url: '/message/list',
      method: 'get',
      params
    })

    if (res.code === 200) {
      messages.value = res.data?.records || []
      total.value = res.data?.total || 0
    }
  } catch (error) {
    console.error('加载消息失败', error)
    messages.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 查看房源
const viewRoom = (roomId) => {
  if (roomId) {
    router.push(`/room/${roomId}`)
  }
}

// 查看报修详情
const viewRepairDetail = (repairId) => {
  router.push(`/tenant/my/repairs?id=${repairId}`)
}

// 查看纠纷详情
const viewDisputeDetail = (disputeId) => {
  router.push(`/tenant/my/disputes?id=${disputeId}`)
}

// 删除消息
const deleteMessage = async (messageId) => {
  try {
    const res = await request({
      url: `/message/${messageId}`,
      method: 'delete'
    })
    if (res.code === 200) {
      ElMessage.success('已删除')
      loadMessages()
    }
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// 分享房源
const shareToFriend = (message) => {
  shareForm.roomId = message.roomInfo?.id
  shareForm.recipientPhone = ''
  shareForm.message = ''
  shareDialogVisible.value = true
}

// 提交分享
const submitShare = async () => {
  if (!shareForm.recipientPhone) {
    ElMessage.warning('请输入接收者手机号')
    return
  }

  sharing.value = true
  try {
    const res = await request({
      url: '/message/share',
      method: 'post',
      data: {
        roomId: shareForm.roomId,
        recipientPhone: shareForm.recipientPhone,
        message: shareForm.message
      }
    })
    if (res.code === 200) {
      ElMessage.success('分享成功')
      shareDialogVisible.value = false
      loadMessages()
    } else {
      ElMessage.error(res.message || '分享失败')
    }
  } catch (error) {
    ElMessage.error('分享失败，请稍后重试')
  } finally {
    sharing.value = false
  }
}

onMounted(() => {
  loadMessages()
})
</script>

<style scoped>
.messages-page {
  background: var(--bg-card);
  border-radius: 8px;
  padding: 20px;
}

.messages-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.messages-header h2 {
  margin: 0;
  font-size: 20px;
}

.message-tabs {
  display: flex;
  gap: 8px;
}

.messages-list {
  margin: 20px 0;
}

.loading {
  padding: 20px;
}

.message-item {
  padding: 16px;
  margin-bottom: 12px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  }

  &.unread {
    background-color: #f0f9ff;
    border-color: #409eff;
  }
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.sender-info {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.sender-detail {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sender-name {
  font-weight: 600;
  font-size: 14px;
  color: #333;
}

.message-type-tag {
  display: inline-block;
  width: fit-content;
}

.message-time {
  font-size: 12px;
  color: #999;
}

.message-content {
  margin: 12px 0;
  padding: 12px;
  background-color: #f9f9f9;
  border-radius: 6px;
  line-height: 1.6;
  color: #555;
}

.message-content p {
  margin: 0 0 12px 0;
}

.room-preview {
  display: flex;
  gap: 10px;
  padding-top: 8px;
  border-top: 1px solid #e8e8e8;
}

.room-thumb {
  width: 60px;
  height: 60px;
  border-radius: 6px;
  object-fit: cover;
}

.room-info {
  flex: 1;
}

.room-title {
  font-weight: 500;
  font-size: 13px;
  margin-bottom: 4px;
  color: #333;
}

.room-price {
  font-size: 12px;
  color: #ff6b6b;
}

.message-actions {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #e8e8e8;
}

.pagination {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.share-form {
  padding: 20px 0;
}

@media (max-width: 768px) {
  .messages-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .message-tabs {
    margin-top: 12px;
    flex-wrap: wrap;
  }

  .message-item {
    padding: 12px;
  }

  .room-preview {
    flex-direction: column;
  }

  .room-thumb {
    width: 100%;
  }
}
</style>
