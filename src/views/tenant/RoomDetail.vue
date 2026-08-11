<template>
  <div class="room-detail-page" v-loading="loading">
    <div v-if="room" class="room-container" v-reveal>
      <!-- 左列：图片 -->
      <div class="room-image">
        <el-image
          :src="currentImage || 'https://loremflickr.com/600/400/house?random=' + room.id"
          fit="cover"
          style="width:100%; height:400px; border-radius: 12px;"
        />
        <div v-if="imageList.length > 1" class="image-thumbs">
          <el-image
            v-for="(img, i) in imageList"
            :key="i"
            :src="img"
            fit="cover"
            class="thumb"
            :class="{ active: currentImage === img }"
            @click="currentImage = img"
          />
        </div>
      </div>

      <!-- 右列：信息 -->
      <div class="room-info">
        <h1 class="room-title">{{ room.title }}</h1>
        <div class="room-address">
          <el-icon><Location /></el-icon>
          {{ room.address }}
        </div>

        <div class="room-tags">
          <el-tag v-for="tag in room.tags?.split(',')" :key="tag" size="large">
            {{ tag }}
          </el-tag>
        </div>

        <div class="room-price">
          <span class="price">¥{{ room.price }}</span>
          <span class="unit">/ 晚</span>
        </div>

        <el-divider />

        <!-- 房东信息 -->
        <div class="landlord-info">
          <el-avatar :size="50" :src="landlord?.avatar || ''" />
          <div class="landlord-detail">
            <div class="name">{{ landlord?.nickname || '房东' }}</div>
            <div class="rating">⭐ {{ room.rating || '暂无评分' }}</div>
          </div>
        </div>

        <el-divider />

        <!-- 预订表单 -->
        <div class="booking-form">
          <h3>📅 选择日期</h3>
          <div class="date-picker">
            <el-date-picker
              v-model="orderForm.checkInDate"
              type="date"
              placeholder="入住日期"
              :disabled-date="disabledCheckIn"
              style="width:180px"
            />
            <span style="margin:0 12px;">至</span>
            <el-date-picker
              v-model="orderForm.checkOutDate"
              type="date"
              placeholder="退租日期"
              :disabled-date="disabledCheckOut"
              style="width:180px"
            />
          </div>

          <div class="price-summary" v-if="orderForm.checkInDate && orderForm.checkOutDate">
            <div class="summary-row">
              <span>¥{{ room.price }} × {{ totalNights }} 晚</span>
              <span>= ¥{{ totalAmount }}</span>
            </div>
            <div class="summary-row">
              <span>押金</span>
              <span>¥{{ room.deposit || 0 }}</span>
            </div>
            <div class="summary-row total">
              <span>总计</span>
              <span>¥{{ totalAmount + (room.deposit || 0) }}</span>
            </div>
          </div>

          <div class="action-buttons">
            <el-button type="primary" size="large" @click="handleBook" :loading="booking">
              立即预订
            </el-button>
            <el-button type="warning" size="large" plain @click="openAppointmentDialog">
              🗓️ 预约看房
            </el-button>
            <el-button type="warning" size="large" plain @click="contactLandlord" v-if="landlord">
              💬 联系房东
            </el-button>
            <el-button
              :type="room.isFavorited ? 'danger' : 'default'"
              size="large"
              @click="toggleFavorite"
            >
              {{ room.isFavorited ? '❤️ 已收藏' : '🤍 收藏' }}
            </el-button>
            <el-button
              v-if="room.longitude && room.latitude"
              size="large"
              plain
              @click="openNavigation"
            >
              📍 地图导航
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 房源描述 -->
    <div v-if="room && room.description" class="description-section" v-reveal="{ delay: 80 }">
      <el-divider />
      <h3>🏠 房源描述</h3>
      <p class="description-text">{{ room.description }}</p>
    </div>

    <!-- 房态日历 -->
    <div v-if="room" class="calendar-section" v-reveal="{ delay: 120 }">
      <el-divider />
      <h3>📅 房态日历</h3>
      <p class="calendar-tip">绿色为空闲日期，黄/红/橙色为已被预订或入住日期，预订请避开这些日期。</p>
      <RoomCalendar :room-id="room.id" />
    </div>

    <!-- 预约看房弹窗 -->
    <el-dialog v-model="appointmentVisible" title="🗓️ 预约看房" width="480px" destroy-on-close>
      <el-alert type="info" :closable="false" show-icon
        title="预约看房需等待房东确认，确认后可前往「我的预约」查看状态。" style="margin-bottom: 16px" />
      <el-form :model="appointmentForm" label-width="90px">
        <el-form-item label="房源">
          <span>{{ room?.title }}</span>
        </el-form-item>
        <el-form-item label="看房日期" required>
          <el-date-picker
            v-model="appointmentForm.date"
            type="date"
            placeholder="选择看房日期"
            :disabled-date="disabledAppointmentDate"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="看房时段" required>
          <el-select v-model="appointmentForm.time" placeholder="选择时间段" style="width: 100%">
            <el-option label="上午（09:00-12:00）" value="上午（09:00-12:00）" />
            <el-option label="下午（14:00-17:00）" value="下午（14:00-17:00）" />
            <el-option label="晚上（18:00-21:00）" value="晚上（18:00-21:00）" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="appointmentForm.remark" type="textarea" :rows="3" placeholder="选填，如：想了解一下周边交通情况" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="appointmentVisible = false">取消</el-button>
        <el-button type="primary" :loading="appointmentSubmitting" @click="handleSubmitAppointment">提交预约</el-button>
      </template>
    </el-dialog>

    <!-- 评论区 -->
    <div v-if="room" class="review-section" v-reveal="{ delay: 100 }">
      <el-divider />
      <h3>💬 房客评价 ({{ room.rating ? '⭐' + room.rating : '暂无评分' }})</h3>
      
      <!-- 评价列表 -->
      <div v-if="reviews.length === 0 && !reviewsLoading" class="no-reviews">
        暂无评价，成为第一个评价的人吧
      </div>
      <div v-for="review in reviews" :key="review.id" class="review-item">
        <div class="review-header">
          <el-avatar :size="36" :src="review.userAvatar || ''" />
          <div class="review-user">
            <span class="review-nick">{{ review.userNickname || '匿名用户' }}</span>
            <span class="review-rating">⭐ {{ review.rating }}</span>
            <span class="review-time">{{ formatDate(review.createTime) }}</span>
          </div>
        </div>
        <div class="review-content">{{ review.content }}</div>
        <div v-if="review.images" class="review-images">
          <el-image
            v-for="(img, idx) in review.images.split(',').filter(Boolean)"
            :key="idx"
            :src="img"
            :preview-src-list="review.images.split(',').filter(Boolean)"
            style="width: 80px; height: 80px; margin-right: 6px; border-radius: 4px; object-fit: cover;"
            fit="cover"
          />
        </div>
        <div v-if="review.replyContent" class="review-reply">
          <span class="reply-tag">房东回复：</span>{{ review.replyContent }}
        </div>
      </div>
      <div v-if="totalReviews > pageSize" class="review-pagination">
        <el-pagination
          v-model:current-page="reviewPage"
          :page-size="pageSize"
          :total="totalReviews"
          layout="prev, pager, next"
          small
          @current-change="loadReviews"
        />
      </div>

      <!-- 写评价（仅已登录租客可写，且不能是房东自己） -->
      <div v-if="userInfo && (userInfo.role === 1 || userInfo.role === 2) && String(room.landlordId) !== String(userInfo.id)" class="write-review">
        <el-divider />
        <h4>✍️ 写评价</h4>
        <el-form :model="reviewForm" :rules="reviewRules" ref="reviewFormRef">
          <el-form-item label="评分" prop="rating">
            <el-rate v-model="reviewForm.rating" :max="5" show-score />
          </el-form-item>
          <el-form-item label="内容" prop="content">
            <el-input v-model="reviewForm.content" type="textarea" :rows="3" placeholder="分享你的入住体验..." />
          </el-form-item>
          <el-form-item label="图片">
            <el-upload
              action="/api/repair/upload"
              :headers="{ Authorization: token }"
              list-type="picture-card"
              :on-success="handleReviewUpload"
              :on-remove="handleReviewRemove"
              :before-upload="(f) => f.type.startsWith('image/')"
              :file-list="reviewFileList"
            >
              <el-icon><Plus /></el-icon>
            </el-upload>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="reviewSubmitting" @click="submitReview">发表评价</el-button>
          </el-form-item>
        </el-form>
      </div>
      <div v-if="userInfo && userInfo.role === 1 && String(room.landlordId) === String(userInfo.id)" class="write-review">
        <el-alert title="您是该房源的房东，不能评价自己的房源" type="info" :closable="false" show-icon />
      </div>
      <div v-if="!userInfo" class="write-review">
        <el-alert title="请先登录后再发表评价" type="info" :closable="false" show-icon />
      </div>
    </div>


    <!-- 空状态 -->
    <el-empty v-if="!room && !loading" description="房源不存在" />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Location } from '@element-plus/icons-vue'
