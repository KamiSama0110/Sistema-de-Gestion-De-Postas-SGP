<template>
  <div class="guardias-cuadro-page mx-auto">
    <v-card rounded="lg" class="pa-sm-5 pa-3">
      <div class="d-flex flex-column flex-sm-row align-sm-center justify-sm-space-between mb-4 ga-3">
        <v-text-field
          v-model="buscar"
          prepend-inner-icon="mdi-magnify"
          placeholder="Buscar por cuadro..."
          variant="solo-filled"
          density="compact"
          hide-details
          clearable
          bg-color="grey-lighten-4"
          class="buscador"
          @update:model-value="onBuscar"
        />
        <v-chip
          v-if="planIdFiltro"
          color="primary"
          variant="tonal"
          closable
          label
          @click:close="limpiarPlan"
        >
          Plan #{{ planIdFiltro }}
        </v-chip>
        <div class="text-body-2 text-medium-emphasis text-center">
          {{ total }} resultado{{ total !== 1 ? 's' : '' }}
        </div>
      </div>

      <div class="d-flex flex-wrap align-center justify-center ga-2 mb-4">
        <v-menu v-model="menuDesde" :close-on-content-click="false" location="bottom start">
          <template #activator="{ props: menuProps }">
            <v-text-field
              :model-value="desde ? formatFecha(desde) : ''"
              label="Desde"
              readonly
              append-inner-icon="mdi-calendar"
              variant="solo-filled"
              density="compact"
              hide-details
              clearable
              bg-color="grey-lighten-4"
              class="filtro-fecha"
              v-bind="menuProps"
              @click:clear="desde = null; periodo = 'rango'; reiniciar()"
            />
          </template>
          <v-date-picker v-model="desdePicker" color="primary" />
        </v-menu>
        <v-menu v-model="menuHasta" :close-on-content-click="false" location="bottom start">
          <template #activator="{ props: menuProps }">
            <v-text-field
              :model-value="hasta ? formatFecha(hasta) : ''"
              label="Hasta"
              readonly
              append-inner-icon="mdi-calendar"
              variant="solo-filled"
              density="compact"
              hide-details
              clearable
              bg-color="grey-lighten-4"
              class="filtro-fecha"
              v-bind="menuProps"
              @click:clear="hasta = null; periodo = 'rango'; reiniciar()"
            />
          </template>
          <v-date-picker v-model="hastaPicker" color="primary" />
        </v-menu>
        <v-divider vertical class="mx-1" />
        <v-autocomplete
          v-model="filtroCuadro"
          :items="cuadrosList"
          item-title="titulo"
          item-value="id"
          label="Cuadro"
          variant="solo-filled"
          density="compact"
          hide-details
          clearable
          bg-color="grey-lighten-4"
          class="filtro-cuadro"
          @update:model-value="reiniciar"
        />
        <v-select
          v-model="filtroEstado"
          :items="estadosItems"
          label="Estado"
          variant="solo-filled"
          density="compact"
          hide-details
          clearable
          bg-color="grey-lighten-4"
          class="filtro"
          @update:model-value="reiniciar"
        />
        <v-divider vertical class="mx-1" />
        <v-btn
          v-for="p in periodos"
          :key="p.value"
          :variant="periodo === p.value ? 'flat' : 'outlined'"
          :color="periodo === p.value ? 'primary' : 'default'"
          size="small"
          class="text-none"
          @click="setPeriodo(p.value)"
        >
          {{ p.label }}
        </v-btn>
      </div>

      <div aria-live="polite">
        <SkeletonList v-if="cargando" :filas="6" />

        <Transition name="fade-up" mode="out-in">
          <div v-if="!cargando && guardias.length === 0" key="empty" class="text-center py-12">
            <v-icon icon="mdi-shield-off-outline" size="48" color="grey-lighten-1" class="mb-2" />
            <p class="text-body-1 text-medium-emphasis">No hay guardias para mostrar</p>
          </div>

          <!-- Mobile: card list -->
          <div v-else-if="!cargando && guardias.length > 0 && mobile" key="mobile-list" class="guardias-mobile-list">
            <div v-for="g in guardias" :key="g.id" class="guardias-mobile-card pa-4 mb-3">
              <div class="d-flex align-center justify-space-between mb-2">
                <div class="d-flex align-center ga-3">
                  <v-avatar :color="estadoColor(g.estado)" size="36" rounded="lg">
                    <v-icon :icon="estadoIcon(g.estado)" size="18" color="white" />
                  </v-avatar>
                  <div>
                    <div class="text-body-1 font-weight-medium">{{ g.cuadro_nombre }}</div>
                    <div class="text-body-2 text-medium-emphasis">{{ g.franja_nombre }}</div>
                  </div>
                </div>
                <v-chip :color="estadoColor(g.estado)" variant="elevated" size="x-small" label class="font-weight-bold">
                  {{ estadoLabel(g.estado) }}
                </v-chip>
              </div>
              <div class="text-body-2 text-medium-emphasis mb-2">
                {{ formatFecha(g.fecha) }}
                <span v-if="horarioDe(g)">· {{ horarioDe(g) }}</span>
              </div>
              <div v-if="g.inicio_real || g.fin_real" class="text-body-2 text-medium-emphasis mb-2">
                <span v-if="g.inicio_real">Inicio: {{ formatDateTime(g.inicio_real) }}</span>
                <span v-if="g.fin_real" class="ml-3">Fin: {{ formatDateTime(g.fin_real) }}</span>
              </div>
              <div class="d-flex justify-end ga-1">
                <v-btn
                  icon size="x-small" variant="text"
                  aria-label="Ver detalle"
                  @click="abrirDetalle(g)"
                >
                  <v-icon icon="mdi-eye-outline" size="16" />
                </v-btn>
                <v-btn
                  v-if="g.estado === 'planificada'"
                  icon size="x-small" variant="text" color="success"
                  aria-label="Marcar llegada"
                  @click="abrirLlegada(g)"
                >
                  <v-icon icon="mdi-clock-check-outline" size="16" />
                </v-btn>
                <v-btn
                  v-if="g.estado === 'activa'"
                  icon size="x-small" variant="text" color="warning"
                  aria-label="Marcar salida"
                  @click="abrirSalida(g)"
                >
                  <v-icon icon="mdi-stop-circle-outline" size="16" />
                </v-btn>
                <v-btn
                  v-if="['planificada', 'activa'].includes(g.estado)"
                  icon size="x-small" variant="text" color="warning"
                  aria-label="Marcar incumplida"
                  @click="abrirIncumplir(g)"
                >
                  <v-icon icon="mdi-account-off-outline" size="16" />
                </v-btn>
                <v-btn
                  v-if="g.estado === 'planificada'"
                  icon size="x-small" variant="text" color="error"
                  aria-label="Cancelar guardia"
                  @click="abrirCancelar(g)"
                >
                  <v-icon icon="mdi-cancel" size="16" />
                </v-btn>
                <v-btn
                  icon size="x-small" variant="text" color="info"
                  aria-label="Ver incidencias"
                  @click="verIncidencias(g)"
                >
                  <v-icon icon="mdi-clipboard-text-outline" size="16" />
                </v-btn>
              </div>
            </div>
          </div>

          <!-- Desktop: table -->
          <v-table v-else-if="!cargando && guardias.length > 0" key="table" density="comfortable">
            <thead>
              <tr>
                <th class="text-body-1 font-weight-bold text-medium-emphasis">Fecha</th>
                <th class="text-body-1 font-weight-bold text-medium-emphasis">Franja</th>
                <th class="text-body-1 font-weight-bold text-medium-emphasis">Cuadro</th>
                <th class="text-body-1 font-weight-bold text-medium-emphasis">Estado</th>
                <th class="text-body-1 font-weight-bold text-medium-emphasis">Inicio / Fin</th>
                <th class="text-body-1 font-weight-bold text-medium-emphasis text-center">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="g in guardias" :key="g.id">
                <td class="text-body-1">{{ formatFecha(g.fecha) }}</td>
                <td class="text-body-1">
                  {{ g.franja_nombre }}
                  <span class="text-body-2 text-medium-emphasis ms-1">{{ horarioDe(g) }}</span>
                </td>
                <td class="font-weight-medium text-body-1">{{ g.cuadro_nombre }}</td>
                <td>
                  <v-chip :color="estadoColor(g.estado)" variant="elevated" size="small" label class="font-weight-bold">
                    {{ estadoLabel(g.estado) }}
                  </v-chip>
                </td>
                <td class="text-body-2">
                  <div v-if="g.inicio_real || g.fin_real">
                    <div v-if="g.inicio_real">Inicio: {{ formatDateTime(g.inicio_real) }}</div>
                    <div v-if="g.fin_real">Fin: {{ formatDateTime(g.fin_real) }}</div>
                  </div>
                  <span v-else class="text-medium-emphasis">—</span>
                </td>
                <td class="text-center">
                  <v-tooltip text="Ver detalle" location="top">
                    <template #activator="{ props: tipProps }">
                      <v-btn icon size="small" variant="text" aria-label="Ver detalle" v-bind="tipProps" @click="abrirDetalle(g)">
                        <v-icon icon="mdi-eye-outline" size="18" />
                      </v-btn>
                    </template>
                  </v-tooltip>
                  <v-tooltip v-if="g.estado === 'planificada'" text="Marcar llegada" location="top">
                    <template #activator="{ props: tipProps }">
                      <v-btn icon size="small" variant="text" color="success" aria-label="Marcar llegada" v-bind="tipProps" @click="abrirLlegada(g)">
                        <v-icon icon="mdi-clock-check-outline" size="18" />
                      </v-btn>
                    </template>
                  </v-tooltip>
                  <v-tooltip v-if="g.estado === 'activa'" text="Marcar salida" location="top">
                    <template #activator="{ props: tipProps }">
                      <v-btn icon size="small" variant="text" color="warning" aria-label="Marcar salida" v-bind="tipProps" @click="abrirSalida(g)">
                        <v-icon icon="mdi-stop-circle-outline" size="18" />
                      </v-btn>
                    </template>
                  </v-tooltip>
                  <v-tooltip v-if="['planificada', 'activa'].includes(g.estado)" text="Marcar incumplida" location="top">
                    <template #activator="{ props: tipProps }">
                      <v-btn icon size="small" variant="text" color="warning" aria-label="Marcar incumplida" v-bind="tipProps" @click="abrirIncumplir(g)">
                        <v-icon icon="mdi-account-off-outline" size="18" />
                      </v-btn>
                    </template>
                  </v-tooltip>
                  <v-tooltip v-if="g.estado === 'planificada'" text="Cancelar guardia" location="top">
                    <template #activator="{ props: tipProps }">
                      <v-btn icon size="small" variant="text" color="error" aria-label="Cancelar guardia" v-bind="tipProps" @click="abrirCancelar(g)">
                        <v-icon icon="mdi-cancel" size="18" />
                      </v-btn>
                    </template>
                  </v-tooltip>
                  <v-tooltip text="Ver incidencias" location="top">
                    <template #activator="{ props: tipProps }">
                      <v-btn icon size="small" variant="text" color="info" aria-label="Ver incidencias" v-bind="tipProps" @click="verIncidencias(g)">
                        <v-icon icon="mdi-clipboard-text-outline" size="18" />
                      </v-btn>
                    </template>
                  </v-tooltip>
                </td>
              </tr>
            </tbody>
          </v-table>
        </Transition>
      </div>

      <div v-if="totalPaginas > 1" class="d-flex align-center justify-center ga-2 mt-4">
        <v-btn icon size="small" variant="text" :disabled="pagina === 1" aria-label="Página anterior" @click="cambiarPagina(-1)">
          <v-icon icon="mdi-chevron-left" />
        </v-btn>
        <span class="text-body-2 text-medium-emphasis">{{ pagina }}/{{ totalPaginas }}</span>
        <v-btn icon size="small" variant="text" :disabled="pagina >= totalPaginas" aria-label="Página siguiente" @click="cambiarPagina(1)">
          <v-icon icon="mdi-chevron-right" />
        </v-btn>
      </div>
    </v-card>

    <!-- Dialog detalle guardia -->
    <v-dialog v-model="dialogDetalle" :max-width="xs ? undefined : 650" :fullscreen="xs">
      <v-card rounded="lg" v-if="detalleGuardia">
        <v-card-title class="d-flex align-center justify-space-between pa-6 pb-2">
          <div class="d-flex align-center ga-3">
            <v-avatar :color="estadoColor(detalleGuardia.estado)" size="36" rounded="lg">
              <v-icon :icon="estadoIcon(detalleGuardia.estado)" size="18" color="white" />
            </v-avatar>
            <div>
              <span class="text-h6 font-weight-bold">{{ detalleGuardia.cuadro_nombre }}</span>
              <div class="text-body-2 text-medium-emphasis">{{ estadoLabel(detalleGuardia.estado) }}</div>
            </div>
          </div>
          <v-chip :color="estadoColor(detalleGuardia.estado)" variant="elevated" size="small" label class="font-weight-bold">
            {{ estadoLabel(detalleGuardia.estado) }}
          </v-chip>
        </v-card-title>
        <v-card-text class="pa-6 pt-4">
          <div class="ficha-section mb-5">
            <div class="ficha-section-title mb-3">Información de la guardia</div>
            <div class="ficha-grid">
              <div class="ficha-item">
                <span class="ficha-label">Cuadro</span>
                <span class="ficha-value">{{ detalleGuardia.cuadro_nombre }}</span>
              </div>
              <div class="ficha-item">
                <span class="ficha-label">Fecha</span>
                <span class="ficha-value">{{ formatFecha(detalleGuardia.fecha) }}</span>
              </div>
              <div class="ficha-item">
                <span class="ficha-label">Franja</span>
                <span class="ficha-value">
                  {{ detalleGuardia.franja_nombre }}
                  <span v-if="horarioDe(detalleGuardia)" class="text-medium-emphasis">· {{ horarioDe(detalleGuardia) }}</span>
                </span>
              </div>
              <div class="ficha-item">
                <span class="ficha-label">Estado</span>
                <span class="ficha-value font-weight-bold" :class="`text-${estadoColor(detalleGuardia.estado)}`">
                  {{ estadoLabel(detalleGuardia.estado) }}
                </span>
              </div>
              <div v-if="detalleGuardia.inicio_real" class="ficha-item">
                <span class="ficha-label">Inicio real</span>
                <span class="ficha-value">{{ formatDateTime(detalleGuardia.inicio_real) }}</span>
              </div>
              <div v-if="detalleGuardia.fin_real" class="ficha-item">
                <span class="ficha-label">Fin real</span>
                <span class="ficha-value">{{ formatDateTime(detalleGuardia.fin_real) }}</span>
              </div>
              <div v-if="detalleGuardia.justificada !== null && detalleGuardia.justificada !== undefined" class="ficha-item">
                <span class="ficha-label">Justificada</span>
                <span class="ficha-value">{{ detalleGuardia.justificada ? 'Sí' : 'No' }}</span>
              </div>
              <div v-if="detalleGuardia.motivo_cancelacion" class="ficha-item ficha-full">
                <span class="ficha-label">Motivo de cancelación</span>
                <span class="ficha-value">{{ detalleGuardia.motivo_cancelacion }}</span>
              </div>
              <div v-if="detalleGuardia.motivo_incumplimiento" class="ficha-item ficha-full">
                <span class="ficha-label">Motivo de incumplimiento</span>
                <span class="ficha-value">{{ detalleGuardia.motivo_incumplimiento }}</span>
              </div>
            </div>
          </div>
        </v-card-text>
        <v-card-actions class="pa-6 pt-0">
          <v-spacer />
          <v-btn
            variant="tonal"
            color="info"
            prepend-icon="mdi-clipboard-text-outline"
            class="text-none text-body-1"
            @click="dialogDetalle = false; verIncidencias(detalleGuardia)"
          >
            Ver incidencias
          </v-btn>
          <v-btn variant="text" class="text-none text-body-1" @click="dialogDetalle = false">Cerrar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Marcar llegada -->
    <v-dialog v-model="dialogLlegada" :max-width="xs ? undefined : 460" :fullscreen="xs" persistent>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">
          Marcar llegada
        </v-card-title>
        <v-card-text class="pa-5">
          <div class="text-body-2 text-medium-emphasis mb-4">
            {{ guardiaAccion?.cuadro_nombre }} · {{ formatFecha(guardiaAccion?.fecha) }}
          </div>
          <v-alert v-if="errorLlegada" role="alert" type="error" variant="tonal" density="compact" class="mb-4">
            {{ errorLlegada }}
          </v-alert>
          <v-menu v-model="menuLlegadaFecha" :close-on-content-click="false" location="bottom start">
            <template #activator="{ props: menuProps }">
              <v-text-field
                :model-value="formLlegada.fecha ? formatFecha(formLlegada.fecha) : ''"
                label="Fecha"
                readonly
                append-inner-icon="mdi-calendar"
                variant="outlined"
                density="comfortable"
                v-bind="menuProps"
                class="mb-2"
              />
            </template>
            <v-date-picker v-model="llegadaFechaPicker" color="primary" />
          </v-menu>
          <v-menu v-model="menuLlegadaHora" :close-on-content-click="false" location="bottom start">
            <template #activator="{ props: menuProps }">
              <v-text-field
                :model-value="formLlegada.hora"
                label="Hora de llegada"
                readonly
                append-inner-icon="mdi-clock-outline"
                variant="outlined"
                density="comfortable"
                v-bind="menuProps"
              />
            </template>
            <v-card rounded="lg" class="pa-3">
              <div class="d-flex ga-3 align-center mb-3">
                <v-select v-model="llegadaHora" :items="horasItems" variant="outlined" density="compact" hide-details class="hora-select" />
                <span class="text-h5 text-medium-emphasis">:</span>
                <v-select v-model="llegadaMinuto" :items="minutosItems" variant="outlined" density="compact" hide-details class="minuto-select" />
              </div>
              <div class="d-flex justify-end">
                <v-btn size="small" variant="tonal" color="primary" class="text-none" @click="menuLlegadaHora = false">Listo</v-btn>
              </div>
            </v-card>
          </v-menu>
        </v-card-text>
        <v-card-actions class="pa-5 pt-0">
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="dialogLlegada = false">Cancelar</v-btn>
          <v-btn color="success" :loading="procesando" class="text-none text-body-1" @click="confirmarLlegada">Confirmar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Marcar salida -->
    <v-dialog v-model="dialogSalida" :max-width="xs ? undefined : 460" :fullscreen="xs" persistent>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">
          Marcar salida
        </v-card-title>
        <v-card-text class="pa-5">
          <div class="text-body-2 text-medium-emphasis mb-4">
            {{ guardiaAccion?.cuadro_nombre }} · {{ formatFecha(guardiaAccion?.fecha) }}
          </div>
          <v-alert v-if="errorSalida" role="alert" type="error" variant="tonal" density="compact" class="mb-4">
            {{ errorSalida }}
          </v-alert>
          <v-menu v-model="menuSalidaFecha" :close-on-content-click="false" location="bottom start">
            <template #activator="{ props: menuProps }">
              <v-text-field
                :model-value="formSalida.fecha ? formatFecha(formSalida.fecha) : ''"
                label="Fecha"
                readonly
                append-inner-icon="mdi-calendar"
                variant="outlined"
                density="comfortable"
                v-bind="menuProps"
                class="mb-2"
              />
            </template>
            <v-date-picker v-model="salidaFechaPicker" color="primary" />
          </v-menu>
          <v-menu v-model="menuSalidaHora" :close-on-content-click="false" location="bottom start">
            <template #activator="{ props: menuProps }">
              <v-text-field
                :model-value="formSalida.hora"
                label="Hora de salida"
                readonly
                append-inner-icon="mdi-clock-outline"
                variant="outlined"
                density="comfortable"
                v-bind="menuProps"
              />
            </template>
            <v-card rounded="lg" class="pa-3">
              <div class="d-flex ga-3 align-center mb-3">
                <v-select v-model="salidaHora" :items="horasItems" variant="outlined" density="compact" hide-details class="hora-select" />
                <span class="text-h5 text-medium-emphasis">:</span>
                <v-select v-model="salidaMinuto" :items="minutosItems" variant="outlined" density="compact" hide-details class="minuto-select" />
              </div>
              <div class="d-flex justify-end">
                <v-btn size="small" variant="tonal" color="primary" class="text-none" @click="menuSalidaHora = false">Listo</v-btn>
              </div>
            </v-card>
          </v-menu>
        </v-card-text>
        <v-card-actions class="pa-5 pt-0">
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="dialogSalida = false">Cancelar</v-btn>
          <v-btn color="warning" :loading="procesando" class="text-none text-body-1" @click="confirmarSalida">Registrar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Marcar incumplida -->
    <v-dialog v-model="dialogIncumplir" :max-width="xs ? undefined : 460" :fullscreen="xs" persistent>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">
          Marcar incumplida
        </v-card-title>
        <v-card-text class="pa-5">
          <div class="text-body-2 text-medium-emphasis mb-4">
            {{ guardiaAccion?.cuadro_nombre }} · {{ formatFecha(guardiaAccion?.fecha) }}
          </div>
          <v-alert v-if="errorIncumplir" role="alert" type="error" variant="tonal" density="compact" class="mb-4">
            {{ errorIncumplir }}
          </v-alert>
          <v-textarea
            v-model="motivoIncumplir"
            label="Motivo *"
            variant="outlined"
            density="comfortable"
            rows="3"
            auto-grow
            maxlength="300"
            counter
            class="mb-2"
          />
          <v-switch v-model="justificada" color="primary" label="Justificada" density="comfortable" hide-details />
        </v-card-text>
        <v-card-actions class="pa-5 pt-0">
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="dialogIncumplir = false">Cancelar</v-btn>
          <v-btn color="warning" :loading="procesando" class="text-none text-body-1" @click="confirmarIncumplir">Confirmar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Cancelar guardia -->
    <v-dialog v-model="dialogCancelar" :max-width="xs ? undefined : 460" :fullscreen="xs" persistent>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">
          Cancelar guardia
        </v-card-title>
        <v-card-text class="pa-5">
          <div class="text-body-2 text-medium-emphasis mb-4">
            {{ guardiaAccion?.cuadro_nombre }} · {{ formatFecha(guardiaAccion?.fecha) }}
          </div>
          <v-alert v-if="errorCancelar" role="alert" type="error" variant="tonal" density="compact" class="mb-4">
            {{ errorCancelar }}
          </v-alert>
          <v-textarea
            v-model="motivoCancelar"
            label="Motivo *"
            variant="outlined"
            density="comfortable"
            rows="3"
            auto-grow
            maxlength="300"
            counter
          />
        </v-card-text>
        <v-card-actions class="pa-5 pt-0">
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="dialogCancelar = false">Volver</v-btn>
          <v-btn color="error" :loading="procesando" class="text-none text-body-1" @click="confirmarCancelar">Cancelar guardia</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <IncidenciasGuardiaDialog
      v-model="dialogIncidencias"
      :guardia="guardiaAccion"
      modo="admin"
      :opciones="opciones"
      @changed="cargarGuardias"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useDisplay } from 'vuetify'
