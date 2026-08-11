<template>
  <div class="repairs-page">
    <h2>🔧 报修管理</h2>
    <el-button type="primary" @click="showSubmit = true">提交报修</el-button>
    
    <!-- 报修列表 -->
    <div v-for="item in repairs" :key="item.id" class="repair-item">
      <el-card>
        <div class="repair-header">
          <span class="title">{{ item.title }}</span>
          <el-tag :type="statusTag(item.status)">{{ statusText(item.status) }}</el-tag>
        </div>
        <div class="repair-desc">{{ item.description }}</div>
        <div v-if="item.images" class="repair-images">
          <img v-for="url in item.images.split(',')" :key="url" :src="url" style="width:100px;height:80px;object-fit:cover;margin-right:8px;" />
        </div>
        <div v-if="item.handlerRemark" class="repair-reply">
          <span class="reply-label">处理备注：</span>{{ item.handlerRemark }}
        </div>
        <span class="time">{{ item.createTime?.slice(0,10) }}</span>
      </el-card>
    </div>
    <el-empty v-if="repairs.length === 0" description="暂无报修" />
    <div class="pagination">
      <el-pagination
        v-model:page-num="pageNum"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="loadRepairs"
      />
    </div>

    <!-- 提交报修弹窗 -->
    <el-dialog v-model="showSubmit" title="提交报修" width="500px">
      <el-form :model="repairForm" label-width="80px">
        <el-form-item label="房源ID">
          <el-input v-model="repairForm.roomId" type="number" />
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="repairForm.title" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="repairForm.description" type="textarea" rows="4" />
        </el-form-item>
        <el-form-item label="图片">
          <el-upload
            action="/api/repair/upload"
            :headers="{ Authorization: 'Bearer ' + token }"
            list-type="picture-card"
            :on-success="handleUploadSuccess"
            :on-remove="handleRemove"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSubmit = false">取消</el-button>
        <el-button type="primary" @click="submitRepair">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import request from '@/utils/request'

const token = localStorage.getItem('token') || ''
const repairs = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(8)
const showSubmit = ref(false)
const repairForm = ref({ roomId: '', title: '', description: '' })
const uploadedImages = ref([])

const statusMap = { 0: '待处理', 1: '处理中', 2: '已完成', 3: '已关闭' }
const statusTag = (s) => ({ 0: 'warning', 1: 'primary', 2: 'success', 3: 'info' }[s] || 'info')
const statusText = (s) => statusMap[s] || '未知'

const loadRepairs = async () => {
  try {
    const res = await request({
      url: '/repair/my',
      method: 'get',
      params: { pageNum: pageNum.value, pageSize: pageSize.value }
    })
    if (res.code === 200) {
      repairs.value = res.data.records || []
      total.value = res.data.total || 0
    }
  } catch (error) {
    console.error('加载报修失败', error)
  }
}

const handleUploadSuccess = (res) => {
  if (res.code === 200) {
    uploadedImages.value.push(res.data)
    ElMessage.success('图片上传成功')
  }
}
const handleRemove = (file) => {
  const idx = uploadedImages.value.indexOf(file.url)
  if (idx > -1) uploadedImages.value.splice(idx, 1)
}

const submitRepair = async () => {
  try {
    const data = {
      roomId: repairForm.value.roomId,
      title: repairForm.value.title,
      description: repairForm.value.description,
      images: uploadedImages.value.join(',')
    }
    const res = await request({
      url: '/repair/submit',
      method: 'post',
      data
    })
    if (res.code === 200) {
      ElMessage.success('报修提交成功')
      showSubmit.value = false
      repairForm.value = { roomId: '', title: '', description: '' }
      uploadedImages.value = []
      loadRepairs()
    } else {
      ElMessage.error(res.message)
    }
  } catch (error) {
    console.error('提交报修失败', error)
  }
}

onMounted(loadRepairs)
</script>

<style scoped>
.repairs-page { max-width: 800px; margin: 0 auto; padding: 20px; }
.repair-item { margin-bottom: 16px; }
.repair-header { display: flex; justify-content: space-between; align-items: center; }
.title { font-weight: bold; font-size: 16px; }
.repair-desc { margin: 10px 0; }
.repair-images { margin: 10px 0; }
.repair-reply { background: var(--bg-soft); padding: 10px; border-radius: 4px; }
.reply-label { color: #409eff; }
.time { color: #999; font-size: 13px; display: block; margin-top: 8px; }
.pagination { display: flex; justify-content: center; padding: 20px 0; }
</style>