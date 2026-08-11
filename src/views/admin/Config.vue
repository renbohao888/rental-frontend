<template>
  <div class="page-container">
    <el-card class="header-card">
      <h2>⚙️ 平台配置</h2>
      <p>管理系统参数与平台设置</p>
      <el-button type="primary" size="small" class="add-btn" @click="openDialog()">＋ 新增配置</el-button>
    </el-card>

    <el-card>
      <div class="toolbar">
        <el-input v-model="keyword" placeholder="搜索配置键" clearable style="width: 220px" @change="reload" />
      </div>

      <el-empty v-if="list.length === 0 && !loading" description="暂无配置" />

      <el-table v-if="!loading" :data="list" border stripe style="width: 100%">
        <el-table-column prop="configKey" label="配置键" min-width="200" />
        <el-table-column prop="configValue" label="配置值" min-width="200" show-overflow-tooltip />
        <el-table-column prop="configType" label="类型" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.configType || '通用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="说明" min-width="200" show-overflow-tooltip />
        <el-table-column prop="updateTime" label="更新时间" min-width="160" />
        <el-table-column label="操作" width="160" fixed="right">
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑配置' : '新增配置'" width="520px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="配置键" required>
          <el-input v-model="form.configKey" placeholder="如 platform_name、customer_service_phone" :disabled="!!form.id" />
        </el-form-item>
        <el-form-item label="配置值" required>
          <el-input v-model="form.configValue" placeholder="请输入配置值" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.configType" placeholder="选择类型" clearable style="width: 100%">
            <el-option label="文本" value="text" />
            <el-option label="数字" value="number" />
            <el-option label="开关" value="switch" />
          </el-select>
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="配置用途说明（选填）" />
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
import request from '@/utils/request'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(10)
const keyword = ref('')
const dialogVisible = ref(false)
const submitting = ref(false)

const emptyForm = () => ({ id: null, configKey: '', configValue: '', configType: 'text', description: '' })
const form = reactive(emptyForm())

const loadList = async () => {
  loading.value = true
  try {
    const params = { pageNum: pageNum.value, pageSize: pageSize.value }
    if (keyword.value) params.configKey = keyword.value
    const res = await request({ url: '/config/admin/list', method: 'get', params })
    if (res.code === 200) {
      list.value = res.data?.records || []
      total.value = res.data?.total || 0
    } else {
      ElMessage.error(res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载配置失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
}

const reload = () => {
  pageNum.value = 1
  loadList()
}

const openDialog = (row) => {
  Object.assign(form, emptyForm(), row ? { id: row.id, configKey: row.configKey, configValue: row.configValue, configType: row.configType, description: row.description } : {})
  dialogVisible.value = true
}

const submit = async () => {
  if (!form.configKey || !form.configKey.trim()) {
    ElMessage.warning('请输入配置键')
    return
  }
  if (!form.configValue || !form.configValue.trim()) {
    ElMessage.warning('请输入配置值')
    return
  }
  submitting.value = true
  try {
    const url = form.id ? '/config/admin/update' : '/config/admin/add'
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
  ElMessageBox.confirm(`确定要删除配置「${row.configKey}」吗？`, '提示', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await request({ url: `/config/admin/${row.id}`, method: 'delete' })
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
.toolbar { margin-bottom: 16px; }
.pagination { display: flex; justify-content: center; padding: 20px 0; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>