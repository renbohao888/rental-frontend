<!-- 房东 - 合同管理 -->
<template>
  <div class="page-wrapper">
    <el-card class="header-section">
      <div class="flex-between">
        <h2>📝 合同管理</h2>
        <el-button type="primary" @click="showAddDialog = true">➕ 新增合同</el-button>
      </div>
    </el-card>

    <el-card>
      <el-table :data="contracts" stripe style="width: 100%">
        <el-table-column prop="contractNo" label="合同号" width="150" />
        <el-table-column prop="tenant" label="租客" width="120" />
        <el-table-column prop="room" label="房源" width="150" />
        <el-table-column prop="startDate" label="开始日期" width="120" />
        <el-table-column prop="endDate" label="结束日期" width="120" />
        <el-table-column prop="rentAmount" label="租金" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '进行中' ? 'success' : 'danger'">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewContract(row.id)">查看</el-button>
            <el-button type="info" size="small" @click="downloadContract(row.id)">下载</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增合同对话框 -->
    <el-dialog v-model="showAddDialog" title="新增合同" width="50%">
      <el-form :model="contractForm" label-width="100px">
        <el-form-item label="租客">
          <el-select v-model="contractForm.tenant" placeholder="选择租客">
            <el-option label="张三" value="1" />
            <el-option label="李四" value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="房源">
          <el-select v-model="contractForm.room" placeholder="选择房源">
            <el-option label="温馨大床房" value="1" />
            <el-option label="豪华套房" value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker v-model="contractForm.startDate" type="date" />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker v-model="contractForm.endDate" type="date" />
        </el-form-item>
        <el-form-item label="租金">
          <el-input-number v-model="contractForm.rentAmount" :step="100" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="submitContract">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const showAddDialog = ref(false)
const contracts = ref([
  { id: 1, contractNo: 'CT-2026-001', tenant: '张三', room: '温馨大床房', startDate: '2026-08-01', endDate: '2026-11-01', rentAmount: 3000, status: '进行中' },
  { id: 2, contractNo: 'CT-2026-002', tenant: '李四', room: '豪华套房', startDate: '2026-07-15', endDate: '2026-10-15', rentAmount: 5000, status: '已完成' },
])

const contractForm = ref({
  tenant: '',
  room: '',
  startDate: '',
  endDate: '',
  rentAmount: 0
})

const viewContract = (id) => {
  ElMessage.info('查看合同详情')
}

const downloadContract = (id) => {
  ElMessage.success('合同已下载')
}

const submitContract = () => {
  ElMessage.success('合同已添加')
  showAddDialog.value = false
}
</script>

<style scoped>
.page-wrapper {
  animation: fadeIn 0.3s;
}

.header-section {
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.flex-between h2 {
  margin: 0;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
