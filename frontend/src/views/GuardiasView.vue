<template>
  <div class="guardias-page mx-auto">
    <div class="d-flex align-center justify-end mb-6">
      <v-btn color="primary" prepend-icon="mdi-plus" @click="abrirCrear">
        Nueva Guardia
      </v-btn>
    </div>

    <v-card rounded="lg" class="pa-sm-5 pa-3">
      <div class="d-flex flex-column flex-sm-row align-sm-center justify-sm-space-between mb-4 ga-3">
        <v-text-field
          v-model="buscarAsp"
          prepend-inner-icon="mdi-magnify"
          placeholder="Buscar por ASP..."
          variant="solo-filled"
          density="compact"
          hide-details
          clearable
          bg-color="grey-lighten-4"
          class="guardias-search"
          @update:model-value="onBuscar"
        />
        <div class="d-flex flex-column flex-sm-row align-sm-center ga-3">
          <div class="d-flex flex-wrap ga-2 justify-center">
            <v-menu location="bottom start">
              <template #activator="{ props: menuProps }">
                <v-text-field
                  :model-value="filtroFecha || ''"
                  label="Fecha"
                  readonly
                  append-inner-icon="mdi-calendar"
                  variant="solo-filled"
                  density="compact"
                  hide-details
                  clearable
                  bg-color="grey-lighten-4"
                  class="guardias-fecha"
                  v-bind="menuProps"
                  @click:clear="filtroFecha = null; pagina = 1; cargarGuardias()"
                />
              </template>
              <v-date-picker
                v-model="fechaPicker"
                color="primary"
                @update:model-value="onFechaSelect"
              />
            </v-menu>
          </div>
          <div class="d-flex flex-wrap ga-2 justify-center">
            <v-btn
              v-for="e in estadosItems"
              :key="e.value"
              :variant="filtroEstado === e.value ? 'flat' : 'outlined'"
              :color="filtroEstado === e.value ? e.color : 'default'"
              size="small"
              class="text-none"
              @click="filtroEstado = filtroEstado === e.value ? null : e.value"
            >
              {{ e.label }}
            </v-btn>
          </div>
          <div v-if="total > 0" class="text-body-2 text-medium-emphasis text-center">
            {{ total }} resultado{{ total !== 1 ? 's' : '' }}
          </div>
        </div>
      </div>

      <div aria-live="polite">
        <SkeletonList v-if="cargando" :filas="6" />

        <Transition name="fade-up" mode="out-in">
          <div v-if="!cargando && guardias.length === 0" key="empty" class="text-center py-12">
            <v-icon icon="mdi-shield-check-outline" size="48" color="grey-lighten-1" class="mb-2" />
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
                  <div class="text-body-1 font-weight-medium">{{ aspNombre(g.asp_id) }}</div>
                  <div class="text-body-2 text-medium-emphasis">{{ postaName(g.turno_posta_id) }}</div>
                </div>
              </div>
              <v-chip :color="estadoColor(g.estado)" variant="elevated" size="x-small" label class="font-weight-bold">
                {{ estadoLabel(g.estado) }}
              </v-chip>
            </div>
            <div class="text-body-2 text-medium-emphasis mb-2">
              {{ turnoName(g.turno_posta_id) }} · {{ turnoHorario(g.turno_posta_id) }}
            </div>
            <div class="d-flex align-center justify-space-between text-body-2 text-medium-emphasis mb-2">
              <span>{{ formatFecha(g.fecha) }}</span>
              <span v-if="g.tardanza_minutos > 0" class="text-error font-weight-medium">+{{ g.tardanza_minutos }} min</span>
            </div>
            <div class="d-flex justify-end ga-1">
              <v-btn icon size="x-small" variant="text" aria-label="Ver detalle" @click="abrirDetalle(g)">
                <v-icon icon="mdi-eye-outline" size="16" />
              </v-btn>
              <v-btn
                v-if="g.estado === 'planificada'"
                icon size="x-small" variant="text" color="success"
                aria-label="Confirmar llegada"
                @click="abrirConfirmar(g)"
              >
                <v-icon icon="mdi-clock-check-outline" size="16" />
              </v-btn>
              <v-btn
                v-if="g.estado === 'planificada'"
                icon size="x-small" variant="text" color="warning"
                aria-label="Marcar ausente"
                @click="abrirAusente(g)"
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
                v-if="g.estado === 'activa'"
                icon size="x-small" variant="text" color="warning"
                aria-label="Finalizar guardia"
                @click="abrirFinalizar(g)"
              >
                <v-icon icon="mdi-stop-circle-outline" size="16" />
              </v-btn>
              <v-btn
                v-if="g.estado === 'activa'"
                icon size="x-small" variant="text" color="info"
                aria-label="Registrar novedad"
                @click="abrirNovedad(g)"
              >
                <v-icon icon="mdi-note-plus-outline" size="16" />
              </v-btn>
            </div>
          </div>
        </div>

        <!-- Desktop: table -->
        <v-table v-else-if="!cargando && guardias.length > 0" key="table" density="comfortable">
          <thead>
            <tr>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">ASP</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">Posta</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">Turno</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">Fecha</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">Estado</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">Tardanza</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="g in guardias" :key="g.id">
              <td class="font-weight-medium text-body-1">{{ aspNombre(g.asp_id) }}</td>
              <td class="text-body-1 text-medium-emphasis">{{ postaName(g.turno_posta_id) }}</td>
              <td class="text-body-1">
                {{ turnoName(g.turno_posta_id) }}
                <span class="text-body-2 text-medium-emphasis ms-1">{{ turnoHorario(g.turno_posta_id) }}</span>
              </td>
              <td class="text-body-1">{{ formatFecha(g.fecha) }}</td>
              <td>
                <v-chip :color="estadoColor(g.estado)" variant="elevated" size="small" label class="font-weight-bold">
                  {{ estadoLabel(g.estado) }}
                </v-chip>
              </td>
              <td class="text-body-1">
                <span v-if="g.tardanza_minutos > 0" class="text-error font-weight-medium">+{{ g.tardanza_minutos }} min</span>
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
                <v-tooltip v-if="g.estado === 'planificada'" text="Confirmar llegada" location="top">
                  <template #activator="{ props: tipProps }">
                    <v-btn icon size="small" variant="text" color="success" aria-label="Confirmar llegada" v-bind="tipProps" @click="abrirConfirmar(g)">
                      <v-icon icon="mdi-clock-check-outline" size="18" />
                    </v-btn>
                  </template>
                </v-tooltip>
                <v-tooltip v-if="g.estado === 'planificada'" text="Marcar ausente" location="top">
                  <template #activator="{ props: tipProps }">
                    <v-btn icon size="small" variant="text" color="warning" aria-label="Marcar ausente" v-bind="tipProps" @click="abrirAusente(g)">
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
                <v-tooltip v-if="g.estado === 'activa'" text="Finalizar" location="top">
                  <template #activator="{ props: tipProps }">
                    <v-btn icon size="small" variant="text" color="warning" aria-label="Finalizar guardia" v-bind="tipProps" @click="abrirFinalizar(g)">
                      <v-icon icon="mdi-stop-circle-outline" size="18" />
                    </v-btn>
                  </template>
                </v-tooltip>
                <v-tooltip v-if="g.estado === 'activa'" text="Registrar novedad" location="top">
                  <template #activator="{ props: tipProps }">
                    <v-btn icon size="small" variant="text" color="info" aria-label="Registrar novedad" v-bind="tipProps" @click="abrirNovedad(g)">
                      <v-icon icon="mdi-note-plus-outline" size="18" />
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
    <v-dialog v-model="dialogDetalle" :max-width="mobile ? undefined : 650" :fullscreen="mobile">
      <v-card rounded="lg" v-if="detalleGuardia">
        <v-card-title class="d-flex align-center justify-space-between pa-6 pb-2">
          <div class="d-flex align-center ga-3">
            <v-avatar :color="estadoColor(detalleGuardia.estado)" size="36" rounded="lg">
              <v-icon :icon="estadoIcon(detalleGuardia.estado)" size="18" color="white" />
            </v-avatar>
            <div>
              <span class="text-h6 font-weight-bold">{{ aspNombre(detalleGuardia.asp_id) }}</span>
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
                <span class="ficha-label">ASP</span>
                <span class="ficha-value">{{ aspNombre(detalleGuardia.asp_id) }}</span>
              </div>
              <div class="ficha-item">
                <span class="ficha-label">Fecha</span>
                <span class="ficha-value">{{ formatFecha(detalleGuardia.fecha) }}</span>
              </div>
              <div class="ficha-item">
                <span class="ficha-label">Turno</span>
                <span class="ficha-value">{{ turnoDetalle(detalleGuardia.turno_posta_id) }}</span>
              </div>
              <div class="ficha-item">
                <span class="ficha-label">Tardanza</span>
                <span class="ficha-value">
                  <span v-if="detalleGuardia.tardanza_minutos > 0" class="text-error">+{{ detalleGuardia.tardanza_minutos }} min</span>
                  <span v-else>Sin tardanza</span>
                </span>
              </div>
              <div v-if="detalleGuardia.hora_inicio_real" class="ficha-item">
                <span class="ficha-label">Hora llegada</span>
                <span class="ficha-value">{{ formatDateTime(detalleGuardia.hora_inicio_real) }}</span>
              </div>
              <div v-if="detalleGuardia.hora_fin_real" class="ficha-item">
                <span class="ficha-label">Hora fin</span>
                <span class="ficha-value">{{ formatDateTime(detalleGuardia.hora_fin_real) }}</span>
              </div>
              <div v-if="detalleGuardia.motivo_ausencia" class="ficha-item ficha-full">
                <span class="ficha-label">Motivo ausencia</span>
                <span class="ficha-value">{{ detalleGuardia.motivo_ausencia }}</span>
              </div>
              <div v-if="detalleGuardia.observaciones" class="ficha-item ficha-full">
                <span class="ficha-label">Observaciones</span>
                <span class="ficha-value">{{ detalleGuardia.observaciones }}</span>
              </div>
            </div>
          </div>

          <v-divider class="mb-5" />

          <div class="ficha-section">
            <div class="d-flex align-center justify-space-between mb-3">
              <div class="ficha-section-title">Novedades</div>
              <v-btn
                v-if="detalleGuardia.estado === 'activa'"
                size="small"
                variant="tonal"
                color="primary"
                prepend-icon="mdi-plus"
                class="text-none"
                @click="dialogDetalle = false; abrirNovedad(detalleGuardia)"
              >
                Agregar novedad
              </v-btn>
            </div>
            <div v-if="!detalleGuardia.novedades || detalleGuardia.novedades.length === 0" class="text-body-2 text-medium-emphasis py-4 text-center">
              No hay novedades registradas
            </div>
            <div v-else class="novedades-list">
              <div v-for="n in detalleGuardia.novedades" :key="n.id" class="novedad-item pa-3 mb-2">
                <div class="d-flex align-center justify-space-between mb-1">
                  <div class="d-flex align-center ga-2">
                    <v-chip :color="severidadColor(n.severidad)" size="x-small" variant="tonal" label>
                      {{ n.tipo }}
                    </v-chip>
                    <v-chip :color="severidadColor(n.severidad)" size="x-small" variant="elevated" label class="font-weight-bold">
                      {{ n.severidad }}
                    </v-chip>
                  </div>
                  <span class="text-body-2 text-medium-emphasis">{{ formatDateTime(n.fecha_hora) }}</span>
                </div>
                <p class="text-body-2 mt-1 mb-0">{{ n.descripcion }}</p>
              </div>
            </div>
          </div>
        </v-card-text>
        <v-card-actions class="pa-6 pt-0">
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="dialogDetalle = false">Cerrar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog crear guardia -->
    <v-dialog v-model="dialogForm" :max-width="mobile ? undefined : 520" :fullscreen="mobile" persistent scrollable>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">
          {{ editando ? 'Editar Guardia' : 'Nueva Guardia' }}
        </v-card-title>
        <v-card-text class="pa-5">
          <v-alert
            role="alert"
            v-if="errores._global"
            type="error"
            variant="tonal"
            density="compact"
            closable
            class="mb-4"
            @click:close="errores._global = null"
          >
            {{ errores._global }}
          </v-alert>
          <v-form @submit.prevent="guardar">
            <v-autocomplete
              v-model="form.asp_id"
              label="ASP *"
              :items="aspsList"
              :item-title="item => `${item.nombre} ${item.apellidos} (${item.ci})`"
              item-value="id"
              variant="outlined"
              density="comfortable"
              :error-messages="errores.asp_id"
              :disabled="!!editando"
              class="mb-3"
            />
            <v-autocomplete
              v-model="form.turno_posta_id"
              label="Turno *"
              :items="turnosList"
              :item-title="item => `${item.posta_nombre} — ${item.nombre} (${item.hora_inicio?.slice(0,5)}-${item.hora_fin?.slice(0,5)})`"
              item-value="id"
              variant="outlined"
              density="comfortable"
              :error-messages="errores.turno_posta_id"
              :disabled="!!editando"
              class="mb-3"
            />
            <v-menu v-model="menuFecha" :close-on-content-click="false" location="bottom start">
              <template #activator="{ props: menuProps }">
                <v-text-field
                  :model-value="form.fecha || ''"
                  label="Fecha *"
                  readonly
                  append-inner-icon="mdi-calendar"
                  variant="outlined"
                  density="comfortable"
                  :error-messages="errores.fecha"
                  :disabled="!!editando"
                  v-bind="menuProps"
                  class="mb-1"
                />
              </template>
              <v-date-picker v-model="fechaFormDate" color="primary" />
            </v-menu>
            <v-textarea
              v-if="!editando"
              v-model="form.observaciones"
              label="Observaciones (opcional)"
              variant="outlined"
              density="comfortable"
              rows="2"
              auto-grow
              class="mb-1"
            />
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-5 pt-0">
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="cerrarForm">Cancelar</v-btn>
          <v-tooltip :disabled="formValido" location="top">
            <template #activator="{ props: tipProps }">
              <span v-bind="tipProps">
                <v-btn
                  color="primary"
                  :disabled="!formValido"
                  :loading="guardando"
                  class="text-none text-body-1"
                  @click="guardar"
                >
                  {{ editando ? 'Actualizar' : 'Crear' }}
                </v-btn>
              </span>
            </template>
            <span>Complete ASP, turno y fecha</span>
          </v-tooltip>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog confirmar llegada -->
    <v-dialog v-model="dialogConfirmar" :max-width="mobile ? undefined : 400" persistent>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">Confirmar Llegada</v-card-title>
        <v-card-text class="pa-5">
          <v-alert
            role="alert"
            v-if="erroresConfirmar._global"
            type="error"
            variant="tonal"
            density="compact"
            closable
            class="mb-4"
            @click:close="erroresConfirmar._global = null"
          >
            {{ erroresConfirmar._global }}
          </v-alert>
          <v-form @submit.prevent="confirmarLlegada">
            <v-menu v-model="menuLlegada" :close-on-content-click="false" location="bottom start">
              <template #activator="{ props: menuProps }">
                <v-text-field
                  :model-value="formLlegadaDisplay"
                  label="Hora de llegada *"
                  readonly
                  append-inner-icon="mdi-clock-outline"
                  variant="outlined"
                  density="comfortable"
                  :error-messages="erroresConfirmar.hora_llegada"
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
                  <v-btn size="small" variant="tonal" color="primary" class="text-none" @click="menuLlegada = false">Listo</v-btn>
                </div>
              </v-card>
            </v-menu>
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-5 pt-0">
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="dialogConfirmar = false">Cancelar</v-btn>
          <v-btn
            color="success"
            :disabled="!formLlegada.hora"
            :loading="guardandoAccion"
            class="text-none text-body-1"
            @click="confirmarLlegada"
          >
            Confirmar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog finalizar guardia -->
    <v-dialog v-model="dialogFinalizar" :max-width="mobile ? undefined : 480" persistent scrollable>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">Finalizar Guardia</v-card-title>
        <v-card-text class="pa-5">
          <v-alert
            role="alert"
            v-if="erroresFinalizar._global"
            type="error"
            variant="tonal"
            density="compact"
            closable
            class="mb-4"
            @click:close="erroresFinalizar._global = null"
          >
            {{ erroresFinalizar._global }}
          </v-alert>
          <v-form @submit.prevent="finalizarGuardia">
            <v-menu v-model="menuFin" :close-on-content-click="false" location="bottom start">
              <template #activator="{ props: menuProps }">
                <v-text-field
                  :model-value="formFinDisplay"
                  label="Hora de fin *"
                  readonly
                  append-inner-icon="mdi-clock-outline"
                  variant="outlined"
                  density="comfortable"
                  :error-messages="erroresFinalizar.hora_fin_real"
                  v-bind="menuProps"
                  class="mb-3"
                />
              </template>
              <v-card rounded="lg" class="pa-3">
                <div class="d-flex ga-3 align-center mb-3">
                  <v-select v-model="finHora" :items="horasItems" variant="outlined" density="compact" hide-details class="hora-select" />
                  <span class="text-h5 text-medium-emphasis">:</span>
                  <v-select v-model="finMinuto" :items="minutosItems" variant="outlined" density="compact" hide-details class="minuto-select" />
                </div>
                <div class="d-flex justify-end">
                  <v-btn size="small" variant="tonal" color="primary" class="text-none" @click="menuFin = false">Listo</v-btn>
                </div>
              </v-card>
            </v-menu>
            <v-textarea
              v-model="formFin.observaciones"
              label="Observaciones (opcional)"
              variant="outlined"
              density="comfortable"
              rows="2"
              auto-grow
            />
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-5 pt-0">
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="dialogFinalizar = false">Cancelar</v-btn>
          <v-btn
            color="warning"
            :disabled="!formFin.hora_fin_real"
            :loading="guardandoAccion"
            class="text-none text-body-1"
            @click="finalizarGuardia"
          >
            Finalizar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog marcar ausente -->
    <v-dialog v-model="dialogAusente" :max-width="mobile ? undefined : 480" persistent scrollable>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">Marcar como Ausente</v-card-title>
        <v-card-text class="pa-5">
          <v-alert
            role="alert"
            v-if="erroresAusente._global"
            type="error"
            variant="tonal"
            density="compact"
            closable
            class="mb-4"
            @click:close="erroresAusente._global = null"
          >
            {{ erroresAusente._global }}
          </v-alert>
          <v-form @submit.prevent="marcarAusente">
            <v-radio-group
              v-model="formAusente.justificada"
              color="warning"
              density="compact"
              class="mb-3"
            >
              <v-radio label="Justificada" value="justificada" />
              <v-radio label="No justificada" value="no_justificada" />
            </v-radio-group>
            <v-textarea
              v-if="formAusente.justificada === 'justificada'"
              v-model="formAusente.motivo_ausencia"
              label="Motivo de ausencia *"
              variant="outlined"
              density="comfortable"
              rows="3"
              auto-grow
              :error-messages="erroresAusente.motivo_ausencia"
              class="mb-3"
            />
            <v-textarea
              v-model="formAusente.observaciones"
              label="Observaciones (opcional)"
              variant="outlined"
              density="comfortable"
              rows="2"
              auto-grow
              class="mb-1"
            />
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-5 pt-0">
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="dialogAusente = false">Cancelar</v-btn>
          <v-tooltip
            :disabled="formAusente.justificada !== 'justificada' || !!formAusente.motivo_ausencia?.trim()"
            location="top"
          >
            <template #activator="{ props: tipProps }">
              <span v-bind="tipProps">
                <v-btn
                  color="warning"
                  :disabled="
                    !formAusente.justificada ||
                    (formAusente.justificada === 'justificada' && !formAusente.motivo_ausencia?.trim())
                  "
                  :loading="guardandoAccion"
                  class="text-none text-body-1"
                  @click="marcarAusente"
                >
                  Marcar ausente
                </v-btn>
              </span>
            </template>
            <span>Indique el motivo de ausencia</span>
          </v-tooltip>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog cancelar guardia -->
    <v-dialog v-model="dialogCancelar" :max-width="mobile ? undefined : 480" persistent scrollable>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">Cancelar Guardia</v-card-title>
        <v-card-text class="pa-5">
          <v-alert
            role="alert"
            v-if="erroresCancelar._global"
            type="error"
            variant="tonal"
            density="compact"
            closable
            class="mb-4"
            @click:close="erroresCancelar._global = null"
          >
            {{ erroresCancelar._global }}
          </v-alert>
          <p class="text-body-2 text-medium-emphasis mb-4">
            La guardia de <strong>{{ guardiaCancelar ? aspNombre(guardiaCancelar.asp_id) : '' }}</strong>
            del <strong>{{ guardiaCancelar ? formatFecha(guardiaCancelar.fecha) : '' }}</strong> quedará cancelada.
          </p>
          <v-form @submit.prevent="cancelarGuardia">
            <v-text-field
              v-model="formCancelar.motivo"
              label="Motivo (opcional)"
              variant="outlined"
              density="comfortable"
              :error-messages="erroresCancelar.motivo"
              class="mb-3"
            />
            <v-textarea
              v-model="formCancelar.observaciones"
              label="Observaciones (opcional)"
              variant="outlined"
              density="comfortable"
              rows="2"
              auto-grow
              class="mb-1"
            />
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-5 pt-0">
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="dialogCancelar = false">Volver</v-btn>
          <v-btn
            color="error"
            :loading="guardandoAccion"
            class="text-none text-body-1"
            @click="cancelarGuardia"
          >
            Cancelar guardia
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog registrar novedad -->
    <v-dialog v-model="dialogNovedad" :max-width="mobile ? undefined : 480" persistent>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">Registrar Novedad</v-card-title>
        <v-card-text class="pa-5">
          <v-alert
            role="alert"
            v-if="erroresNovedad._global"
            type="error"
            variant="tonal"
            density="compact"
            closable
            class="mb-4"
            @click:close="erroresNovedad._global = null"
          >
            {{ erroresNovedad._global }}
          </v-alert>
          <v-form @submit.prevent="registrarNovedad">
            <v-select
              v-model="formNovedad.tipo"
              label="Tipo *"
              :items="tipoNovedadItems"
              item-title="label"
              item-value="value"
              variant="outlined"
              density="comfortable"
              :error-messages="erroresNovedad.tipo"
              class="mb-3"
            />
            <v-textarea
              v-model="formNovedad.descripcion"
              label="Descripción *"
              variant="outlined"
              density="comfortable"
              :error-messages="erroresNovedad.descripcion"
              rows="3"
              auto-grow
              class="mb-3"
            />
            <v-select
              v-model="formNovedad.severidad"
              label="Severidad"
              :items="severidadItems"
              item-title="label"
              item-value="value"
              variant="outlined"
              density="comfortable"
            />
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-5 pt-0">
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="dialogNovedad = false">Cancelar</v-btn>
          <v-btn
            color="primary"
            :disabled="!formNovedad.tipo || !formNovedad.descripcion.trim()"
            :loading="guardandoAccion"
            class="text-none text-body-1"
            @click="registrarNovedad"
          >
            Registrar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useDisplay } from 'vuetify'
