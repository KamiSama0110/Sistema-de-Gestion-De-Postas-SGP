<template>
  <v-container class="fill-height">
    <v-row justify="center">
      <v-col cols="12" sm="8" md="6">
        <v-card class="text-center pa-8" elevation="0" rounded="xl">
          <div class="text-h1 font-weight-black text-primary mb-4">404</div>
          <h1 class="text-h5 font-weight-bold mb-2">Pagina no encontrada</h1>
          <p class="text-body-1 text-medium-emphasis mb-6">
            La ruta que buscas no existe o fue movida.
          </p>
          <v-btn
            color="primary"
            prepend-icon="mdi-home"
            :to="auth.isAuthenticated ? { name: 'dashboard' } : { name: 'login' }"
          >
            {{ auth.isAuthenticated ? 'Ir al dashboard' : 'Ir al login' }}
          </v-btn>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
</script>