import { getRoomDetail, getRoomCalendar } from '@/api/room'
import { createOrder } from '@/api/order'
import { submitAppointment } from '@/api/appointment'
import RoomCalendar from '@/components/RoomCalendar.vue'
import request from '@/utils/request'
import { buildAmapUri } from '@/utils/amap'

const route = useRoute()
const router = useRouter()
const roomId = route.params.id

const loading = ref(false)
const booking = ref(false)
const room = ref(null)
const landlord = ref(null)

// 图片列表（封面 + 详情图）
const imageList = computed(() => {
  const list = []
  if (room.value?.cover) list.push(room.value.cover)
  if (room.value?.detailImages) {
    room.value.detailImages.split(',').filter(Boolean).forEach((u) => list.push(u))
  }
  return list
})
const currentImage = ref('')

// 用户信息 & token
const token = localStorage.getItem('token') || ''
const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

// 评价列表
const reviews = ref([])
const reviewsLoading = ref(false)
const totalReviews = ref(0)
const reviewPage = ref(1)
const pageSize = ref(10)

// 评价表单
const reviewFormRef = ref(null)
const reviewSubmitting = ref(false)
const reviewFileList = ref([])
const uploadedReviewImages = ref([])
const reviewForm = reactive({
  rating: 5,
  content: ''
})
const reviewRules = {
  rating: [{ required: true, message: '请评分', trigger: 'change' }],
  content: [{ required: true, message: '请输入评价内容', trigger: 'blur' }]
}