import { guardiaApi } from '../api/guardia'
import { postaApi } from '../api/posta'
import { aspApi } from '../api/asp'
import { normalizeApiError } from '../utils/error'
import { useToast } from '../composables/useToast'
import SkeletonList from '../components/SkeletonList.vue'

const toast = useToast()
const { mobile } = useDisplay()
const route = useRoute()

const guardias = ref([])
const cargando = ref(true)
const total = ref(0)
const pagina = ref(1)
const tamanoPagina = computed(() => mobile.value ? 10 : 20)
const buscarAsp = ref('')
const filtroFecha = ref(null)
const filtroEstado = ref(null)

const aspsList = ref([])
const turnosList = ref([])
const aspMap = ref({})
const turnoMap = ref({})

const dialogDetalle = ref(false)
const detalleGuardia = ref(null)

const dialogForm = ref(false)
const editando = ref(null)
const guardando = ref(false)
const form = ref(emptyForm())
const errores = ref({})

const dialogConfirmar = ref(false)
const guardiaConfirmar = ref(null)
const guardandoAccion = ref(false)
const formLlegada = ref({ hora: '', fecha: '' })
const erroresConfirmar = ref({})

const dialogFinalizar = ref(false)
const guardiaFinalizar = ref(null)
const formFin = ref({ hora_fin_real: '', observaciones: '' })
const erroresFinalizar = ref({})

