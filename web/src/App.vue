<template>
  <router-view />
  <ToastMessage ref="toastRef" />
</template>

<script setup>
import { onMounted, ref } from 'vue'
import ToastMessage from '@/components/ToastMessage.vue'
import { setToastRef } from '@/utils/toast'

const toastRef = ref(null)

onMounted(() => {
  if (toastRef.value) {
    setToastRef(toastRef.value)
  }
})
</script>