import { guardiaCuadroApi } from '../api/guardiaCuadro'
import { cuadroApi } from '../api/cuadro'
import { postaApi } from '../api/posta'
import { aspApi } from '../api/asp'
import { normalizeApiError } from '../utils/error'
import { useToast } from '../composables/useToast'
import SkeletonList from '../components/SkeletonList.vue'
import IncidenciasGuardiaDialog from '../components/IncidenciasGuardiaDialog.vue'

const route = useRoute()
const toast = useToast()
const { mobile, xs } = useDisplay()

const guardias = ref([])
const cargando = ref(true)
const total = ref(0)
const pagina = ref(1)
const tamanoPagina = computed(() => (mobile.value ? 10 : 20))

const periodos = [
  { value: 'hoy', label: 'Hoy' },
  { value: 'semana', label: 'Esta semana' },
  { value: 'mes', label: 'Este mes' },
  { value: 'todo', label: 'Todas' },
]
const periodo = ref('todo')
const desde = ref(null)
const hasta = ref(null)

const filtroCuadro = ref(null)
const filtroEstado = ref(null)
const cuadrosList = ref([])
const buscar = ref('')

const planIdFiltro = ref(route.query.plan_id ? Number(route.query.plan_id) : null)

const estadosItems = [
  { title: 'Planificada', value: 'planificada' },
  { title: 'Activa', value: 'activa' },
  { title: 'Finalizada', value: 'finalizada' },
  { title: 'Incumplida', value: 'incumplida' },
  { title: 'Cancelada', value: 'cancelada' },
]
const estadosInfo = {
  planificada: { color: 'info', label: 'Planificada', icon: 'mdi-calendar-clock' },
  activa: { color: 'success', label: 'Activa', icon: 'mdi-shield-check' },
  finalizada: { color: 'grey', label: 'Finalizada', icon: 'mdi-check-bold' },
  incumplida: { color: 'error', label: 'Incumplida', icon: 'mdi-account-off' },
  cancelada: { color: 'error', label: 'Cancelada', icon: 'mdi-cancel' },
}