// 预订表单
const orderForm = reactive({
  checkInDate: null,
  checkOutDate: null
})

// 预约看房表单
const appointmentVisible = ref(false)
const appointmentSubmitting = ref(false)
const appointmentForm = reactive({
  date: null,
  time: '',
  remark: ''
})

// 房态日历数据：{ 'YYYY-MM-DD': { status, orderNo } }
const calendarMap = ref({})

const loadCalendar = async () => {
  try {
    const res = await getRoomCalendar(roomId)
    if (res.code === 200 && res.data?.days) {
      const map = {}
      res.data.days.forEach((d) => { map[d.date] = d })
      calendarMap.value = map
    }
  } catch (e) {
    console.error('加载房态日历失败', e)
  }
}

// 某日期是否已被占用（已预订/已入住/核算中均不可再预订）
const isDateOccupied = (dayStr) => {
  const info = calendarMap.value[dayStr]
  return !!info && info.status !== 0
}

// 禁用日期：入住日期不能早于今天，且不能是已占用日期
const disabledCheckIn = (time) => {
  if (time.getTime() < Date.now() - 8.64e7) return true
  return isDateOccupied(formatDate(time))
}

// 禁用日期：退租日期不能早于入住日期，且不能是已占用日期
const disabledCheckOut = (time) => {
  if (!orderForm.checkInDate) return time.getTime() < Date.now() - 8.64e7
  if (time.getTime() <= orderForm.checkInDate.getTime()) return true
  return isDateOccupied(formatDate(time))
}

// 预约看房日期：不能早于今天，且不能是已占用日期
const disabledAppointmentDate = (time) => {
  if (time.getTime() < Date.now() - 8.64e7) return true
  return isDateOccupied(formatDate(time))
}

// 打开预约看房弹窗
const openAppointmentDialog = () => {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录再预约看房')
    router.push('/login')
    return
  }
  appointmentForm.date = null
  appointmentForm.time = ''
  appointmentForm.remark = ''
  appointmentVisible.value = true
}

// 提交看房预约
const handleSubmitAppointment = async () => {
  if (!appointmentForm.date) {
    ElMessage.warning('请选择看房日期')
    return
  }
  if (!appointmentForm.time) {
    ElMessage.warning('请选择看房时段')
    return
  }
  appointmentSubmitting.value = true
  try {
    const res = await submitAppointment({
      roomId: room.value.id,
      appointmentDate: appointmentForm.date,
      appointmentTime: appointmentForm.time,
      remark: appointmentForm.remark
    })
    if (res.code === 200) {
      ElMessage.success(res.message || '预约提交成功')
      appointmentVisible.value = false
      router.push('/tenant/my/appointments')
    } else {
      ElMessage.error(res.message || '预约提交失败')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '预约提交失败')
  } finally {
    appointmentSubmitting.value = false
  }
}

// 计算晚数
const totalNights = computed(() => {
  if (!orderForm.checkInDate || !orderForm.checkOutDate) return 0
  const diff = orderForm.checkOutDate.getTime() - orderForm.checkInDate.getTime()
  return Math.ceil(diff / (1000 * 60 * 60 * 24))
})

// 计算租金
const totalAmount = computed(() => {
  if (!room.value || !totalNights.value) return 0
  return totalNights.value * room.value.price
})