const dialogAusente = ref(false)
const guardiaAusente = ref(null)
const formAusente = ref({ justificada: null, motivo_ausencia: '', observaciones: '' })
const erroresAusente = ref({})

const dialogCancelar = ref(false)
const guardiaCancelar = ref(null)
const formCancelar = ref({ motivo: '', observaciones: '' })
const erroresCancelar = ref({})

const dialogNovedad = ref(false)
const guardiaNovedad = ref(null)
const formNovedad = ref(emptyNovedadForm())
const erroresNovedad = ref({})

const menuFecha = ref(false)
const menuLlegada = ref(false)
const menuFin = ref(false)

const estadosItems = [
  { label: 'Planificada', value: 'planificada', color: 'blue' },
  { label: 'Activa', value: 'activa', color: 'success' },
  { label: 'Finalizada', value: 'finalizada', color: 'grey' },
  { label: 'Ausente', value: 'ausente', color: 'warning' },
  { label: 'Cancelada', value: 'cancelada', color: 'error' },
]

const tipoNovedadItems = [
  { label: 'Incidente', value: 'incidente' },
  { label: 'Comunicado', value: 'comunicado' },
  { label: 'Entrega/Recepción', value: 'entrega_recepcion' },
  { label: 'Solicitud', value: 'solicitud' },
  { label: 'Otro', value: 'otro' },
]

