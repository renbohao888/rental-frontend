<template>
  <div class="room-audit-page">
    <div class="page-header">
      <h2>✅ 房源审核</h2>
      <el-button size="small" @click="loadRooms"><el-icon><Refresh /></el-icon>&nbsp;刷新</el-button>
    </div>

    <el-empty v-if="rooms.length === 0 && !loading" description="暂无待审核房源" />

    <div v-if="loading" class="loading">
      <el-skeleton :rows="4" animated />
    </div>

    <el-table v-if="!loading" :data="rooms" border stripe>
      <el-table-column label="封面" width="110">
        <template #default="{ row }">
          <el-image :src="row.cover || fallbackCover(row)" class="room-cover" :preview-src-list="[row.cover || fallbackCover(row)]" preview-teleported fit="cover" />
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" min-width="150" show-overflow-tooltip />
      <el-table-column prop="address" label="地址" min-width="150" show-overflow-tooltip />
      <el-table-column label="价格" width="90">
        <template #default="{ row }">¥{{ row.price }}/晚</template>
      </el-table-column>
      <el-table-column label="押金" width="90">
        <template #default="{ row }">¥{{ row.deposit || 0 }}</template>
      </el-table-column>
      <el-table-column prop="landlordId" label="房东ID" width="90" />
      <el-table-column label="提交时间" width="165">
        <template #default="{ row }">{{ formatDate(row.createTime) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="240" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" plain @click="openDetail(row)">查看详情</el-button>
          <el-button size="small" type="success" @click="doAudit(row, 1)">通过</el-button>
          <el-button size="small" type="danger" @click="doReject(row)">驳回</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination" v-if="total > 0">
      <el-pagination
        v-model:page-num="pageNum"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadRooms"
        @current-change="loadRooms"
      />
    </div>

    <!-- 房源详情弹窗 -->
    <el-dialog v-model="detailVisible" title="🏠 房源详情" width="720px" top="5vh">
      <div v-if="currentRoom" class="detail-wrap" v-loading="detailLoading">
        <el-carousel v-if="detailImages.length" height="260px" class="detail-carousel">
          <el-carousel-item v-for="(img, i) in detailImages" :key="i">
            <el-image :src="img" fit="cover" class="detail-img" :preview-src-list="detailImages" preview-teleported />
          </el-carousel-item>
        </el-carousel>
        <el-image v-else :src="currentRoom.cover || fallbackCover(currentRoom)" class="detail-img single" fit="cover" />

        <el-descriptions :column="2" border class="detail-desc">
          <el-descriptions-item label="标题" :span="2">{{ currentRoom.title }}</el-descriptions-item>
          <el-descriptions-item label="价格">¥{{ currentRoom.price }}/晚</el-descriptions-item>
          <el-descriptions-item label="押金">¥{{ currentRoom.deposit || 0 }}</el-descriptions-item>
          <el-descriptions-item label="地址" :span="2">{{ currentRoom.address }}</el-descriptions-item>
          <el-descriptions-item label="经度">{{ currentRoom.longitude ?? '-' }}</el-descriptions-item>
          <el-descriptions-item label="纬度">{{ currentRoom.latitude ?? '-' }}</el-descriptions-item>
          <el-descriptions-item label="标签" :span="2">
            <el-tag v-for="t in parseTags(currentRoom.tags)" :key="t" size="small" class="tag-item">{{ t }}</el-tag>
            <span v-if="!parseTags(currentRoom.tags).length">-</span>
          </el-descriptions-item>
          <el-descriptions-item label="房东ID">{{ currentRoom.landlordId }}</el-descriptions-item>
          <el-descriptions-item label="提交时间">{{ formatDate(currentRoom.createTime) }}</el-descriptions-item>
          <el-descriptions-item label="房源描述" :span="2">
            <div class="desc-text">{{ currentRoom.description || '暂无描述' }}</div>
          </el-descriptions-item>
          <el-descriptions-item v-if="currentRoom.adminRemark" label="审核意见" :span="2">
            <el-alert type="warning" :closable="false" :title="currentRoom.adminRemark" />
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button v-if="currentRoom && currentRoom.status === 0" type="success" @click="doAudit(currentRoom, 1)">通过上架</el-button>
        <el-button v-if="currentRoom && currentRoom.status === 0" type="danger" @click="doReject(currentRoom)">驳回</el-button>
      </template>
    </el-dialog>
  </div>
