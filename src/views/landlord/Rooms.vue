<template>
  <div class="rooms-page">
    <div class="page-header">
      <h2>🏠 房源管理</h2>
      <el-button type="primary" size="small" @click="openAddDialog">＋ 发布房源</el-button>
    </div>

    <el-empty v-if="rooms.length === 0 && !loading" description="还没有房源，点击右上角发布" />

    <div v-if="loading" class="loading">
      <el-skeleton :rows="4" animated />
    </div>

    <el-table v-if="!loading" :data="rooms" border stripe>
      <el-table-column label="封面" width="120">
        <template #default="{ row }">
          <img :src="row.cover || fallbackCover(row)" class="room-cover" />
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" min-width="160" />
      <el-table-column prop="address" label="地址" min-width="160" show-overflow-tooltip />
      <el-table-column label="价格" width="100">
        <template #default="{ row }">¥{{ row.price }}/晚</template>
      </el-table-column>
      <el-table-column label="押金" width="100">
        <template #default="{ row }">¥{{ row.deposit || 0 }}</template>
      </el-table-column>
      <el-table-column label="状态" width="150">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">{{ getStatusName(row.status) }}</el-tag>
          <el-tooltip v-if="row.status === 4 && row.adminRemark" :content="row.adminRemark" placement="top">
            <el-tag size="small" type="danger" effect="plain" class="reason-tag" @click="showRejectReason(row)">📄 驳回理由</el-tag>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="320" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
          <el-button size="small" type="info" @click="openCalendar(row)">房态日历</el-button>
          <el-button v-if="row.status === 1" size="small" type="warning" @click="toggleStatus(row, 3)">下架</el-button>
          <el-button v-else-if="row.status === 3" size="small" type="success" @click="toggleStatus(row, 1)">上架</el-button>
          <el-button v-else-if="row.status === 4" size="small" type="success" @click="toggleStatus(row, 0)">重新提交审核</el-button>
          <el-button size="small" type="danger" plain @click="removeRoom(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑房源' : '发布房源'" width="650px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="form.title" placeholder="房源标题" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="4" placeholder="房源描述、配置、周边等信息" />
        </el-form-item>
        <el-form-item label="价格" required>
          <el-input-number v-model="form.price" :min="0" :precision="2" style="width: 200px" />
          <span class="form-suffix">元/晚</span>
        </el-form-item>
        <el-form-item label="押金">
          <el-input-number v-model="form.deposit" :min="0" :precision="2" style="width: 200px" />
          <span class="form-suffix">元</span>
        </el-form-item>
        <el-form-item label="地址" required>
          <el-input v-model="form.address" placeholder="详细地址" />
          <el-button link type="primary" size="small" style="margin-left:8px;" @click="mapDialogVisible = true">
            🗺️ 地图选点
          </el-button>
        </el-form-item>
        <el-form-item label="封面图">
          <el-upload
            action="/api/upload/image"
            :headers="{ Authorization: token }"
            :show-file-list="false"
            :on-success="handleCoverUpload"
            :before-upload="(f) => f.type.startsWith('image/')"
          >
            <img v-if="form.cover" :src="form.cover" class="cover-preview" />
            <el-button v-else><el-icon><Plus /></el-icon> 上传封面</el-button>
          </el-upload>
          <el-input v-if="form.cover" v-model="form.cover" placeholder="或直接输入图片URL" size="small" style="margin-top:6px" />
        </el-form-item>
        <el-form-item label="详情图片">
          <el-upload
            action="/api/upload/image"
            :headers="{ Authorization: token }"
            list-type="picture-card"
            :on-success="handleDetailUpload"
            :on-remove="handleDetailRemove"
            :before-upload="(f) => f.type.startsWith('image/')"
            :file-list="detailFileList"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="form.tags" placeholder="逗号分隔，如：近地铁,精装修" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="mapDialogVisible" title="地图选点（点击地图选择位置）" width="580px" :close-on-click-modal="false">
      <AmapPicker @select="handleMapSelect" />
    </el-dialog>

    <!-- 房态日历弹窗 -->
    <el-dialog v-model="calendarVisible" :title="`📅 ${calendarRoom?.title || ''} 房态日历`" width="880px" destroy-on-close>
      <RoomCalendar v-if="calendarRoom" :room-id="calendarRoom.id" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import AmapPicker from '@/components/AmapPicker.vue'
import RoomCalendar from '@/components/RoomCalendar.vue'
import { getMyRooms, addRoom, updateRoom, changeRoomStatus, deleteRoom } from '@/api/room'

const token = localStorage.getItem('token') || ''
const loading = ref(false)
const rooms = ref([])
const dialogVisible = ref(false)
const mapDialogVisible = ref(false)
const submitting = ref(false)
const detailFileList = ref([])
const uploadedDetailImages = ref([])

// 房态日历
const calendarVisible = ref(false)
const calendarRoom = ref(null)
const openCalendar = (row) => {
  calendarRoom.value = row
  calendarVisible.value = true
}

const emptyForm = {
  id: null,
  title: '',
  description: '',
  price: 0,
  deposit: 0,
  address: '',
  longitude: null,
  latitude: null,
  cover: '',
  detailImages: '',
  tags: ''
}
const form = reactive({ ...emptyForm })

const getStatusType = (status) => {
  const map = { '0': 'warning', '1': 'success', '2': 'info', '3': 'info', '4': 'danger' }
  return map[String(status)] || 'default'
}

