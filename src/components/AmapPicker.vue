<template>
  <div class="amap-picker">
    <div class="picker-toolbar">
      <el-input
        v-model="keyword"
        placeholder="搜索地址，如：北京市朝阳区xx路xx号"
        size="small"
        clearable
        @keyup.enter="searchKeyword"
      >
        <template #append>
          <el-button size="small" @click="searchKeyword">搜索</el-button>
        </template>
      </el-input>
    </div>
    <div ref="mapContainer" class="map-container"></div>
    <div v-if="selected" class="picker-result">
      <p>📍 {{ selected.address }}</p>
      <p class="coord">经纬度：{{ selected.lng.toFixed(6) }}, {{ selected.lat.toFixed(6) }}</p>
      <el-button type="primary" size="small" @click="confirm">确认使用此位置</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { loadAMap } from '@/utils/amap'

const emit = defineEmits(['select'])
const mapContainer = ref(null)
const keyword = ref('')
const selected = ref(null)

let map = null
let marker = null
let geocoder = null
let placeSearch = null

onMounted(async () => {
  try {
    const AMap = await loadAMap()
    initMap(AMap)
  } catch (e) {
    ElMessage.error(e.message || '地图加载失败，请检查网络')
  }
})

const initMap = (AMap) => {
  map = new AMap.Map(mapContainer.value, {
    zoom: 13,
    center: [116.397428, 39.90923] // 默认北京
  })
  geocoder = new AMap.Geocoder({ radius: 1000 })
  placeSearch = new AMap.PlaceSearch({ pageSize: 10, pageIndex: 1 })

  map.on('click', (e) => {
    const { lng, lat } = e.lnglat
    placeMarker(AMap, lng, lat)
    // 逆地理编码获取地址
    geocoder.getAddress([lng, lat], (status, result) => {
      if (status === 'complete' && result.regeocode) {
        selected.value = {
          address: result.regeocode.formattedAddress,
          lng,
          lat
        }
      }
    })
  })
}

const placeMarker = (AMap, lng, lat) => {
  if (marker) marker.setMap(null)
  marker = new AMap.Marker({ position: [lng, lat] })
  marker.setMap(map)
  map.setCenter([lng, lat])
}

const searchKeyword = async () => {
  const kw = keyword.value.trim()
  if (!kw) return
  const AMap = await loadAMap()
  placeSearch.search(kw, (status, result) => {
    if (status === 'complete' && result.poiList && result.poiList.pois.length) {
      const poi = result.poiList.pois[0]
      map.setZoom(16)
      map.setCenter(poi.location)
      placeMarker(AMap, poi.location.lng, poi.location.lat)
      selected.value = {
        address: poi.name + (poi.address ? ' ' + poi.address : ''),
        lng: poi.location.lng,
        lat: poi.location.lat
      }
    } else {
      ElMessage.warning('未找到该地址')
    }
  })
}

const confirm = () => {
  emit('select', { ...selected.value })
}

onBeforeUnmount(() => {
  if (map) map.destroy()
})
</script>

<style scoped>
.amap-picker .picker-toolbar {
  margin-bottom: 8px;
}
.map-container {
  width: 100%;
  height: 340px;
  border-radius: 8px;
  border: 1px solid #dcdfe6;
}
.picker-result {
  margin-top: 8px;
  padding: 10px 12px;
  background: #f5f7fa;
  border-radius: 6px;
}
.picker-result p {
  margin: 0 0 4px;
  font-size: 13px;
}
.picker-result .coord {
  color: #909399;
  font-size: 12px;
}
</style>