const severidadItems = [
  { label: 'Baja', value: 'baja' },
  { label: 'Media', value: 'media' },
  { label: 'Alta', value: 'alta' },
  { label: 'Crítica', value: 'critica' },
]

const horasItems = Array.from({ length: 24 }, (_, i) => String(i).padStart(2, '0'))
const minutosItems = ['00', '05', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55']

const estadoMap = Object.fromEntries(estadosItems.map(e => [e.value, e]))
const totalPaginas = computed(() => Math.max(1, Math.ceil(total.value / tamanoPagina.value)))
const formValido = computed(() => {
  const f = form.value
  return f.asp_id && f.turno_posta_id && f.fecha
})

function estadoLabel(e) { return estadoMap[e]?.label || e }
function estadoColor(e) { return estadoMap[e]?.color || 'grey' }
function estadoIcon(e) {
  const icons = { planificada: 'mdi-calendar-clock', activa: 'mdi-shield-check', finalizada: 'mdi-check-bold', ausente: 'mdi-account-off', cancelada: 'mdi-cancel' }
  return icons[e] || 'mdi-help'
}
function severidadColor(s) {
  return { baja: 'grey', media: 'info', alta: 'warning', critica: 'error' }[s] || 'grey'
}

function aspNombre(id) {
  const asp = aspMap.value[id]
  return asp ? `${asp.nombre} ${asp.apellidos}` : `ASP #${id}`
}

function postaName(id) {
  const t = turnoMap.value[id]
  return t ? t.posta_nombre : `Turno #${id}`
}

function turnoName(id) {
  const t = turnoMap.value[id]
  return t ? t.nombre : `#${id}`
}

function turnoHorario(id) {
  const t = turnoMap.value[id]
  return t ? `${t.hora_inicio?.slice(0, 5)}-${t.hora_fin?.slice(0, 5)}` : ''
}

function turnoDetalle(id) {
  const t = turnoMap.value[id]
  return t ? `${t.posta_nombre} — ${t.nombre} (${t.hora_inicio?.slice(0, 5)}-${t.hora_fin?.slice(0, 5)})` : `Turno #${id}`
}

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

function dateToYMD(d) {
  if (!d) return ''
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

const fechaPicker = computed({
  get() { return ymdToDate(filtroFecha.value) },
  set(val) {
    filtroFecha.value = dateToYMD(val)
    menuFecha.value = false
    pagina.value = 1
    cargarGuardias()
  },
})

const fechaFormDate = computed({
  get() { return ymdToDate(form.value.fecha) },
  set(val) {
    form.value.fecha = dateToYMD(val)
    menuFecha.value = false
  },
})

function timeToParts(t) {
  if (!t) return { h: '08', m: '00' }
  const [h, m] = t.split(':')
  return { h: h || '08', m: m || '00' }
}
function partsToTime(h, m) { return `${h}:${m}` }

const llegadaHora = computed({
  get() { return timeToParts(formLlegada.value.hora).h },
  set(val) { formLlegada.value.hora = partsToTime(val, timeToParts(formLlegada.value.hora).m) },
})
const llegadaMinuto = computed({
  get() { return timeToParts(formLlegada.value.hora).m },
  set(val) { formLlegada.value.hora = partsToTime(timeToParts(formLlegada.value.hora).h, val) },
})
const finHora = computed({
  get() { return timeToParts(formFin.value.hora_fin_real).h },
  set(val) { formFin.value.hora_fin_real = partsToTime(val, timeToParts(formFin.value.hora_fin_real).m) },
})
const finMinuto = computed({
  get() { return timeToParts(formFin.value.hora_fin_real).m },
  set(val) { formFin.value.hora_fin_real = partsToTime(timeToParts(formFin.value.hora_fin_real).h, val) },
})

const formLlegadaDisplay = computed(() => formLlegada.value.hora || '')
const formFinDisplay = computed(() => formFin.value.hora_fin_real || '')

function emptyForm() {
  return { asp_id: null, turno_posta_id: null, fecha: '', observaciones: '' }
}
function emptyNovedadForm() {
  return { tipo: null, descripcion: '', severidad: 'baja' }
}

function debounce(fn, ms) {
  let timer
  return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), ms) }
}