const getStatusName = (status) => {
  const map = { '0': '待审核', '1': '已上架', '2': '已租出', '3': '已下架', '4': '已驳回' }
  return map[String(status)] || '未知'
}

const fallbackCover = (row) => `https://loremflickr.com/300/200/house?random=${row.id}`

// 查看驳回理由
const showRejectReason = (row) => {
  ElMessageBox.alert(row.adminRemark || '暂无驳回理由', `「${row.title}」被驳回的原因`, {
    confirmButtonText: '知道了',
    type: 'warning'
  }).catch(() => {})
}

const loadRooms = async () => {
  loading.value = true
  try {
    const res = await getMyRooms()
    // /room/my 直接返回数组
    rooms.value = Array.isArray(res) ? res : []
  } catch (error) {
    console.error('加载房源失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
}

const openAddDialog = () => {
  Object.assign(form, emptyForm)
  detailFileList.value = []
  uploadedDetailImages.value = []
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  Object.assign(form, {
    id: row.id,
    title: row.title,
    description: row.description || '',
    price: row.price,
    deposit: row.deposit || 0,
    address: row.address,
    longitude: row.longitude || null,
    latitude: row.latitude || null,
    cover: row.cover || '',
    detailImages: row.detailImages || '',
    tags: row.tags || ''
  })
  // 回显已有详情图片
  detailFileList.value = []
  uploadedDetailImages.value = []
  if (row.detailImages) {
    const imgs = row.detailImages.split(',').filter(Boolean)
    uploadedDetailImages.value = imgs
    detailFileList.value = imgs.map((url, idx) => ({ uid: idx, name: `image-${idx}`, url, status: 'success' }))
  }
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!form.title.trim()) { ElMessage.warning('请输入房源标题'); return }
  if (!form.address.trim()) { ElMessage.warning('请输入房源地址'); return }
  if (form.price == null || form.price <= 0) { ElMessage.warning('请输入正确的价格'); return }

  submitting.value = true
  try {
    const payload = {
      id: form.id,
      title: form.title,
      description: form.description,
      price: form.price,
      deposit: form.deposit,
      address: form.address,
      longitude: form.longitude,
      latitude: form.latitude,
      cover: form.cover,
      detailImages: uploadedDetailImages.value.join(','),
      tags: form.tags
    }
    let res
    if (form.id) {
      res = await updateRoom(payload)
    } else {
      res = await addRoom({
        title: form.title,
        price: form.price,
        deposit: form.deposit,
        address: form.address,
        cover: form.cover,
        tags: form.tags
      })
    }
    const message = typeof res === 'string' ? res : (res?.message || '操作成功')
    if (typeof res === 'string' && res.includes('失败')) {
      ElMessage.error(message)
    } else {
      ElMessage.success(message)
      dialogVisible.value = false
      loadRooms()
    }
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    submitting.value = false
  }
}

const toggleStatus = (row, target) => {
  const action = target === 1 ? '上架' : (target === 3 ? '下架' : '重新提交审核')
  ElMessageBox.confirm(`确定要${action}「${row.title}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await changeRoomStatus(row.id, target)
      const message = typeof res === 'string' ? res : (res?.message || '操作成功')
      if (typeof res === 'string' && res.includes('失败')) {
        ElMessage.error(message)
      } else {
        ElMessage.success(message)
        loadRooms()
      }
    } catch (error) {
      ElMessage.error('操作失败')
    }
  }).catch(() => {})
}

// 删除房源（软删除，仅本人房源可删；存在进行中订单时后端会拒绝）
const removeRoom = (row) => {
  ElMessageBox.confirm(
    `确定要删除「${row.title}」吗？删除后房源将下架并从所有列表隐藏，该操作不可恢复。`,
    '删除房源',
    {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger'
    }
  ).then(async () => {
    try {
      const res = await deleteRoom(row.id)
      const message = typeof res === 'string' ? res : (res?.message || '操作成功')
      if (typeof res === 'string' && res.includes('失败')) {
        ElMessage.error(message)
      } else if (res && res.code === 200) {
        ElMessage.success(message)
        loadRooms()
      } else {
        ElMessage.error(message)
      }
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// 封面图上传成功
const handleCoverUpload = (res) => {
  if (res.code === 200) {
    form.cover = res.data
    ElMessage.success('封面上传成功')
  } else { ElMessage.error(res.message || '上传失败') }
}

// 详情图上传成功
const handleDetailUpload = (res) => {
  if (res.code === 200) {
    uploadedDetailImages.value.push(res.data)
  } else { ElMessage.error(res.message || '上传失败') }
}

// 删除详情图
const handleDetailRemove = (file) => {
  const url = file.response?.data || file.url
  const idx = uploadedDetailImages.value.indexOf(url)
  if (idx > -1) uploadedDetailImages.value.splice(idx, 1)
}

// 地图选点回填
const handleMapSelect = (loc) => {
  form.address = loc.address
  form.longitude = loc.lng
  form.latitude = loc.lat
  mapDialogVisible.value = false
  ElMessage.success('已选点，请确认地址信息')
}

onMounted(() => {
  loadRooms()
})
</script>

<style scoped>
.rooms-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0;
}

.loading {
  padding: 20px 0;
}

.room-cover {
  width: 80px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
}

.form-suffix {
  margin-left: 8px;
  color: #909399;
}
.cover-preview {
  width: 160px;
  height: 100px;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
}

.reason-tag {
  margin-left: 6px;
  cursor: pointer;
}
</style>