</template>


<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { auditRoom, getRoomDetail } from '@/api/room'

const loading = ref(false)
const rooms = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(10)

// 详情弹窗
const detailVisible = ref(false)
const detailLoading = ref(false)
const currentRoom = ref(null)
const detailImages = ref([])

const fallbackCover = (row) => `https://loremflickr.com/300/200/house?random=${row.id}`

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString()
}

const parseTags = (tags) => {
  if (!tags) return []
  if (Array.isArray(tags)) return tags
  return String(tags).split(',').map(t => t.trim()).filter(Boolean)
}

const loadRooms = async () => {
  loading.value = true
  try {
    const res = await request({
      url: '/room/admin/list',
      method: 'get',
      params: { pageNum: pageNum.value, pageSize: pageSize.value, status: 0 }
    })
    if (res.code === 200) {
      rooms.value = res.data?.records || []
      total.value = res.data?.total || 0
    } else {
      ElMessage.error(res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载房源失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
}

// 查看详情：展示完整数据（含详情图、描述）
const openDetail = async (row) => {
  currentRoom.value = row
  detailVisible.value = true
  detailImages.value = parseImages(row.detailImages)
  if (!row.description && !row.detailImages) {
    detailLoading.value = true
    try {
      const res = await getRoomDetail(row.id)
      if (res.code === 200) {
        const full = res.data
        currentRoom.value = { ...row, ...full }
        detailImages.value = parseImages(full.detailImages)
      }
    } catch (e) {
      console.error('加载详情失败', e)
    } finally {
      detailLoading.value = false
    }
  }
}

const parseImages = (str) => {
  if (!str) return []
  return String(str).split(',').map(s => s.trim()).filter(Boolean)
}

const doAudit = (row, status) => {
  const action = status === 1 ? '审核通过并上架' : '驳回'
  ElMessageBox.confirm(`确定要${action}「${row.title}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await auditRoom(row.id, status)
      const message = typeof res === 'string' ? res : (res?.message || '操作成功')
      if (typeof res === 'string' && res.includes('失败')) {
        ElMessage.error(message)
      } else {
        ElMessage.success(message)
        detailVisible.value = false
        loadRooms()
      }
    } catch (error) {
      ElMessage.error('操作失败')
    }
  }).catch(() => {})
}

// 驳回时必须填写驳回理由
const doReject = (row) => {
  ElMessageBox.prompt(`请填写驳回「${row.title}」的理由，房东将根据理由修改后重新提交`, '驳回房源', {
    confirmButtonText: '确定驳回',
    cancelButtonText: '取消',
    inputType: 'textarea',
    inputPlaceholder: '请填写驳回理由（必填）',
    inputValidator: (val) => (val && val.trim().length > 0 ? true : '驳回理由不能为空'),
    type: 'warning'
  }).then(async ({ value }) => {
    try {
      const res = await auditRoom(row.id, 4, value.trim())
      const message = typeof res === 'string' ? res : (res?.message || '操作成功')
      if (typeof res === 'string' && res.includes('失败')) {
        ElMessage.error(message)
      } else {
        ElMessage.success(message)
        detailVisible.value = false
        loadRooms()
      }
    } catch (error) {
      ElMessage.error('操作失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  loadRooms()
})
</script>


<style scoped>
.room-audit-page {
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

.pagination {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.detail-carousel {
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 16px;
}

.detail-img {
  width: 100%;
  height: 100%;
  border-radius: 8px;
}

.detail-img.single {
  height: 240px;
  margin-bottom: 16px;
}

.detail-desc {
  margin-top: 8px;
}

.tag-item {
  margin-right: 6px;
}

.desc-text {
  white-space: pre-wrap;
  line-height: 1.6;
  color: #555;
  max-height: 140px;
  overflow-y: auto;
}
</style>