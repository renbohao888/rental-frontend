// 滚动进入视口动画指令 v-reveal
// 用法：
//   v-reveal                                  -> 默认向上淡入
//   v-reveal="{ dir: 'left', delay: 100 }"    -> 从左滑入，延迟 100ms
// 可选 dir：up(默认) / left / right / zoom
export default {
  mounted(el, binding) {
    el.classList.add('reveal-init')
    const opt = binding.value || {}
    if (opt.dir) el.classList.add(`reveal-${opt.dir}`)
    if (opt.delay) el.style.transitionDelay = `${opt.delay}ms`

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
  },
  unmounted(el) {
    if (el._revealObserver) {
      el._revealObserver.disconnect()
      el._revealObserver = null
    }
  }
}
