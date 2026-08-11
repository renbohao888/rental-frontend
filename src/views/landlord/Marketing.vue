<template>
  <div class="page">
    <el-card class="header">
      <h2>🎯 营销推广</h2>
      <p style="color: #999; margin: 8px 0 0;">房源推广、优惠券、广告投放等营销工具</p>
    </el-card>

    <el-row :gutter="20">
      <el-col :xs="24" :md="12">
        <el-card title="🎨 推广工具">
          <div class="tool-grid">
            <el-button @click="launchPromotion">发布推广文案</el-button>
            <el-button @click="createCoupon">创建优惠券</el-button>
            <el-button @click="manageStar">申请星级房源</el-button>
            <el-button @click="runAds">投放广告</el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card title="📊 推广效果">
          <el-table :data="promoStats" size="small">
            <el-table-column prop="name" label="推广名称" />
            <el-table-column prop="views" label="浏览数" />
            <el-table-column prop="clicks" label="点击数" />
            <el-table-column prop="conversions" label="转化数" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const promoStats = ref([
  { name: '秋季特惠', views: 1200, clicks: 256, conversions: 28 },
  { name: '家电优惠券', views: 890, clicks: 178, conversions: 15 },
])

const launchPromotion = () => ElMessage.success('推广已发布')
const createCoupon = () => ElMessage.success('优惠券已创建')
const manageStar = () => ElMessage.success('申请已提交')
const runAds = () => ElMessage.success('广告投放已启动')
</script>

<style scoped>
.header {
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
}

.tool-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

@media (max-width: 768px) {
  .tool-grid {
    grid-template-columns: 1fr;
  }
}
</style>
