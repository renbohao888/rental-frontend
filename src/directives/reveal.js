// 滚动进入视口动画指令 v-reveal
// 用法：
//   v-reveal                                  -> 默认向上淡入
//   v-reveal="{ dir: 'left', delay: 100 }"    -> 从左滑入，延迟 100ms
// 可选 dir：up(默认) / left / right / zoom
const FALLBACK_DELAY = 3000 // 兜底：进入视口动画 3 秒内未触发则强制显示，防止元素被永久隐藏

// 是否已在视口内（含底部缩进 40px，与 IO rootMargin 保持一致）
function isInViewport(el) {
  const rect = el.getBoundingClientRect()
  const vh = window.innerHeight || document.documentElement.clientHeight
  return rect.bottom > 0 && rect.top < vh - 40
}

// 强制显示：防止 IntersectionObserver 首次判断异常导致元素永久 opacity: 0
function forceShow(el) {
  if (!document.contains(el)) return
  if (!el.classList.contains('reveal-in')) {
    el.classList.add('reveal-in')
    el.style.transitionDelay = ''
  }
  if (el._revealObserver) {
    el._revealObserver.disconnect()
    el._revealObserver = null
  }
}

export default {
  mounted(el, binding) {
    el.classList.add('reveal-init')
    const opt = binding.value || {}
    if (opt.dir) el.classList.add(`reveal-${opt.dir}`)
    if (opt.delay) el.style.transitionDelay = `${opt.delay}ms`

    // 首屏元素：已在视口内则直接显示（不依赖 IO 首次异步回调，避免首屏内容永久隐藏）
    if (isInViewport(el)) {
      el.classList.add('reveal-in')
      el.style.transitionDelay = ''
      return
    }

    // 低版本浏览器兜底：直接显示
    if (typeof IntersectionObserver === 'undefined') {
      el.classList.add('reveal-in')
      return
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            el.classList.add('reveal-in')
            observer.unobserve(el)
            // transitionend 后清除内联延迟，避免残留 delay 影响后续 hover 过渡
            el.addEventListener('transitionend', () => {
              el.style.transitionDelay = ''
            }, { once: true })
          }
        })
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
    )
    observer.observe(el)
    el._revealObserver = observer

    // 兜底：超时仍未触发动画则强制显示，杜绝"内容永久隐藏"导致的排版错乱
    setTimeout(() => forceShow(el), FALLBACK_DELAY)
  },
  unmounted(el) {
    if (el._revealObserver) {
      el._revealObserver.disconnect()
      el._revealObserver = null
    }
  }
}
