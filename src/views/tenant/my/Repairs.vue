<template>
  <div class="repairs-page">
    <div class="page-header">
      <h2>🔧 我的报修</h2>
      <el-button type="primary" size="small" @click="openDialog">＋ 发起报修</el-button>
    </div>

    <el-empty v-if="repairs.length === 0 && !loading" description="暂无报修记录" />

    <div v-if="loading" class="loading">
      <el-skeleton :rows="3" animated />
    </div>

    <div v-for="repair in repairs" :key="repair.id" class="repair-card">
      <div class="repair-header">
        <div class="repair-title">
          <span class="repair-icon">🔧</span>
          <span class="repair-title-text">{{ repair.title }}</span>
          <el-tag :type="getStatusType(repair.status)" size="small">{{ getStatusName(repair.status) }}</el-tag>
        </div>
        <div class="repair-time">{{ formatDate(repair.createTime) }}</div>
      </div>
      <div class="repair-body">
        <div class="repair-room">📍 {{ getRoomName(repair.roomId) }}</div>
        <div class="repair-desc">{{ repair.description }}</div>
        <div v-if="repair.images" class="repair-images">
          <el-image
            v-for="(img, idx) in repair.images.split(',').filter(Boolean)"
            :key="idx"
            :src="img"
            :preview-src-list="repair.images.split(',').filter(Boolean)"
            style="width: 100px; height: 100px; margin-right: 8px; border-radius: 4px; object-fit: cover;"
            fit="cover"
          />
        </div>
        <div v-if="repair.handlerRemark" class="repair-reply">
          <div class="reply-label">处理回复：</div>
          <div>{{ repair.handlerRemark }}</div>
        </div>
      </div>
      <div v-if="repair.status === 0" class="repair-actions">
        <el-button type="danger" size="small" plain @click="cancelRepair(repair.id)">撤销报修</el-button>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" title="发起报修" width="600px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="房源" required>
          <el-select v-model="form.roomId" placeholder="请选择房源" style="width: 100%">
            <el-option v-for="room in orderedRooms" :key="room.roomId" :label="room.title" :value="room.roomId" />
          </el-select>
        </el-form-item>
        <el-form-item label="标题" required>
          <el-input v-model="form.title" placeholder="请输入报修标题" />
        </el-form-item>
        <el-form-item label="描述" required>
          <el-input v-model="form.description" type="textarea" :rows="4" placeholder="请描述问题" />
        </el-form-item>
        <el-form-item label="上传图片">
          <el-upload
            v-model:file-list="fileList"
            list-type="picture-card"
            :auto-upload="false"
            accept="image/*"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitRepair">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import request from '@/utils/request'

const loading = ref(false)
const repairs = ref([])
const orderedRooms = ref([])
const dialogVisible = ref(false)
const submitting = ref(false)
const fileList = ref([])

const form = reactive({
  roomId: null,
  title: '',
  description: ''
})

const roomMap = computed(() => {
  const map = {}
  orderedRooms.value.forEach((room) => {
    map[room.roomId] = room.title
  })
  return map
})

const getStatusType = (status) => {
  const map = { '0': 'danger', '1': 'warning', '2': 'success', '3': 'info' }
  return map[String(status)] || 'default'
}

const getStatusName = (status) => {
  const map = { '0': '待处理', '1': '处理中', '2': '已完成', '3': '已关闭' }
  return map[String(status)] || '未知'
}

const getRoomName = (roomId) => {
  return roomMap.value[roomId] || `房源 #${roomId}`
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString()
}

const loadRepairs = async () => {
  loading.value = true
  try {
    const res = await request({ url: '/repair/my', method: 'get', params: { pageNum: 1, pageSize: 100 } })
    if (res.code === 200) { repairs.value = res.data?.records || [] }
    else { ElMessage.error(res.message || '加载失败') }
  } catch (error) { console.error('加载报修失败', error); ElMessage.error('网络请求失败') }
  finally { loading.value = false }
}

const loadOrderedRooms = async () => {
  try {
    const res = await request({ url: '/order/tenant/list', method: 'get', params: { pageNum: 1, pageSize: 100 } })
    if (res.code === 200) {
      const list = res.data?.records || []
      const map = {}
      list.forEach((order) => { if (order.roomId && !map[order.roomId]) { map[order.roomId] = { roomId: order.roomId, title: order.roomTitleSnapshot || `房源 #${order.roomId}` } } })
      orderedRooms.value = Object.values(map)
    }
  } catch (error) { console.error('加载房源失败', error) }
}

const openDialog = () => {
  form.roomId = null; form.title = ''; form.description = ''
  fileList.value = []
  dialogVisible.value = true
}

const submitRepair = async () => {
  if (!form.roomId) { ElMessage.warning('请选择房源'); return }
  if (!form.title.trim()) { ElMessage.warning('请输入报修标题'); return }
  if (!form.description.trim()) { ElMessage.warning('请输入报修描述'); return }
  submitting.value = true
  try {
    const fd = new FormData()
    const repairJson = JSON.stringify({ roomId: form.roomId, title: form.title, description: form.description })
    fd.append('repair', new Blob([repairJson], { type: 'application/json' }), 'repair.json')
    fileList.value.forEach((item) => { if (item.raw) fd.append('files', item.raw) })
    const res = await request({ url: '/repair/submit', method: 'post', data: fd })
    if (res.code === 200) { ElMessage.success('报修提交成功'); dialogVisible.value = false; loadRepairs() }
    else { ElMessage.error(res.message || '提交失败') }
  } catch (error) { ElMessage.error('提交失败') }
  finally { submitting.value = false }
}

const cancelRepair = (repairId) => {
  ElMessageBox.confirm('确定要撤销此报修吗？', '提示', { confirmButtonText: '确定撤销', cancelButtonText: '取消', type: 'warning' })
    .then(async () => {
      try {
        const res = await request({ url: `/repair/cancel/${repairId}`, method: 'post' })
        if (res.code === 200) { ElMessage.success('已撤销报修'); loadRepairs() }
        else { ElMessage.error(res.message || '撤销失败') }
      } catch (error) { ElMessage.error('撤销失败') }
    }).catch(() => {})
}

onMounted(() => { loadRepairs(); loadOrderedRooms() })
</script>
<style scoped>
.repairs-page { background: var(--bg-card); padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h2 { margin: 0; }
.repair-card { padding: 16px; margin-bottom: 12px; border: 1px solid #f0f0f0; border-radius: 8px; }
.repair-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
.repair-title { display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 14px; }
.repair-time { font-size: 12px; color: #999; }
.repair-body { margin-bottom: 8px; }
.repair-room { font-size: 13px; color: #666; margin-bottom: 8px; }
.repair-desc { font-size: 13px; line-height: 1.6; color: #555; padding: 8px 12px; background: #f9f9f9; border-radius: 4px; margin-bottom: 8px; }
.repair-images { margin-bottom: 8px; display: flex; flex-wrap: wrap; }
.repair-reply { padding: 8px 12px; background: #f0f9ff; border-radius: 4px; border-left: 3px solid #409eff; margin-bottom: 8px; }
.reply-label { font-weight: 600; font-size: 12px; color: #409eff; margin-bottom: 4px; }
.repair-actions { display: flex; gap: 8px; padding-top: 12px; border-top: 1px solid #f0f0f0; }
@media (max-width: 768px) { .repairs-page { padding: 12px; } .page-header { flex-direction: column; align-items: flex-start; gap: 12px; } }
</style>