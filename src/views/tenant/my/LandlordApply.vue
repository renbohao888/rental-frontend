<template>
  <div class="landlord-apply-page">
    <div class="page-header">
      <h2>🏘️ 房东入驻申请</h2>
      <p>提交资质审核，审核通过后即可成为房东发布房源</p>
    </div>

    <!-- 已有申请记录 -->
    <el-card v-if="application && !editing" class="status-card">
      <div class="status-header">
        <span class="status-label">申请状态：</span>
        <el-tag :type="statusTypeMap[application.status]" size="large">
          {{ statusTextMap[application.status] }}
        </el-tag>
      </div>
      <div class="status-detail" v-if="application.status === 1">
        <el-alert title="恭喜！您的房东资质已审核通过" type="success" :closable="false" show-icon>
          <template #default>
            <p>您现在已升级为房东身份，可<a href="/landlord/dashboard" style="color: #409eff;">前往房东后台</a>发布房源。</p>
            <p style="color: #999; font-size: 12px;">（请退出后重新登录，或刷新页面以获取房东菜单权限）</p>
          </template>
        </el-alert>
      </div>
      <div class="status-detail" v-if="application.status === 2">
        <el-alert :title="'审核未通过：' + (application.auditRemark || '请重新提交')" type="error" :closable="false" show-icon />
        <el-button type="primary" style="margin-top: 16px;" @click="editing = true">重新申请</el-button>
      </div>
      <div class="status-detail" v-if="application.status === 0">
        <el-alert title="您的申请正在审核中，请耐心等待..." type="warning" :closable="false" show-icon />
      </div>
      <div class="app-info" v-if="application">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="真实姓名">{{ application.realName }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ application.phone }}</el-descriptions-item>
          <el-descriptions-item label="身份证号">{{ maskIdCard(application.idCard) }}</el-descriptions-item>
          <el-descriptions-item label="申请时间">{{ formatDate(application.createTime) }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>

    <!-- 申请表单 -->
    <el-card v-if="!application || editing" class="form-card">
      <h3>{{ editing ? '重新提交申请' : '提交入驻申请' }}</h3>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px" style="max-width: 600px;">
        <el-form-item label="真实姓名" prop="realName">
          <el-input v-model="form.realName" placeholder="请输入真实姓名" maxlength="20" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" maxlength="11" />
        </el-form-item>
        <el-form-item label="身份证号" prop="idCard">
          <el-input v-model="form.idCard" placeholder="请输入18位身份证号" maxlength="18" />
        </el-form-item>
        <el-form-item label="身份证正面" prop="idCardFront">
          <el-upload action="/api/upload/image" :headers="{ Authorization: token }" :show-file-list="false"
            :on-success="(res) => handleUploadSuccess(res, 'idCardFront')" :before-upload="beforeUpload">
            <el-button type="primary" v-if="!form.idCardFront"><el-icon><Upload /></el-icon> 上传身份证正面</el-button>
            <img v-else :src="form.idCardFront" class="upload-preview" />
          </el-upload>
        </el-form-item>
        <el-form-item label="身份证反面" prop="idCardBack">
          <el-upload action="/api/upload/image" :headers="{ Authorization: token }" :show-file-list="false"
            :on-success="(res) => handleUploadSuccess(res, 'idCardBack')" :before-upload="beforeUpload">
            <el-button type="primary" v-if="!form.idCardBack"><el-icon><Upload /></el-icon> 上传身份证反面</el-button>
            <img v-else :src="form.idCardBack" class="upload-preview" />
          </el-upload>
        </el-form-item>
        <el-form-item label="营业执照">
          <el-upload action="/api/upload/image" :headers="{ Authorization: token }" :show-file-list="false"
            :on-success="(res) => handleUploadSuccess(res, 'businessLicense')" :before-upload="beforeUpload">
            <el-button v-if="!form.businessLicense"><el-icon><Upload /></el-icon> 上传营业执照（选填）</el-button>
            <img v-else :src="form.businessLicense" class="upload-preview" />
          </el-upload>
          <div style="font-size: 12px; color: #999; margin-top: 4px;">个人房东可不传营业执照</div>
        </el-form-item>
        <el-form-item label="申请备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="补充说明（选填）" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">提交申请</el-button>
          <el-button v-if="editing" @click="editing = false">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import request from '@/utils/request'

const token = localStorage.getItem('token') || ''
const application = ref(null)
const editing = ref(false)
const submitting = ref(false)
const formRef = ref(null)

const form = reactive({
  realName: '',
  phone: '',
  idCard: '',
  idCardFront: '',
  idCardBack: '',
  businessLicense: '',
  remark: ''
})

const statusTypeMap = { 0: 'warning', 1: 'success', 2: 'danger' }
const statusTextMap = { 0: '审核中', 1: '已通过', 2: '已拒绝' }

const rules = {
  realName: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  idCard: [
    { required: true, message: '请输入身份证号', trigger: 'blur' },
    { pattern: /^\d{17}[\dXx]$/, message: '身份证号格式不正确', trigger: 'blur' }
  ],
  idCardFront: [{ required: true, message: '请上传身份证正面', trigger: 'change' }],
  idCardBack: [{ required: true, message: '请上传身份证反面', trigger: 'change' }]
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString()
}

const maskIdCard = (idCard) => {
  if (!idCard || idCard.length < 8) return idCard
  return idCard.substring(0, 4) + '**********' + idCard.substring(idCard.length - 4)
}

const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) { ElMessage.error('只能上传图片文件'); return false }
  return true
}

const handleUploadSuccess = (res, field) => {
  if (res.code === 200) { form[field] = res.data; ElMessage.success('上传成功') }
  else { ElMessage.error(res.message || '上传失败') }
}

const loadApplication = async () => {
  try {
    const res = await request({ url: '/landlord/application/my', method: 'get' })
    if (res.code === 200 && res.data) { application.value = res.data }
  } catch (error) { console.error('查询申请状态失败', error) }
}

const handleSubmit = async () => {
  try { await formRef.value?.validate() } catch { return }
  submitting.value = true
  try {
    const res = await request({
      url: '/landlord/apply',
      method: 'post',
      data: {
        realName: form.realName, phone: form.phone, idCard: form.idCard,
        idCardFront: form.idCardFront, idCardBack: form.idCardBack,
        businessLicense: form.businessLicense, remark: form.remark
      }
    })
    if (res.code === 200) {
      ElMessage.success('申请已提交，请等待审核')
      editing.value = false; loadApplication()
    } else { ElMessage.error(res.message || '提交失败') }
  } catch (error) { ElMessage.error('提交失败') }
  finally { submitting.value = false }
}

onMounted(() => { loadApplication() })
</script>

<style scoped>
.landlord-apply-page { background: var(--bg-card); padding: 20px; }
.page-header { margin-bottom: 24px; }
.page-header h2 { margin: 0 0 8px; }
.page-header p { margin: 0; color: #999; font-size: 14px; }
.status-card { margin-bottom: 20px; }
.status-header { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.status-label { font-weight: 600; font-size: 16px; }
.status-detail { margin-bottom: 16px; }
.app-info { margin-top: 16px; }
.form-card h3 { margin: 0 0 20px; }
.upload-preview { width: 150px; height: 100px; object-fit: cover; border-radius: 6px; border: 1px solid #e0e0e0; }
@media (max-width: 768px) { .landlord-apply-page { padding: 12px; } }
</style>