const dialogLlegada = ref(false)
const formLlegada = ref({ fecha: '', hora: '' })
const errorLlegada = ref(null)
const menuLlegadaFecha = ref(false)
const menuLlegadaHora = ref(false)

const dialogSalida = ref(false)
const formSalida = ref({ fecha: '', hora: '' })
const errorSalida = ref(null)
const menuSalidaFecha = ref(false)
const menuSalidaHora = ref(false)

const menuDesde = ref(false)
const menuHasta = ref(false)

const horasItems = Array.from({ length: 24 }, (_, i) => String(i).padStart(2, '0'))
const minutosItems = ['00', '05', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55']

function timeToParts(t) {
  if (!t) return { h: '08', m: '00' }
  const [h, m] = t.split(':')
  return { h: h || '08', m: m || '00' }
}
function partsToTime(h, m) {
  return `${h}:${m}`
}

const dialogIncumplir = ref(false)
const motivoIncumplir = ref('')
const justificada = ref(false)
const errorIncumplir = ref(null)

const dialogCancelar = ref(false)
const motivoCancelar = ref('')
const errorCancelar = ref(null)

const dialogDetalle = ref(false)
const detalleGuardia = ref(null)

const dialogIncidencias = ref(false)
const guardiaAccion = ref(null)
const procesando = ref(false)
const opciones = ref({ postas: [], asp: [] })

const totalPaginas = computed(() => Math.max(1, Math.ceil(total.value / tamanoPagina.value)))

const estadoMap = estadosInfo
function estadoLabel(e) { return estadoMap[e]?.label || e }
function estadoColor(e) { return estadoMap[e]?.color || 'grey' }
function estadoIcon(e) { return estadoMap[e]?.icon || 'mdi-help' }

function dateToYMD(d) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${dd}`
}

function ymdToDate(s) {
  if (!s) return null
  const [y, m, d] = s.split('-').map(Number)
  return new Date(y, m - 1, d)
}

const desdePicker = computed({
  get() { return ymdToDate(desde.value) },
  set(val) {
    desde.value = dateToYMD(val)
    periodo.value = 'rango'
    reiniciar()
  },
})

const hastaPicker = computed({
  get() { return ymdToDate(hasta.value) },
  set(val) {
    hasta.value = dateToYMD(val)
    periodo.value = 'rango'
    reiniciar()
  },
})

const llegadaFechaPicker = computed({
  get() { return ymdToDate(formLlegada.value.fecha) },
  set(val) { if (val) formLlegada.value.fecha = dateToYMD(val) },
})

const llegadaHora = computed({
  get() { return timeToParts(formLlegada.value.hora).h },
  set(val) { formLlegada.value.hora = partsToTime(val, timeToParts(formLlegada.value.hora).m) },
})

const llegadaMinuto = computed({
  get() { return timeToParts(formLlegada.value.hora).m },
  set(val) { formLlegada.value.hora = partsToTime(timeToParts(formLlegada.value.hora).h, val) },
})

const salidaFechaPicker = computed({
  get() { return ymdToDate(formSalida.value.fecha) },
  set(val) { if (val) formSalida.value.fecha = dateToYMD(val) },
})

const salidaHora = computed({
  get() { return timeToParts(formSalida.value.hora).h },
  set(val) { formSalida.value.hora = partsToTime(val, timeToParts(formSalida.value.hora).m) },
})

const salidaMinuto = computed({
  get() { return timeToParts(formSalida.value.hora).m },
  set(val) { formSalida.value.hora = partsToTime(timeToParts(formSalida.value.hora).h, val) },
})

function formatFecha(f) {
  if (!f) return ''
  const [y, m, d] = f.split('-')
  return `${d}/${m}/${y}`
}

function formatDateTime(dt) {
  if (!dt) return ''
  const d = dt.replace('T', ' ').slice(0, 16)
  const parts = d.split(' ')
  if (parts.length < 2) return d
  const [y, m, dd] = parts[0].split('-')
  return `${dd}/${m}/${y} ${parts[1]}`
}

function horarioDe(g) {
  const f = g?.franja
  if (!f) return ''
  return `${(f.hora_inicio || '').slice(0, 5)}–${(f.hora_fin || '').slice(0, 5)}`
}

function setPeriodo(value) {
  periodo.value = value
  const hoy = new Date()
  if (value === 'hoy') {
    desde.value = dateToYMD(hoy)
    hasta.value = dateToYMD(hoy)
  } else if (value === 'semana') {
    const dow = (hoy.getDay() + 6) % 7
    const lunes = new Date(hoy)
    lunes.setDate(hoy.getDate() - dow)
    const domingo = new Date(lunes)
    domingo.setDate(lunes.getDate() + 6)
    desde.value = dateToYMD(lunes)
    hasta.value = dateToYMD(domingo)
  } else if (value === 'mes') {
    const primero = new Date(hoy.getFullYear(), hoy.getMonth(), 1)
    const ultimo = new Date(hoy.getFullYear(), hoy.getMonth() + 1, 0)
    desde.value = dateToYMD(primero)
    hasta.value = dateToYMD(ultimo)
  } else {
    desde.value = null
    hasta.value = null
  }
  reiniciar()
}

function limpiarPlan() {
  planIdFiltro.value = null
  reiniciar()
}

function reiniciar() {
  pagina.value = 1
  cargarGuardias()
}

function debounce(fn, ms) {
  let timer = null
  return (...args) => {
    clearTimeout(timer)
    timer = setTimeout(() => fn(...args), ms)
  }
}

const onBuscar = debounce(() => reiniciar(), 300)

async function cargarCuadros() {
  try {
    const todos = []
    let page = 1
    let totalCuadros = 0
    do {
      const res = await cuadroApi.listar({ page, size: 100 })
      todos.push(...(res.data.items || []))
      totalCuadros = res.data.total || 0
      page += 1
    } while (todos.length < totalCuadros)
    cuadrosList.value = todos
      .map((c) => ({ id: c.id, titulo: `${c.nombre} ${c.apellidos || ''}`.trim() }))
      .sort((a, b) => a.titulo.localeCompare(b.titulo, 'es'))
  } catch {
    cuadrosList.value = []
  }
}

async function cargarGuardias() {
  cargando.value = true
  try {
    const params = { page: pagina.value, size: tamanoPagina.value }
    if (desde.value) params.desde = desde.value
    if (hasta.value) params.hasta = hasta.value
    if (filtroCuadro.value) params.cuadro_id = filtroCuadro.value
    if (filtroEstado.value) params.estado = filtroEstado.value
    if (planIdFiltro.value) params.plan_id = planIdFiltro.value
    if (buscar.value?.trim()) params.buscar = buscar.value.trim()
    const res = await guardiaCuadroApi.listar(params)
    guardias.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al cargar las guardias'))
  } finally {
    cargando.value = false
  }
}

function cambiarPagina(delta) {
  const next = pagina.value + delta
  if (next < 1 || next > totalPaginas.value) return
  pagina.value = next
  cargarGuardias().then(() => {
    document.getElementById('main-content')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  })
}

function horaActual() {
  const d = new Date()
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function abrirLlegada(g) {
  guardiaAccion.value = g
  formLlegada.value = { fecha: g.fecha, hora: horaActual() }
  errorLlegada.value = null
  dialogLlegada.value = true
}

async function confirmarLlegada() {
  if (!formLlegada.value.fecha || !formLlegada.value.hora) {
    errorLlegada.value = 'Indique fecha y hora'
    return
  }
  procesando.value = true
  errorLlegada.value = null
  try {
    await guardiaCuadroApi.iniciar(guardiaAccion.value.id, {
      inicio_real: `${formLlegada.value.fecha}T${formLlegada.value.hora}:00`,
    })
    toast.success('Llegada registrada')
    dialogLlegada.value = false
    await cargarGuardias()
  } catch (e) {
    errorLlegada.value = normalizeApiError(e, 'No se pudo registrar la llegada')
  } finally {
    procesando.value = false
  }
}

function fechaSalidaPorDefecto(g) {
  const f = g?.franja
  const cruzaMedianoche = f && f.hora_fin < f.hora_inicio
  const ahora = new Date()
  if (cruzaMedianoche && ahora.getHours() < 12) {
    const d = ymdToDate(g.fecha)
    d.setDate(d.getDate() + 1)
    return dateToYMD(d)
  }
  return g?.fecha || dateToYMD(ahora)
}

function abrirSalida(g) {
  guardiaAccion.value = g
  formSalida.value = { fecha: fechaSalidaPorDefecto(g), hora: horaActual() }
  errorSalida.value = null
  dialogSalida.value = true
}

async function confirmarSalida() {
  if (!formSalida.value.fecha || !formSalida.value.hora) {
    errorSalida.value = 'Indique fecha y hora'
    return
  }
  procesando.value = true
  errorSalida.value = null
  try {
    await guardiaCuadroApi.finalizar(guardiaAccion.value.id, {
      fin_real: `${formSalida.value.fecha}T${formSalida.value.hora}:00`,
    })
    toast.success('Salida registrada')
    dialogSalida.value = false
    await cargarGuardias()
  } catch (e) {
    errorSalida.value = normalizeApiError(e, 'No se pudo registrar la salida')
  } finally {
    procesando.value = false
  }
}

function abrirIncumplir(g) {
  guardiaAccion.value = g
  motivoIncumplir.value = ''
  justificada.value = false
  errorIncumplir.value = null
  dialogIncumplir.value = true
}

async function confirmarIncumplir() {
  if (!motivoIncumplir.value.trim()) {
    errorIncumplir.value = 'El motivo es obligatorio'
    return
  }
  procesando.value = true
  errorIncumplir.value = null
  try {
    await guardiaCuadroApi.incumplir(guardiaAccion.value.id, {
      motivo: motivoIncumplir.value.trim(),
      justificada: justificada.value,
    })
    toast.success('Guardia marcada como incumplida')
    dialogIncumplir.value = false
    await cargarGuardias()
  } catch (e) {
    errorIncumplir.value = normalizeApiError(e, 'No se pudo marcar la guardia como incumplida')
  } finally {
    procesando.value = false
  }
}

function abrirCancelar(g) {
  guardiaAccion.value = g
  motivoCancelar.value = ''
  errorCancelar.value = null
  dialogCancelar.value = true
}

async function confirmarCancelar() {
  if (!motivoCancelar.value.trim()) {
    errorCancelar.value = 'El motivo es obligatorio'
    return
  }
  procesando.value = true
  errorCancelar.value = null
  try {
    await guardiaCuadroApi.cancelar(guardiaAccion.value.id, { motivo: motivoCancelar.value.trim() })
    toast.success('Guardia cancelada')
    dialogCancelar.value = false
    await cargarGuardias()
  } catch (e) {
    errorCancelar.value = normalizeApiError(e, 'No se pudo cancelar la guardia')
  } finally {
    procesando.value = false
  }
}

function abrirDetalle(g) {
  detalleGuardia.value = g
  dialogDetalle.value = true
}

function verIncidencias(g) {
  guardiaAccion.value = g
  dialogIncidencias.value = true
}

async function cargarOpciones() {
  const [p, a] = await Promise.allSettled([
    postaApi.listar({ page: 1, size: 100, activa: true }),
    aspApi.listar({ page: 1, size: 100, estado: 'activo' }),
  ])
  opciones.value = {
    postas:
      p.status === 'fulfilled'
        ? (p.value.data.items || []).map((x) => ({ id: x.id, nombre: x.nombre }))
        : [],
    asp:
      a.status === 'fulfilled'
        ? (a.value.data.items || []).map((x) => ({
            id: x.id,
            nombre: `${x.nombre} ${x.apellidos || ''}`.trim(),
          }))
        : [],
  }
}

onMounted(() => {
  setPeriodo('todo')
  cargarCuadros()
  cargarOpciones()
})
</script>

<style scoped>
.guardias-cuadro-page {
  width: 100%;
}

.filtro,
.filtro-cuadro,
.filtro-fecha {
  min-width: 180px;
  max-width: 240px;
}

.buscador {
  flex-grow: 1;
}

.guardias-mobile-list {
  display: flex;
  flex-direction: column;
}

.guardias-mobile-card {
  border: 1px solid rgb(var(--v-border-color));
  border-radius: 12px;
  background: rgb(var(--v-theme-surface));
}

.ficha-section-title {
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: rgba(0, 0, 0, 0.45);
}

.ficha-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px 24px;
}

.ficha-full {
  grid-column: 1 / -1;
}

.ficha-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.ficha-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.45);
}

.ficha-value {
  font-size: 0.9375rem;
  color: rgba(0, 0, 0, 0.87);
  line-height: 1.4;
}

.hora-select,
.minuto-select {
  min-width: 70px;
}

@media (max-width: 599px) {
  .filtro,
  .filtro-cuadro,
  .filtro-fecha {
    min-width: 0;
    max-width: 100%;
    width: 100%;
    flex: none;
  }

  .ficha-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}
</style>
