<template>
  <RouterView />
  <Toast position="top-right" />
</template>

<script setup>
import { RouterView } from 'vue-router'
import Toast from 'primevue/toast'
</script>
