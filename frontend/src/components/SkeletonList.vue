<template>
  <div role="status" aria-busy="true" aria-live="polite">
    <v-skeleton-loader v-if="!mobile" type="table" class="skeleton-table" />
    <div v-else>
      <v-skeleton-loader
        v-for="i in filas"
        :key="i"
        :type="avatar ? 'list-item-avatar-two-line' : 'list-item-two-line'"
        class="skeleton-mobile-card mb-3"
      />
    </div>
  </div>
</template>

<script setup>
import { useDisplay } from 'vuetify'

defineProps({
  filas: { type: Number, default: 6 },
  avatar: { type: Boolean, default: true },
})

const { mobile } = useDisplay()
</script>