// ========== 加载房源详情 ==========
const loadRoomDetail = async () => {
  loading.value = true
  try {
    const res = await getRoomDetail(roomId)
    if (res.code === 200) {
      room.value = res.data
      currentImage.value = res.data?.cover || imageList.value[0] || ''
      // 如果是对象，直接赋值，否则保持 null
      if (res.data) {
        // 查询房东信息（如果有 landlordId）
        if (res.data.landlordId) {
          try {
            const userRes = await request({
              url: `/user/detail/${res.data.landlordId}`,
              method: 'get'
            })
            if (userRes.code === 200) {
              landlord.value = userRes.data
            }
          } catch (e) {
            console.log('获取房东信息失败')
          }
        }
        // 检查收藏状态
        const token = localStorage.getItem('token')
        if (token) {
          try {
            const favRes = await request({
              url: '/favorite/check',
              method: 'get',
              params: { roomId: roomId }
            })
            if (favRes.code === 200) {
              room.value.isFavorited = favRes.data === true
            }
          } catch (e) {
            room.value.isFavorited = false
          }
        } else {
          room.value.isFavorited = false
        }
      }
    } else {
      ElMessage.error(res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载房源详情失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
  // 加载房态日历（用于禁用已订日期）
  loadCalendar()
  // 加载评论
  loadReviews()
}

// ========== 收藏/取消收藏 ==========
const toggleFavorite = async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录再收藏')
    router.push('/login')
    return
  }

  try {
    if (room.value.isFavorited) {
      const res = await request({
        url: '/favorite/cancel',
        method: 'post',
        data: { roomId: room.value.id }
      })
      if (res.code === 200) {
        room.value.isFavorited = false
        ElMessage.success('已取消收藏')
      } else {
        ElMessage.error(res.message || '取消收藏失败')
      }
    } else {
      const res = await request({
        url: '/favorite/add',
        method: 'post',
        data: { roomId: room.value.id }
      })
      if (res.code === 200) {
        room.value.isFavorited = true
        ElMessage.success('收藏成功')
      } else {
        ElMessage.error(res.message || '收藏失败')
      }
    }
  } catch (error) {
    console.error('收藏操作失败', error)
    ElMessage.error('操作失败，请稍后重试')
  }
}

// ========== 立即预订 ==========
const handleBook = async () => {
  // 1. 检查登录
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  // 2. 检查日期
  if (!orderForm.checkInDate || !orderForm.checkOutDate) {
    ElMessage.warning('请选择入住和退租日期')
    return
  }

  if (totalNights.value <= 0) {
    ElMessage.warning('退租日期必须晚于入住日期')
    return
  }

  // 3. 提交订单
  booking.value = true
  try {
    const res = await createOrder({
      roomId: room.value.id,
      checkInDate: formatDate(orderForm.checkInDate),
      checkOutDate: formatDate(orderForm.checkOutDate)
    })
    if (res.code === 200 || res.code === 0) {
      ElMessage.success('下单成功，正在跳转支付...')
      // 直接跳转到支付页面
      router.replace({
        path: '/tenant/my/pay',
        query: { orderNo: res.data?.orderNo || '', orderId: res.data?.id || '' }
      })
    } else {
      ElMessage.error(res.message || '下单失败')
    }
  } catch (error) {
    console.error('下单失败', error)
    ElMessage.error(error.response?.data?.message || '下单失败，请稍后重试')
  } finally {
    booking.value = false
  }
}

// ========== 地图导航（高德） ==========
const openNavigation = () => {
  const { longitude, latitude, title } = room.value
  if (!longitude || !latitude) {
    ElMessage.warning('该房源暂未标注地图位置')
    return
  }
  const url = buildAmapUri(longitude, latitude, title)
  window.open(url, '_blank')
}

// ========== 联系房东（跳转聊天） ==========
const contactLandlord = () => {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录，再联系房东')
    router.push('/login')
    return
  }
  if (landlord.value?.id) {
    router.push(`/chat?friendId=${landlord.value.id}`)
  } else {
    ElMessage.warning('暂未获取到房东信息')
  }
}

