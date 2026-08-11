// 高德地图 JS API 配置（请替换为你的 Key 与安全密钥）
const AMAP_KEY = '***REMOVED***'
const AMAP_SECURITY_CODE = '***REMOVED***'

let amapPromise = null

/**
 * 动态加载高德地图 JS API 2.0（含安全密钥）
 * @returns {Promise} window.AMap
 */
export function loadAMap() {
  if (window.AMap) return Promise.resolve(window.AMap)
  if (amapPromise) return amapPromise

  amapPromise = new Promise((resolve, reject) => {
    // 必须在加载 SDK 前设置安全密钥
    window._AMapSecurityConfig = { securityJsCode: AMAP_SECURITY_CODE }

    const script = document.createElement('script')
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${AMAP_KEY}&plugin=AMap.PlaceSearch,AMap.Geocoder`
    script.async = true
    script.onload = () => {
      if (window.AMap) resolve(window.AMap)
      else reject(new Error('高德地图 SDK 加载失败'))
    }
    script.onerror = () => {
      amapPromise = null
      reject(new Error('高德地图 SDK 网络加载失败'))
    }
    document.head.appendChild(script)
  })

  return amapPromise
}

/**
 * 生成高德地图导航/标记 URI 链接（无需 SDK）
 * @param {Number} lng 经度
 * @param {Number} lat 纬度
 * @param {String} name 地点名称
 */
export function buildAmapUri(lng, lat, name) {
  const title = encodeURIComponent(name || '房源位置')
  return `https://uri.amap.com/marker?position=${lng},${lat}&name=${title}&coordinate=gaode`
}
