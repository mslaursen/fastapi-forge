import { defineStore } from "pinia"
import { ref, shallowRef, markRaw, type Component } from "vue"

export const useModalStore = defineStore("modal", () => {
  const isOpen = ref(false)
  const currentComponent = shallowRef<Component | null>(null)
  const props = ref<Record<string, any>>({})

  function open(component: Component, componentProps: Record<string, any> = {}) {
    currentComponent.value = markRaw(component)
    props.value = componentProps
    isOpen.value = true
  }

  function close() {
    isOpen.value = false
    currentComponent.value = null
    props.value = {}
  }

  return {
    isOpen,
    currentComponent,
    props,
    open,
    close,
  }
})
