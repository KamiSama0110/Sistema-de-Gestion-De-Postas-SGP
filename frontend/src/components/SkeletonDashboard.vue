<template>
  <div role="status" aria-busy="true" aria-live="polite">
    <v-row class="mb-6" dense>
      <v-col v-for="i in 4" :key="i" cols="6" md="3">
        <v-card rounded="lg" class="pa-4" style="min-height: 120px">
          <v-skeleton-loader type="list-item-avatar-two-line" class="skeleton-dash-card" />
        </v-card>
      </v-col>
    </v-row>

    <v-card rounded="lg" class="mb-6 pa-sm-5 pa-3">
      <div class="d-flex align-center justify-space-between mb-2">
        <v-skeleton-loader type="text" width="140" />
        <v-skeleton-loader type="text" width="60" />
      </div>
      <v-skeleton-loader type="paragraph" />
    </v-card>

    <v-card rounded="lg" class="pa-sm-5 pa-3">
      <div class="d-flex align-center justify-space-between mb-2">
        <v-skeleton-loader type="text" width="150" />
        <v-skeleton-loader type="chip" width="48" />
      </div>
      <SkeletonList :filas="4" :avatar="false" />
    </v-card>
  </div>
</template>

<script setup>
import SkeletonList from './SkeletonList.vue'
</script>

