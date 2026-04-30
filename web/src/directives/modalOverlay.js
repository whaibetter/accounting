export const vModalOverlay = {
  mounted(el, binding) {
    let mouseDownTarget = null

    el._onMouseDown = (e) => {
      mouseDownTarget = e.target
    }

    el._onClick = (e) => {
      if (e.target === document.documentElement || e.target === document.body) return
      if (mouseDownTarget !== el) return
      if (e.target === el) {
        binding.value()
      }
    }

    el.addEventListener('mousedown', el._onMouseDown, true)
    el.addEventListener('click', el._onClick, true)
  },
  unmounted(el) {
    el.removeEventListener('mousedown', el._onMouseDown, true)
    el.removeEventListener('click', el._onClick, true)
  },
}