// 工具：格式化日期为 YYYY-MM-DD
const formatDate = (date) => {
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// ========== 评价相关 ==========
const loadReviews = async () => {
  reviewsLoading.value = true
  try {
    const res = await request({
      url: `/evaluation/room/${roomId}`,
      method: 'get',
      params: { pageNum: reviewPage.value, pageSize: pageSize.value }
    })
    if (res.code === 200) {
      reviews.value = res.data?.records || []
      totalReviews.value = res.data?.total || 0
    }
  } catch (error) {
    console.error('加载评价失败', error)
  } finally {
    reviewsLoading.value = false
  }
}

const handleReviewUpload = (res) => {
  if (res.code === 200) {
    uploadedReviewImages.value.push(res.data)
  } else {
    ElMessage.error(res.message || '上传失败')
  }
}

const handleReviewRemove = (file) => {
  const url = file.response?.data || file.url
  const idx = uploadedReviewImages.value.indexOf(url)
  if (idx > -1) uploadedReviewImages.value.splice(idx, 1)
}

const submitReview = async () => {
  try { await reviewFormRef.value?.validate() } catch { return }
  reviewSubmitting.value = true
  try {
    const res = await request({
      url: '/evaluation/add',
      method: 'post',
      data: {
        roomId,
        rating: reviewForm.rating,
        content: reviewForm.content,
        images: uploadedReviewImages.value.join(',')
      }
    })
    if (res.code === 200) {
      ElMessage.success('评价发表成功')
      reviewForm.rating = 5
      reviewForm.content = ''
      reviewFileList.value = []
      uploadedReviewImages.value = []
      reviewPage.value = 1
      loadReviews()
    } else {
      ElMessage.error(res.message || '发表失败')
    }
  } catch (error) {
    ElMessage.error('发表失败')
  } finally {
    reviewSubmitting.value = false
  }
}

onMounted(loadRoomDetail)
</script>

<style scoped>
.room-detail-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
.room-container {
  display: flex;
  gap: 40px;
}
.room-image {
  flex: 1.2;
}
.image-thumbs {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  overflow-x: auto;
}
.image-thumbs .thumb {
  width: 90px;
  height: 65px;
  border-radius: 6px;
  cursor: pointer;
  border: 2px solid transparent;
  flex-shrink: 0;
}
.image-thumbs .thumb.active {
  border-color: #409eff;
}
.description-section {
  margin-top: 20px;
}
.description-section h3 {
  margin: 0 0 12px;
}
.description-text {
  color: var(--text-sub);
  line-height: 1.8;
  white-space: pre-wrap;
}
.calendar-section { margin-top: 20px; }
.calendar-tip { color: var(--text-sub); font-size: 13px; margin: 0 0 12px; }
.room-info {
  flex: 1;
}
.room-title {
  font-size: 28px;
  margin: 0 0 12px 0;
}
.room-address {
  color: var(--text-sub);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}
.room-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin: 12px 0;
}
.room-price .price {
  font-size: 32px;
  font-weight: bold;
  color: #f56c6c;
}
.room-price .unit {
  font-size: 16px;
  color: var(--text-sub);
}
.landlord-info {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 0;
}
.landlord-detail .name {
  font-weight: bold;
  font-size: 16px;
}
.landlord-detail .rating {
  color: var(--text-sub);
  font-size: 14px;
}
.booking-form {
  background: var(--bg-soft);
  padding: 20px;
  border-radius: 12px;
  margin-top: 16px;
}
.booking-form h3 {
  margin: 0 0 16px 0;
}
.date-picker {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}
.price-summary {
  background: var(--bg-card);
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}
.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
}
.summary-row.total {
  font-weight: bold;
  font-size: 18px;
  border-top: 1px solid var(--border-color);
  padding-top: 12px;
  margin-top: 6px;
}
.action-buttons {
  display: flex;
  gap: 12px;
}

/* 评论区样式 */
.review-section { margin-top: 20px; }
.review-section h3 { margin-bottom: 16px; }
.review-section h4 { margin: 8px 0; }
.no-reviews { color: var(--text-sub); text-align: center; padding: 30px; }
.review-item { padding: 14px 0; border-bottom: 1px solid var(--border-color); }
.review-header { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.review-user { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.review-nick { font-weight: bold; font-size: 14px; }
.review-rating { color: #f5a623; font-size: 13px; }
.review-time { font-size: 12px; color: var(--text-sub); }
.review-content { font-size: 14px; line-height: 1.6; margin: 8px 0; padding: 8px 12px; background: var(--bg-soft); border-radius: 6px; }
.review-images { margin: 8px 0; display: flex; flex-wrap: wrap; }
.review-reply { margin-top: 8px; padding: 8px 12px; background: #f0f9ff; border-radius: 6px; border-left: 3px solid #409eff; font-size: 13px; }
html.dark .review-reply { background: rgba(64, 158, 255, 0.12); border-left-color: rgba(64, 158, 255, 0.6); }
.reply-tag { color: #409eff; font-weight: bold; }
.review-pagination { display: flex; justify-content: center; padding: 16px 0; }
.write-review { margin-top: 20px; }
</style>