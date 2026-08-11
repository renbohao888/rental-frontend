// src/utils/autoReveal.js
// 全局自动滚动动画：路由切换后自动扫描当前页面里的主要区块，
// 让「基本所有网页」在滚动/打开时都有画面弹出的入场效果，
// 无需在每个页面手动加 v-reveal（与 v-reveal 指令共用 reveal-init / reveal-in 类，互不冲突）。

const AUTO_REVEAL_SELECTOR = [
  '.el-card',         // Element Plus 卡片（后台 / 房东 / 租客页面主体）
  '.rc-card',         // 全局橙色卡片（房源卡片、搜索结果等）
  '.section',         // 通用区块
  '.stat-card',       // 统计指标卡
  '.filter-bar',      // 筛选栏
  '.header-card',     // 页面头部卡片
  '.welcome-banner',  // 欢迎横幅
  '.quick-links',     // 快捷入口区
  '.stats-section',   // 统计区
  '.page-header',     // 页面标题区
  '.content-card',    // 内容卡片
  '.my-sidebar',      // 个人中心侧栏
  '.chat-page',       // 聊天页整体
].join(',')

const STAGGER_STEP = 60   // 相邻元素交错延迟（ms）
const STAGGER_MAX = 6     // 最多交错前 6 个，避免长页面延迟过大

function scanOnce() {
  const root = document.getElementById('app')
  if (!root) return
  const targets = root.querySelectorAll(AUTO_REVEAL_SELECTOR)
  let order = 0
  targets.forEach((el) => {
    // 已被 v-reveal 或上一次扫描处理过的元素跳过
    if (el.classList.contains('reveal-init')) return
    el.classList.add('reveal-init')
    el.style.transitionDelay = `${(order % STAGGER_MAX) * STAGGER_STEP}ms`
    order += 1

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          el.classList.add('reveal-in')
          observer.disconnect()
          // transitionend 后清除内联延迟，避免残留 delay 影响后续 hover 过渡
          el.addEventListener('transitionend', () => {
            el.style.transitionDelay = ''
          }, { once: true })
        }
      })
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' })
    observer.observe(el)
    el._autoRevealObserver = observer
  })
}

export function autoRevealScan() {
  // 低版本浏览器兜底
  if (typeof IntersectionObserver === 'undefined') return

  // 等 router-view 内容渲染完再扫描（组件懒加载，延迟一拍最稳）
  setTimeout(scanOnce, 40)
  // 异步接口返回数据后（表格/卡片加载完）再补扫一次，保证全部页面都有动画
  setTimeout(scanOnce, 900)
}