const onBuscar = debounce(() => { pagina.value = 1; cargarGuardias() }, 300)

async function cargarListas() {
  try {
    const results = await Promise.allSettled([
      aspApi.listar({ size: 100 }),
      postaApi.listarTurnos({ size: 100 }),
      postaApi.listar({ size: 100, activa: true }),
    ])
    if (results[0].status === 'fulfilled') {
      const allAsps = results[0].value.data.items || []
      aspsList.value = allAsps.filter(a => a.estado === 'activo')
      aspMap.value = Object.fromEntries(allAsps.map(a => [a.id, a]))
      aspsList.value.sort((a, b) => `${a.nombre} ${a.apellidos}`.localeCompare(`${b.nombre} ${b.apellidos}`, 'es'))
    } else {
      toast.error('Error al cargar ASPs')
    }
    if (results[1].status === 'fulfilled') {
      const allTurnos = results[1].value.data.items || []
      turnoMap.value = Object.fromEntries(allTurnos.map(t => [t.id, t]))
      const postasActivas = new Set(
        results[2].status === 'fulfilled'
          ? (results[2].value.data.items || []).map(p => p.id)
          : allTurnos.map(t => t.posta_id)
      )
      turnosList.value = allTurnos.filter(t => t.activo && postasActivas.has(t.posta_id))
      turnosList.value.sort((a, b) => `${a.posta_nombre} ${a.nombre}`.localeCompare(`${b.posta_nombre} ${b.nombre}`, 'es'))
    } else {
      toast.error('Error al cargar turnos')
    }
  } catch {
    toast.error('Error al cargar datos')
  }
}

