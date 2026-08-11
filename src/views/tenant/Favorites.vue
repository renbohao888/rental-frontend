<template>
  <div class="favorites-page">
    <h2>❤️ 我的收藏</h2>
    <el-row :gutter="20">
      <el-col :span="6" v-for="item in favorites" :key="item.id">
        <el-card :body-style="{ padding: '12px' }">
          <img :src="item.roomCover || 'https://loremflickr.com/300/200/house?random='+item.roomId" class="room-cover" />
          <div class="room-title">{{ item.roomTitle }}</div>
          <div class="room-address">{{ item.roomAddress }}</div>
          <el-button type="danger" size="small" @click="cancelFavorite(item.roomId)">取消收藏</el-button>
        </el-card>
      </el-col>
    </el-row>
    <el-empty v-if="favorites.length === 0" description="暂无收藏房源" />
    <div class="pagination">
      <el-pagination
        v-model:page-num="pageNum"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="loadFavorites"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const favorites = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(8)

const loadFavorites = async () => {
  try {
    const res = await request({
      url: '/favorite/my',
      method: 'get',
      params: { pageNum: pageNum.value, pageSize: pageSize.value }
    })
    if (res.code === 200) {
      favorites.value = res.data.records || []
      total.value = res.data.total || 0
    }
  } catch (error) {
    console.error('加载收藏失败', error)
  }
}

const cancelFavorite = async (roomId) => {
  try {
    const res = await request({
      url: '/favorite/cancel',
      method: 'post',
      data: { roomId }
    })
    if (res.code === 200) {
      ElMessage.success('取消收藏成功')
      loadFavorites()
    }
  } catch (error) {
    console.error('取消收藏失败', error)
  }
}

onMounted(loadFavorites)
</script>

<style scoped>
.favorites-page { max-width: 1200px; margin: 0 auto; padding: 20px; }
.room-cover { width: 100%; height: 180px; object-fit: cover; border-radius: 4px; }
.room-title { font-size: 16px; font-weight: bold; margin: 8px 0; }
.room-address { color: #888; font-size: 13px; }
.pagination { display: flex; justify-content: center; padding: 20px 0; }
</style>