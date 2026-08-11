<template>
  <div class="page-container">
    <el-card class="header-card">
      <h2>🖼️ 轮播图管理</h2>
      <p>管理首页轮播图，支持新增、编辑与上下架</p>
      <el-button type="primary" size="small" class="add-btn" @click="openDialog()">＋ 新增轮播图</el-button>
    </el-card>

    <el-card>
      <el-empty v-if="list.length === 0 && !loading" description="暂无轮播图" />

      <el-table v-if="!loading" :data="list" border stripe style="width: 100%">
        <el-table-column label="图片" width="180">
          <template #default="{ row }">
            <el-image :src="row.imageUrl" style="width: 140px; height: 60px; border-radius: 4px; object-fit: cover;" :preview-src-list="[row.imageUrl]" preview-teleported />
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="140" />
        <el-table-column prop="linkUrl" label="跳转链接" min-width="180" show-overflow-tooltip />
        <el-table-column prop="sortOrder" label="排序" width="80" align="center" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'">{{ row.status === 1 ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" min-width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="openDialog(row)">编辑</el-button>
            <el-button type="danger" size="small" plain @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination" v-if="total > 0">
        <el-pagination v-model:page-num="pageNum" v-model:page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="loadList" />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑轮播图' : '新增轮播图'" width="520px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="轮播图" required>
          <el-upload
            class="avatar-uploader"
            action="/api/upload/image"
            :show-file-list="false"
            :headers="{ Authorization: token }"
            :on-success="handleUploadSuccess"
          >
            <img v-if="form.imageUrl" :src="form.imageUrl" class="avatar" />
            <el-icon v-else><Plus /></el-icon>
          </el-upload>
          <div class="tip">建议尺寸 1200×400，点击上传</div>
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="跳转链接">
          <el-input v-model="form.linkUrl" placeholder="选填，点击轮播图跳转的地址" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sortOrder" :min="0" :max="999" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.status" :active-value="1" :inactive-value="0" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import request from '@/utils/request'

const token = localStorage.getItem('token') || ''
const loading = ref(false)
const list = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(10)
const dialogVisible = ref(false)
const submitting = ref(false)

const emptyForm = () => ({ id: null, title: '', imageUrl: '', linkUrl: '', sortOrder: 0, status: 1 })
const form = reactive(emptyForm())

const loadList = async () => {
  loading.value = true
  try {
    const res = await request({ url: '/banner/admin/list', method: 'get', params: { pageNum: pageNum.value, pageSize: pageSize.value } })
    if (res.code === 200) {
      list.value = res.data?.records || []
      total.value = res.data?.total || 0
    } else {
      ElMessage.error(res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载轮播图失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
}

const openDialog = (row) => {
  Object.assign(form, emptyForm(), row ? { id: row.id, title: row.title, imageUrl: row.imageUrl, linkUrl: row.linkUrl, sortOrder: row.sortOrder, status: row.status } : {})
  dialogVisible.value = true
}

const handleUploadSuccess = (res) => {
  if (res.code === 200) {
    form.imageUrl = res.data
    ElMessage.success('图片上传成功')
  } else {
    ElMessage.error(res.message || '上传失败')
  }
}

const submit = async () => {
  if (!form.imageUrl) {
    ElMessage.warning('请先上传轮播图')
    return
  }
  submitting.value = true
  try {
    const url = form.id ? '/banner/admin/update' : '/banner/admin/add'
    const res = await request({ url, method: form.id ? 'put' : 'post', data: { ...form } })
    if (res.code === 200) {
      ElMessage.success(res.message || '保存成功')
      dialogVisible.value = false
      loadList()
    } else {
      ElMessage.error(res.message || '保存失败')
    }
  } catch (error) {
    ElMessage.error('网络请求失败')
  } finally {
    submitting.value = false
  }
}

const remove = (row) => {
  ElMessageBox.confirm(`确定要删除轮播图「${row.title || row.imageUrl}」吗？`, '提示', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await request({ url: `/banner/admin/${row.id}`, method: 'delete' })
      if (res.code === 200) {
        ElMessage.success('删除成功')
        loadList()
      } else {
        ElMessage.error(res.message || '删除失败')
      }
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

onMounted(loadList)
</script>

<style scoped>
.page-container { animation: slideUp 0.3s ease; }
.header-card { margin-bottom: 20px; position: relative; }
.header-card h2 { margin: 0 0 8px; }
.header-card p { margin: 0; color: #999; font-size: 13px; }
.add-btn { position: absolute; right: 20px; top: 20px; }
.pagination { display: flex; justify-content: center; padding: 20px 0; }
.avatar-uploader :deep(.el-upload) { border: 1px dashed #d9d9d9; border-radius: 6px; cursor: pointer; width: 240px; height: 90px; display: flex; align-items: center; justify-content: center; overflow: hidden; }
.avatar-uploader :deep(.el-upload:hover) { border-color: #409eff; }
.avatar { width: 240px; height: 90px; object-fit: cover; }
.tip { font-size: 12px; color: #999; margin-top: 6px; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>