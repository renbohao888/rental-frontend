<template>
  <div class="page-container">
    <el-card class="header-card">
      <h2>📢 公告管理</h2>
      <p>发布平台公告、活动通知与重要通知</p>
    </el-card>

    <el-card>
      <div class="toolbar">
        <el-input v-model="query.title" placeholder="搜索公告标题" clearable style="width: 220px" @keyup.enter="reload" @clear="reload" />
        <el-select v-model="query.status" placeholder="发布状态" clearable style="width: 140px" @change="reload">
          <el-option label="草稿" :value="0" />
          <el-option label="已发布" :value="1" />
        </el-select>
        <el-select v-model="query.type" placeholder="公告类型" clearable style="width: 140px" @change="reload">
          <el-option label="系统公告" :value="0" />
          <el-option label="活动通知" :value="1" />
          <el-option label="重要通知" :value="2" />
        </el-select>
        <el-button type="primary" @click="reload">查询</el-button>
        <el-button type="success" @click="openAdd">＋ 发布公告</el-button>
      </div>

      <el-table v-loading="loading" :data="notices" border stripe style="width: 100%">
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.type)">{{ getTypeName(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="置顶" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.isTop === 1" type="danger" size="small">置顶</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'">{{ row.status === 1 ? '已发布' : '草稿' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="发布时间" width="165">
          <template #default="{ row }">{{ formatTime(row.publishTime || row.createTime) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" :type="row.status === 1 ? 'warning' : 'success'" @click="togglePublish(row)">
              {{ row.status === 1 ? '撤回' : '发布' }}
            </el-button>
            <el-button size="small" type="danger" @click="doDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination" v-if="total > 0">
        <el-pagination
          v-model:page-num="pageNum"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadNotices"
        />
      </div>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑公告' : '发布公告'" width="620px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="form.title" placeholder="公告标题" maxlength="60" show-word-limit />
        </el-form-item>
        <el-form-item label="类型" required>
          <el-radio-group v-model="form.type">
            <el-radio :label="0">系统公告</el-radio>
            <el-radio :label="1">活动通知</el-radio>
            <el-radio :label="2">重要通知</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input v-model="form.content" type="textarea" :rows="8" placeholder="公告详细内容" />
        </el-form-item>
        <el-form-item label="置顶">
          <el-switch v-model="form.isTop" :active-value="1" :inactive-value="0" active-text="是" inactive-text="否" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio :label="0">草稿</el-radio>
            <el-radio :label="1">立即发布</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>


<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAdminNoticeList, addNotice, updateNotice, deleteNotice } from '@/api/notice'

const loading = ref(false)
const submitting = ref(false)
const notices = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(10)
const query = reactive({ title: '', status: null, type: null })
const dialogVisible = ref(false)

const emptyForm = { id: null, title: '', content: '', type: 0, isTop: 0, status: 1 }
const form = reactive({ ...emptyForm })

const getTypeName = (type) => {
  const map = { '0': '系统公告', '1': '活动通知', '2': '重要通知' }
  return map[String(type)] || '未知'
}

const getTypeTag = (type) => {
  const map = { '0': 'primary', '1': 'success', '2': 'danger' }
  return map[String(type)] || 'info'
}

const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString()
}

const loadNotices = async () => {
  loading.value = true
  try {
    const params = { pageNum: pageNum.value, pageSize: pageSize.value }
    if (query.title) params.title = query.title
    if (query.status !== null && query.status !== '') params.status = query.status
    if (query.type !== null && query.type !== '') params.type = query.type
    const res = await getAdminNoticeList(params)
    if (res.code === 200) {
      notices.value = res.data?.records || []
      total.value = res.data?.total || 0
    } else {
      ElMessage.error(res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载公告失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
}

const reload = () => {
  pageNum.value = 1
  loadNotices()
}

const openAdd = () => {
  Object.assign(form, emptyForm)
  dialogVisible.value = true
}

const openEdit = (row) => {
  Object.assign(form, {
    id: row.id,
    title: row.title,
    content: row.content,
    type: row.type,
    isTop: row.isTop,
    status: row.status
  })
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!form.title.trim()) { ElMessage.warning('请输入公告标题'); return }
  if (!form.content.trim()) { ElMessage.warning('请输入公告内容'); return }
  submitting.value = true
  try {
    const payload = {
      id: form.id,
      title: form.title.trim(),
      content: form.content.trim(),
      type: form.type,
      isTop: form.isTop,
      status: form.status
    }
    const res = form.id ? await updateNotice(payload) : await addNotice(payload)
    if (res.code === 200) {
      ElMessage.success(res.message || '保存成功')
      dialogVisible.value = false
      loadNotices()
    } else {
      ElMessage.error(res.message || '保存失败')
    }
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    submitting.value = false
  }
}

const togglePublish = (row) => {
  const target = row.status === 1 ? 0 : 1
  const action = target === 1 ? '发布' : '撤回'
  ElMessageBox.confirm(`确定要${action}「${row.title}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await updateNotice({ id: row.id, status: target })
      if (res.code === 200) {
        ElMessage.success(res.message || `${action}成功`)
        loadNotices()
      } else {
        ElMessage.error(res.message || '操作失败')
      }
    } catch (error) {
      ElMessage.error('操作失败')
    }
  }).catch(() => {})
}

const doDelete = (row) => {
  ElMessageBox.confirm(`确定要删除公告「${row.title}」吗？`, '警告', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await deleteNotice(row.id)
      if (res.code === 200) {
        ElMessage.success(res.message || '删除成功')
        loadNotices()
      } else {
        ElMessage.error(res.message || '删除失败')
      }
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

onMounted(loadNotices)
</script>

<style scoped>
.page-container { animation: slideUp 0.3s ease; }
.header-card { margin-bottom: 20px; }
.header-card h2 { margin: 0 0 8px; }
.header-card p { margin: 0; color: #999; font-size: 13px; }
.toolbar { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 16px; }
.toolbar .el-button:last-child { margin-left: auto; }
.pagination { display: flex; justify-content: center; padding: 20px 0; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>