async function cargarGuardias() {
  cargando.value = true
  try {
    const params = { page: pagina.value, size: tamanoPagina.value }
    if (filtroFecha.value) params.fecha = filtroFecha.value
    if (filtroEstado.value) params.estado = filtroEstado.value
    if (buscarAsp.value?.trim()) {
      const found = aspsList.value.find(a => {
        const full = `${a.nombre} ${a.apellidos}`.toLowerCase()
        return full.includes(buscarAsp.value.trim().toLowerCase())
      })
      if (found) params.asp_id = found.id
      else { guardias.value = []; total.value = 0; return }
    }
    const res = await guardiaApi.listar(params)
    guardias.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al cargar guardias'))
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

async function abrirDetalle(g) {
  dialogDetalle.value = true
  detalleGuardia.value = null
  try {
    const res = await guardiaApi.obtener(g.id)
    detalleGuardia.value = res.data
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al cargar detalle'))
    dialogDetalle.value = false
  }
}

function abrirCrear() {
  editando.value = null
  form.value = emptyForm()
  errores.value = {}
  dialogForm.value = true
}

function cerrarForm() {
  dialogForm.value = false
  errores.value = {}
}

function validar() {
  const e = {}
  if (!form.value.asp_id) e.asp_id = 'Seleccione un ASP'
  if (!form.value.turno_posta_id) e.turno_posta_id = 'Seleccione un turno'
  if (!form.value.fecha) e.fecha = 'Seleccione una fecha'
  errores.value = e
  return Object.keys(e).length === 0
}

async function guardar() {
  if (!validar()) return
  guardando.value = true
  try {
    const payload = {
      asp_id: form.value.asp_id,
      turno_posta_id: form.value.turno_posta_id,
      fecha: form.value.fecha,
    }
    if (!editando.value && form.value.observaciones?.trim()) {
      payload.observaciones = form.value.observaciones.trim()
    }
    if (editando.value) {
      await guardiaApi.actualizar(editando.value.id, payload)
      toast.success('Guardia actualizada')
    } else {
      await guardiaApi.crear(payload)
      toast.success('Guardia creada')
    }
    cerrarForm()
    await cargarGuardias()
  } catch (e) {
    const detail = e?.response?.data?.detail
    if (typeof detail === 'string') {
      errores.value = { _global: detail }
    } else {
      const fieldErrors = {}
      if (Array.isArray(detail)) {
        for (const item of detail) {
          const msg = (item?.msg || '').replace(/^Value error,\s*/i, '')
          if (msg) {
            if (!fieldErrors._global) fieldErrors._global = msg
            else fieldErrors._global += '. ' + msg
          }
        }
      }
      if (fieldErrors._global) errores.value = fieldErrors
      else toast.error(normalizeApiError(e, 'Error al guardar'))
    }
  } finally {
    guardando.value = false
  }
}

function abrirConfirmar(g) {
  guardiaConfirmar.value = g
  const t = turnoMap.value[g.turno_posta_id]
  const horaDefault = t?.hora_inicio?.slice(0, 5) || '08:00'
  formLlegada.value = { hora: horaDefault, fecha: g.fecha }
  erroresConfirmar.value = {}
  dialogConfirmar.value = true
}

async function confirmarLlegada() {
  if (!formLlegada.value.hora) return
  guardandoAccion.value = true
  try {
    const dt = `${formLlegada.value.fecha}T${formLlegada.value.hora}:00`
    await guardiaApi.confirmarLlegada(guardiaConfirmar.value.id, dt)
    toast.success('Llegada confirmada')
    dialogConfirmar.value = false
    await cargarGuardias()
  } catch (e) {
    const detail = e?.response?.data?.detail
    if (typeof detail === 'string') {
      erroresConfirmar.value = { _global: detail }
    } else {
      toast.error(normalizeApiError(e, 'Error al confirmar'))
    }
  } finally {
    guardandoAccion.value = false
  }
}

function abrirFinalizar(g) {
  guardiaFinalizar.value = g
  const t = turnoMap.value[g.turno_posta_id]
  const horaDefault = t?.hora_fin?.slice(0, 5) || '16:00'
  formFin.value = { hora_fin_real: horaDefault, observaciones: '' }
  erroresFinalizar.value = {}
  dialogFinalizar.value = true
}

async function finalizarGuardia() {
  if (!formFin.value.hora_fin_real) return
  guardandoAccion.value = true
  try {
    const g = guardiaFinalizar.value
    const t = turnoMap.value[g.turno_posta_id]
    let fecha = g.fecha
    if (t?.cruza_medianoche && g.hora_inicio_real) {
      const horaInicio = new Date(g.hora_inicio_real)
      const [h, m] = formFin.value.hora_fin_real.split(':').map(Number)
      const finApprox = new Date(horaInicio)
      finApprox.setHours(h, m, 0, 0)
      if (finApprox <= horaInicio) {
        const nextDay = new Date(fecha + 'T00:00:00')
        nextDay.setDate(nextDay.getDate() + 1)
        fecha = nextDay.toISOString().slice(0, 10)
      }
    }
    const dt = `${fecha}T${formFin.value.hora_fin_real}:00`
    const payload = { hora_fin_real: dt }
    if (formFin.value.observaciones?.trim()) payload.observaciones = formFin.value.observaciones.trim()
    await guardiaApi.finalizar(guardiaFinalizar.value.id, payload)
    toast.success('Guardia finalizada')
    dialogFinalizar.value = false
    await cargarGuardias()
  } catch (e) {
    const detail = e?.response?.data?.detail
    if (typeof detail === 'string') {
      erroresFinalizar.value = { _global: detail }
    } else {
      toast.error(normalizeApiError(e, 'Error al finalizar'))
    }
  } finally {
    guardandoAccion.value = false
  }
}

function abrirAusente(g) {
  guardiaAusente.value = g
  formAusente.value = { justificada: null, motivo_ausencia: '', observaciones: '' }
  erroresAusente.value = {}
  dialogAusente.value = true
}

async function marcarAusente() {
  if (formAusente.value.justificada === 'justificada' && !formAusente.value.motivo_ausencia?.trim()) return
  guardandoAccion.value = true
  try {
    const payload = {}
    if (formAusente.value.justificada === 'justificada') payload.motivo_ausencia = formAusente.value.motivo_ausencia.trim()
    if (formAusente.value.observaciones?.trim()) payload.observaciones = formAusente.value.observaciones.trim()
    await guardiaApi.marcarAusente(guardiaAusente.value.id, payload)
    toast.success('Guardia marcada como ausente')
    dialogAusente.value = false
    await cargarGuardias()
  } catch (e) {
    const detail = e?.response?.data?.detail
    if (typeof detail === 'string') {
      erroresAusente.value = { _global: detail }
    } else {
      toast.error(normalizeApiError(e, 'Error al marcar ausente'))
    }
  } finally {
    guardandoAccion.value = false
  }
}

function abrirCancelar(g) {
  guardiaCancelar.value = g
  formCancelar.value = { motivo: '', observaciones: '' }
  erroresCancelar.value = {}
  dialogCancelar.value = true
}

async function cancelarGuardia() {
  guardandoAccion.value = true
  try {
    const payload = {}
    if (formCancelar.value.motivo?.trim()) payload.motivo = formCancelar.value.motivo.trim()
    if (formCancelar.value.observaciones?.trim()) payload.observaciones = formCancelar.value.observaciones.trim()
    await guardiaApi.cancelar(guardiaCancelar.value.id, payload)
    toast.success('Guardia cancelada')
    dialogCancelar.value = false
    await cargarGuardias()
  } catch (e) {
    const detail = e?.response?.data?.detail
    if (typeof detail === 'string') {
      erroresCancelar.value = { _global: detail }
    } else {
      toast.error(normalizeApiError(e, 'Error al cancelar guardia'))
    }
  } finally {
    guardandoAccion.value = false
  }
}

function abrirNovedad(g) {
  guardiaNovedad.value = g
  formNovedad.value = emptyNovedadForm()
  erroresNovedad.value = {}
  dialogNovedad.value = true
}

async function registrarNovedad() {
  if (!formNovedad.value.tipo || !formNovedad.value.descripcion.trim()) return
  guardandoAccion.value = true
  try {
    await guardiaApi.registrarNovedad(guardiaNovedad.value.id, {
      tipo: formNovedad.value.tipo,
      descripcion: formNovedad.value.descripcion.trim(),
      severidad: formNovedad.value.severidad,
    })
    toast.success('Novedad registrada')
    dialogNovedad.value = false
    await cargarGuardias()
  } catch (e) {
    const detail = e?.response?.data?.detail
    if (typeof detail === 'string') {
      erroresNovedad.value = { _global: detail }
    } else {
      toast.error(normalizeApiError(e, 'Error al registrar novedad'))
    }
  } finally {
    guardandoAccion.value = false
  }
}

watch(filtroEstado, () => { pagina.value = 1; cargarGuardias() })
watch(mobile, () => { pagina.value = 1; cargarGuardias() })

onMounted(async () => {
  await Promise.all([cargarListas(), cargarGuardias()])
  if (route.query.detalle) {
    const g = guardias.value.find(item => item.id === Number(route.query.detalle))
    if (g) abrirDetalle(g)
    else {
      const res = await guardiaApi.obtener(Number(route.query.detalle)).catch(() => null)
      if (res) { dialogDetalle.value = true; detalleGuardia.value = res.data }
    }
  }
})
</script>

<style scoped>
.guardias-page {
  width: 100%;
}

.guardias-search {
  flex-grow: 1;
}

.guardias-fecha {
  min-width: 160px;
  max-width: 200px;
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

.novedades-list {
  display: flex;
  flex-direction: column;
}

.novedad-item {
  border: 1px solid rgb(var(--v-border-color));
  border-radius: 8px;
  background: rgb(var(--v-theme-surface));
}

.hora-select,
.minuto-select {
  min-width: 70px;
}

@media (max-width: 599px) {
  .guardias-search {
    max-width: 100%;
  }

  .guardias-fecha {
    min-width: 100%;
    max-width: 100%;
  }

  .ficha-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}
</style>
