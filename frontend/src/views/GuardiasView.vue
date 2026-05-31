<template>
  <div class="guardias-page">
    <div class="page-header guardias-header">
      <div class="page-title-block">
        <div class="page-title-icon">
          <i class="pi pi-shield"></i>
        </div>
        <div>
          <h2 class="page-title">Guardias</h2>
          <p class="page-subtitle">Gestion de guardias y novedades</p>
        </div>
      </div>

      <div class="header-actions">
        <Button type="button" @click="abrirModal()">
          <i class="pi pi-plus button-icon"></i>
          Nueva guardia
        </Button>
      </div>
    </div>

    <Card class="panel-card filters-card" style="margin-bottom: 16px">
      <template #content>
        <div class="filters-top">
          <div class="filters-summary">
            <span class="filters-summary-label">Filtros actuales</span>
            <span class="filters-summary-value">
              <Tag :value="`ASP: ${filtroAspSeleccionado ? `${filtroAspSeleccionado.nombre} ${filtroAspSeleccionado.apellidos}` : 'Todos'}`" severity="info" />
              <Tag :value="`Posta: ${filtroPostaSeleccionada ? filtroPostaSeleccionada.nombre : 'Todas'}`" severity="info" />
              <Tag :value="`Fecha: ${filtros.fecha ? formatFecha(filtros.fecha) : 'Todas'}`" severity="secondary" />
              <Tag v-if="filtros.estado" :value="labelEstado(filtros.estado)" :severity="severidadEstado(filtros.estado)" />
              <Tag v-else value="Estado: Todos" severity="secondary" />
            </span>
          </div>

          <div class="filter-state-box">
            <label for="filtroEstado">Estado</label>
            <div class="filter-state-controls">
              <Select
                id="filtroEstado"
                v-model="filtros.estado"
                :options="opcionesEstado"
                optionLabel="label"
                optionValue="value"
                placeholder="Todos"
                @update:modelValue="cargarGuardias"
              />
              <Button type="button" severity="secondary" outlined @click="abrirModalFiltros">
                <i class="pi pi-filter button-icon"></i>
                Filtros
              </Button>
              <Button type="button" severity="secondary" text @click="limpiarFiltros">
                <i class="pi pi-times button-icon"></i>
                Limpiar
              </Button>
            </div>
          </div>
        </div>
      </template>
    </Card>

    <Dialog v-model:visible="modalFiltrosVisible" header="Filtros de guardias" :style="{ width: '760px' }" modal
      :closable="true">
      <div class="wizard">
        <div class="steps">
          <div :class="['step', { active: filtroPaso === 1 }]">1. ASP</div>
          <div :class="['step', { active: filtroPaso === 2 }]">2. Posta</div>
          <div :class="['step', { active: filtroPaso === 3 }]">3. Fecha y estado</div>
        </div>

        <div v-if="filtroPaso === 1" class="step-content">
          <div class="field">
            <InputText v-model="filtroAspFiltro" placeholder="Nombre o CI..." />
          </div>


          <DataTable :value="filtroAspsFiltrados" v-model:selection="filtroAspSeleccionado" selectionMode="single"
            dataKey="id" size="small" paginator :rows="wizardRows" emptyMessage="No hay ASP encontrados"
            @rowSelect="seleccionarFiltroAsp">
            <Column field="ci" header="CI" />
            <Column header="Nombre">
              <template #body="{ data }">
                {{ data.nombre }} {{ data.apellidos }}
              </template>
            </Column>
          </DataTable>
        </div>

        <div v-else-if="filtroPaso === 2" class="step-content">
          <div class="field">
            <label>Buscar posta</label>
            <InputText v-model="filtroPostaFiltro" placeholder="Nombre de posta..." />
          </div>
          <DataTable :value="filtroPostasFiltradas" v-model:selection="filtroPostaSeleccionada" selectionMode="single"
            dataKey="id" size="small" paginator :rows="wizardRows" emptyMessage="No hay postas encontradas"
            @rowSelect="seleccionarFiltroPosta">
            <Column field="nombre" header="Posta" />
            <Column header="Tipo">
              <template #body="{ data }">
                {{ labelTipoPosta(data.tipo) }}
              </template>
            </Column>
            <Column header="Turnos">
              <template #body="{ data }">
                {{ turnosPorPosta(data.id).length }}
              </template>
            </Column>
          </DataTable>
        </div>

        <div v-else class="step-content">
          <div class="resume-grid">
            <div>
              <p class="resume-label">ASP seleccionado</p>
              <p class="resume-value">{{ filtroAspSeleccionado ? `${filtroAspSeleccionado.nombre}
                ${filtroAspSeleccionado.apellidos}` : 'Todos' }}</p>
            </div>
            <div>
              <p class="resume-label">Posta</p>
              <p class="resume-value">{{ filtroPostaSeleccionada ? filtroPostaSeleccionada.nombre : 'Todas' }}</p>
            </div>
          </div>

          <div class="form-grid">
            <div class="field">
              <label>Fecha</label>
              <DatePicker v-model="filtros.fecha" dateFormat="yy-mm-dd" showIcon />
            </div>
            <div class="field">
              <label>Estado</label>
              <Select v-model="filtros.estado" :options="opcionesEstado" optionLabel="label" optionValue="value"
                placeholder="Todos" />
            </div>
          </div>
        </div>

        <div class="wizard-actions">
          <Button v-if="filtroPaso > 1" label="Atras" severity="secondary" text @click="retrocederFiltroPaso" />
          <Button v-if="filtroPaso < 3" label="Siguiente" icon="pi pi-arrow-right" @click="avanzarFiltroPaso" />
          <Button v-if="filtroPaso === 3" label="Aplicar filtros" icon="pi pi-check" @click="aplicarFiltros" />
          <Button v-if="filtroPaso === 3" label="Limpiar" severity="secondary" text @click="limpiarFiltros" />
        </div>
      </div>
      <template #footer>
        <Button label="Cerrar" severity="secondary" text @click="cerrarModalFiltros" />
      </template>
    </Dialog>

    <Card class="panel-card table-card">
      <template #content>
        <div v-if="cargando" class="empty-state">
          <div class="spinner"></div>
          <p>Cargando...</p>
        </div>

        <div v-else-if="guardias.length === 0" class="empty-state">
          <i class="pi pi-shield empty-icon"></i>
          <div>
            <p class="empty-title">No hay guardias registradas</p>
            <p class="empty-subtitle">Comienza creando una guardia nueva</p>
          </div>
        </div>
        <div v-else class="table-shell">
          <table class="guardias-table">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>ASP</th>
                <th>Posta / Turno</th>
                <th>Estado</th>
                <th>Tardanza (min)</th>
                <th class="actions-col">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="guardia in guardias" :key="guardia.id">
                <td class="mono">{{ formatFecha(guardia.fecha) || '-' }}</td>
                <td><span class="name-main">{{ nombreAsp(guardia.asp_id) }}</span></td>
                <td class="cell-muted">{{ labelTurno(guardia.turno_posta_id) }}</td>
                <td>
                  <Tag :value="labelEstado(guardia.estado)" :severity="severidadEstado(guardia.estado)" />
                </td>
                <td>{{ guardia.tardanza_minutos ?? '-' }}</td>
                <td class="actions-col">
                  <div class="actions">
                    <Button class="action-button" icon="pi pi-eye" size="small" severity="info" text title="Ver informacion" aria-label="Ver informacion" @click="abrirModalInfo(guardia)" />
                    <Button v-if="puedeMostrarAccion(guardia.estado, 'editar')" class="action-button" icon="pi pi-pencil" size="small" severity="secondary" text title="Editar guardia" aria-label="Editar guardia" @click="abrirModal(guardia)" />
                    <Button v-if="puedeMostrarAccion(guardia.estado, 'ausencia')" class="action-button" icon="pi pi-user-minus" size="small" severity="danger" text title="Marcar ausencia" aria-label="Marcar ausencia" @click="abrirModalAusencia(guardia)" />
                    <Button v-if="puedeMostrarAccion(guardia.estado, 'llegada')" class="action-button" icon="pi pi-sign-in" size="small" severity="info" text title="Confirmar llegada" aria-label="Confirmar llegada" @click="abrirModalLlegada(guardia)" />
                    <Button v-if="puedeMostrarAccion(guardia.estado, 'finalizar')" class="action-button" icon="pi pi-flag" size="small" severity="success" text title="Finalizar guardia" aria-label="Finalizar guardia" @click="abrirModalFinalizar(guardia)" />
                    <Button v-if="puedeMostrarAccion(guardia.estado, 'novedad')" class="action-button" icon="pi pi-exclamation-triangle" size="small" severity="warn" text title="Registrar novedad" aria-label="Registrar novedad" @click="abrirModalNovedad(guardia)" />
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </Card>

    <Dialog v-model:visible="modalVisible" :header="editando ? 'Editar guardia' : 'Nueva guardia'"
      :style="{ width: '980px' }" modal :closable="true">
      <div class="p-fluid wizard-layout">
        <Message v-if="error" severity="error" :closable="false" style="margin-bottom: 12px">
          {{ error }}
        </Message>

        <div class="wizard-steps">
          <div class="wizard-step" :class="{ active: paso === 1, done: paso > 1 }">
            <span class="wizard-step-index">1</span>
            <div>
              <strong>ASP</strong>
              <small>Selecciona el ASP</small>
            </div>
          </div>
          <div class="wizard-step" :class="{ active: paso === 2, done: paso > 2 }">
            <span class="wizard-step-index">2</span>
            <div>
              <strong>Posta</strong>
              <small>Elige la posta</small>
            </div>
          </div>
          <div class="wizard-step" :class="{ active: paso === 3 }">
            <span class="wizard-step-index">3</span>
            <div>
              <strong>Turno y fecha</strong>
              <small>Completa datos finales</small>
            </div>
          </div>
        </div>

        <section v-if="paso === 1" class="form-section">
          <div class="section-head">
            <h3>Seleccionar ASP</h3>
            <p>Busca el ASP antes de continuar con el horario.</p>
          </div>

          <div class="field">
            <label for="aspFiltro">Buscar</label>
            <div class="search-inline">
              <div class="search-field search-field-flex">
                <i class="pi pi-search search-icon"></i>
                <InputText id="aspFiltro" v-model="aspFiltro" class="search-input" placeholder="Nombre o CI..." />
              </div>
            </div>
          </div>

          <div class="results-shell wizard-results-shell">
            <table class="results-table">
              <thead>
                <tr>
                  <th>CI</th>
                  <th>Nombre</th>
                  <th class="actions-col">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="asp in aspsFiltrados" :key="asp.id" :class="{ selected: aspSeleccionado?.id === asp.id }">
                  <td class="mono">{{ asp.ci }}</td>
                  <td><span class="name-main">{{ asp.nombre }} {{ asp.apellidos }}</span></td>
                  <td class="actions-col">
                    <Button type="button" size="small" severity="secondary" text :label="aspSeleccionado?.id === asp.id ? 'Elegido' : 'Elegir'" @click="seleccionarAsp({ data: asp })" />
                  </td>
                </tr>
              </tbody>
            </table>

            <div v-if="aspsFiltrados.length === 0" class="empty-state compact-empty">
              <i class="pi pi-search empty-icon"></i>
              <div>
                <p class="empty-title">No hay ASP encontrados</p>
                <p class="empty-subtitle">Prueba con otro criterio de búsqueda</p>
              </div>
            </div>
          </div>
        </section>

        <section v-else-if="paso === 2" class="form-section">
          <div class="section-head">
            <h3>Seleccionar posta</h3>
            <p>Busca la posta antes de continuar con el horario.</p>
          </div>

          <div class="field">
            <label for="postaFiltro">Buscar</label>
            <div class="search-inline">
              <div class="search-field search-field-flex">
                <i class="pi pi-search search-icon"></i>
                <InputText id="postaFiltro" v-model="postaFiltro" class="search-input" placeholder="Nombre de posta..." />
              </div>
            </div>
          </div>

          <div class="results-shell wizard-results-shell">
            <table class="results-table">
              <thead>
                <tr>
                  <th>Posta</th>
                  <th>Tipo</th>
                  <th>Estado</th>
                  <th>Turnos</th>
                  <th class="actions-col">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="posta in postasFiltradas" :key="posta.id" :class="{ selected: postaSeleccionada?.id === posta.id }">
                  <td><span class="name-main">{{ posta.nombre }}</span></td>
                  <td>{{ labelTipoPosta(posta.tipo) }}</td>
                  <td><Tag :value="posta.activa ? 'Activa' : 'Inactiva'" :severity="posta.activa ? 'success' : 'secondary'" /></td>
                  <td>{{ turnosActivosPorPosta(posta.id).length }}</td>
                  <td class="actions-col">
                    <Button type="button" size="small" severity="secondary" text :label="postaSeleccionada?.id === posta.id ? 'Elegida' : 'Elegir'" @click="seleccionarPosta({ data: posta })" />
                  </td>
                </tr>
              </tbody>
            </table>

            <div v-if="postasFiltradas.length === 0" class="empty-state compact-empty">
              <i class="pi pi-search empty-icon"></i>
              <div>
                <p class="empty-title">No hay postas encontradas</p>
                <p class="empty-subtitle">Prueba con otro criterio de búsqueda</p>
              </div>
            </div>
          </div>
        </section>

        <section v-else class="form-section">
          <div class="section-head">
            <h3>Turno y fecha</h3>
            <p>Define el turno, la fecha y las observaciones.</p>
          </div>

          <div class="selected-posta-banner resume-grid">
            <div>
              <p class="resume-label">ASP seleccionado</p>
              <p class="resume-value">{{ aspSeleccionado ? `${aspSeleccionado.nombre} ${aspSeleccionado.apellidos}` : '-' }}</p>
            </div>
            <div>
              <p class="resume-label">Posta</p>
              <p class="resume-value">{{ postaSeleccionada ? postaSeleccionada.nombre : '-' }}</p>
            </div>
          </div>

          <div class="field">
            <label for="turnoFiltro">Buscar</label>
            <div class="search-inline">
              <div class="search-field search-field-flex">
                <i class="pi pi-search search-icon"></i>
                <InputText id="turnoFiltro" v-model="turnoFiltro" class="search-input" placeholder="Nombre del turno..." />
              </div>
            </div>
          </div>

          <div class="results-shell wizard-results-shell">
            <table class="results-table">
              <thead>
                <tr>
                  <th>Turno</th>
                  <th>Horario</th>
                  <th>ASP</th>
                  <th class="actions-col">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="turno in turnosFiltrados" :key="turno.id" :class="{ selected: turnoSeleccionado?.id === turno.id }">
                  <td><span class="name-main">{{ turno.nombre }}</span></td>
                  <td>{{ formatHora(turno.hora_inicio) }} - {{ formatHora(turno.hora_fin) }}</td>
                  <td>{{ turno.asp_requeridos }}</td>
                  <td class="actions-col">
                    <Button type="button" size="small" severity="secondary" text :label="turnoSeleccionado?.id === turno.id ? 'Elegido' : 'Elegir'" @click="seleccionarTurno({ data: turno })" />
                  </td>
                </tr>
              </tbody>
            </table>

            <div v-if="turnosFiltrados.length === 0" class="empty-state compact-empty">
              <i class="pi pi-search empty-icon"></i>
              <div>
                <p class="empty-title">No hay turnos disponibles</p>
                <p class="empty-subtitle">Prueba con otro criterio de búsqueda</p>
              </div>
            </div>
          </div>

          <div class="form-grid">
            <div class="field">
              <label>Fecha *</label>
              <DatePicker v-model="form.fecha" dateFormat="yy-mm-dd" showIcon />
            </div>
            <div class="field span-2">
              <label>Observaciones</label>
              <Textarea v-model="form.observaciones" rows="2" autoResize />
            </div>
          </div>
        </section>
      </div>
      <template #footer>
        <div class="dialog-footer wizard-footer">
          <Button type="button" label="Cancelar" severity="secondary" text @click="cerrarModal" />
          <div class="dialog-actions">
            <Button v-if="paso > 1" type="button" label="Atras" severity="secondary" outlined @click="retrocederPaso" />
            <Button v-if="paso < 3" type="button" label="Siguiente" icon="pi pi-arrow-right" @click="avanzarPaso" />
            <Button v-if="paso === 3" type="button" label="Guardar" icon="pi pi-check" :loading="guardando" @click="guardar" />
          </div>
        </div>
      </template>
    </Dialog>

    <Dialog v-model:visible="modalLlegadaVisible" header="Confirmar llegada" :style="{ width: '420px' }" modal
      :closable="true">
      <div class="p-fluid">
        <Message v-if="errorLlegada" severity="error" :closable="false" style="margin-bottom: 12px">
          {{ errorLlegada }}
        </Message>
        <div class="field">
          <label>Hora de llegada *</label>
          <InputText v-model="formLlegada.hora_llegada" type="datetime-local" />
        </div>
      </div>
      <template #footer>
        <Button label="Cancelar" severity="secondary" text @click="cerrarModalLlegada" />
        <Button label="Confirmar" icon="pi pi-check" :loading="guardandoLlegada" @click="confirmarLlegada" />
      </template>
    </Dialog>

    <Dialog v-model:visible="modalFinalizarVisible" header="Finalizar guardia" :style="{ width: '460px' }" modal
      :closable="true">
      <div class="p-fluid">
        <Message v-if="errorFinalizar" severity="error" :closable="false" style="margin-bottom: 12px">
          {{ errorFinalizar }}
        </Message>
        <div class="field">
          <label>Hora de fin *</label>
          <InputText v-model="formFinalizar.hora_fin_real" type="datetime-local" />
        </div>
        <div class="field" style="margin-top: 12px">
          <label>Observaciones</label>
          <Textarea v-model="formFinalizar.observaciones" rows="2" autoResize />
        </div>
      </div>
      <template #footer>
        <Button label="Cancelar" severity="secondary" text @click="cerrarModalFinalizar" />
        <Button label="Finalizar" icon="pi pi-check" :loading="guardandoFinalizar" @click="finalizar" />
      </template>
    </Dialog>

    <Dialog v-model:visible="modalNovedadVisible" :header="'Novedades — ' + (guardiaSeleccionada?.id || '')"
      :style="{ width: '700px' }" modal :closable="true">
      <div class="p-fluid">
        <Message v-if="errorNovedad" severity="error" :closable="false" style="margin-bottom: 12px">
          {{ errorNovedad }}
        </Message>
        <div class="novedad-form">
          <div class="field">
            <label>Tipo *</label>
            <Select v-model="formNovedad.tipo" :options="opcionesTipoNovedad" optionLabel="label" optionValue="value" />
          </div>
          <div class="field">
            <label>Severidad *</label>
            <Select v-model="formNovedad.severidad" :options="opcionesSeveridad" optionLabel="label"
              optionValue="value" />
          </div>
          <div class="field" style="grid-column: span 2">
            <label>Descripcion *</label>
            <Textarea v-model="formNovedad.descripcion" rows="2" autoResize />
          </div>
          <div class="novedad-actions">
            <Button label="Registrar" icon="pi pi-check" :loading="guardandoNovedad" @click="registrarNovedad" />
          </div>
        </div>

        <DataTable :value="novedades" size="small" stripedRows emptyMessage="No hay novedades">
          <Column field="fecha_hora" header="Fecha" />
          <Column header="Tipo">
            <template #body="{ data }">
              {{ labelTipoNovedad(data.tipo) }}
            </template>
          </Column>
          <Column header="Severidad">
            <template #body="{ data }">
              <Tag :value="labelSeveridad(data.severidad)" :severity="severidadNovedad(data.severidad)" />
            </template>
          </Column>
          <Column field="descripcion" header="Descripcion" />
        </DataTable>
      </div>
      <template #footer>
        <Button label="Cerrar" severity="secondary" text @click="cerrarModalNovedad" />
      </template>
    </Dialog>

    <Dialog v-model:visible="modalAusenciaVisible" header="Marcar ausencia" :style="{ width: '520px' }" modal
      :closable="true">
      <div class="p-fluid">
        <Message v-if="errorAusencia" severity="error" :closable="false" style="margin-bottom: 12px">
          {{ errorAusencia }}
        </Message>
        <div class="form-grid">
          <div class="field" :class="{ 'span-2': formAusencia.justificada !== true }">
            <label>Justificada</label>
            <Select v-model="formAusencia.justificada" :options="opcionesJustificada" optionLabel="label"
              optionValue="value" placeholder="Selecciona" />
          </div>
          <div class="field" v-if="formAusencia.justificada">
            <label>Motivo de ausencia</label>
            <InputText v-model="formAusencia.motivo_ausencia" />
          </div>
          <div class="field" style="grid-column: span 2">
            <label>Observaciones</label>
            <Textarea v-model="formAusencia.observaciones" rows="2" autoResize />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancelar" severity="secondary" text @click="cerrarModalAusencia" />
        <Button label="Guardar" icon="pi pi-check" :loading="guardandoAusencia" @click="guardarAusencia" />
      </template>
    </Dialog>

    <Dialog v-model:visible="modalInfoVisible" header="Ficha tecnica de guardia" :style="{ width: '720px' }" modal
      :closable="true">
      <div class="p-fluid">
        <Message v-if="errorInfo" severity="error" :closable="false" style="margin-bottom: 12px">
          {{ errorInfo }}
        </Message>
        <div v-if="cargandoInfo" class="empty-state">Cargando...</div>
        <div v-else-if="guardiaDetalle" class="info-grid">
          <div class="info-col">
            <div class="info-item">
              <span class="info-label">Fecha</span>
              <span class="info-value">{{ formatFecha(guardiaDetalle.fecha) || '—' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">ASP</span>
              <span class="info-value">{{ nombreAsp(guardiaDetalle.asp_id) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Hora de llegada</span>
              <span class="info-value">{{ formatFechaHora(guardiaDetalle.hora_inicio_real) || '—' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Tardanza (min)</span>
              <span class="info-value">{{ guardiaDetalle.tardanza_minutos ?? '—' }}</span>
            </div>
          </div>
          <div class="info-col">
            <div class="info-item">
              <span class="info-label">Estado</span>
              <span class="info-value">{{ labelEstado(guardiaDetalle.estado) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Posta / Turno</span>
              <span class="info-value">{{ labelTurno(guardiaDetalle.turno_posta_id) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Hora de fin</span>
              <span class="info-value">{{ formatFechaHora(guardiaDetalle.hora_fin_real) || '—' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Motivo de ausencia</span>
              <span class="info-value">{{ guardiaDetalle.motivo_ausencia || '—' }}</span>
            </div>
          </div>
          <div class="info-item span-2">
            <span class="info-label">Observaciones</span>
            <span class="info-value">{{ guardiaDetalle.observaciones || '—' }}</span>
          </div>
        </div>

        <div v-if="guardiaDetalle?.novedades?.length" class="info-section">
          <h4>Novedades</h4>
          <DataTable :value="guardiaDetalle.novedades" size="small" stripedRows>
            <Column field="fecha_hora" header="Fecha" />
            <Column header="Tipo">
              <template #body="{ data }">
                {{ labelTipoNovedad(data.tipo) }}
              </template>
            </Column>
            <Column header="Severidad">
              <template #body="{ data }">
                {{ labelSeveridad(data.severidad) }}
              </template>
            </Column>
            <Column field="descripcion" header="Descripcion" />
          </DataTable>
        </div>
      </div>
      <template #footer>
        <Button label="Cerrar" severity="secondary" text @click="cerrarModalInfo" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import DatePicker from 'primevue/datepicker'
import Message from 'primevue/message'
import { useToast } from 'primevue/usetoast'
import { guardiaApi } from '../api/guardia'
import { aspApi } from '../api/asp'
import { postaApi } from '../api/posta'
import { normalizeApiError } from '../utils/error'

const guardias = ref([])
const cargando = ref(true)
const modalVisible = ref(false)
const modalFiltrosVisible = ref(false)
const modalLlegadaVisible = ref(false)
const modalFinalizarVisible = ref(false)
const modalNovedadVisible = ref(false)
const modalAusenciaVisible = ref(false)
const modalInfoVisible = ref(false)
const editando = ref(null)
const guardiaSeleccionada = ref(null)
const guardiaDetalle = ref(null)
const error = ref('')
const errorLlegada = ref('')
const errorFinalizar = ref('')
const errorNovedad = ref('')
const errorAusencia = ref('')
const errorInfo = ref('')
const guardando = ref(false)
const guardandoLlegada = ref(false)
const guardandoFinalizar = ref(false)
const guardandoNovedad = ref(false)
const guardandoAusencia = ref(false)
const cargandoInfo = ref(false)
const toast = useToast()

const wizardRows = 6

const asps = ref([])
const postas = ref([])
const turnos = ref([])
const turnosById = ref({})

const filtros = ref({ fecha: null, estado: '', asp_id: null, posta_id: null })
const filtroPaso = ref(1)
const filtroAspFiltro = ref('')
const filtroPostaFiltro = ref('')
const filtroAspSeleccionado = ref(null)
const filtroPostaSeleccionada = ref(null)

const opcionesEstado = [
  { label: 'Todos', value: '' },
  { label: 'Planificada', value: 'planificada' },
  { label: 'Activa', value: 'activa' },
  { label: 'Finalizada', value: 'finalizada' },
  { label: 'Ausente', value: 'ausente' },
  { label: 'Cancelada', value: 'cancelada' },
]

const opcionesTipoNovedad = [
  { label: 'Incidente', value: 'incidente' },
  { label: 'Comunicado', value: 'comunicado' },
  { label: 'Entrega recepcion', value: 'entrega_recepcion' },
  { label: 'Solicitud', value: 'solicitud' },
  { label: 'Otro', value: 'otro' },
]
const opcionesSeveridad = [
  { label: 'Baja', value: 'baja' },
  { label: 'Media', value: 'media' },
  { label: 'Alta', value: 'alta' },
  { label: 'Critica', value: 'critica' },
]

const opcionesJustificada = [
  { label: 'Si', value: true },
  { label: 'No', value: false },
]

const form = ref({ asp_id: null, turno_posta_id: null, fecha: null, observaciones: '' })
const formAusencia = ref({ justificada: null, motivo_ausencia: '', observaciones: '' })
const formLlegada = ref({ hora_llegada: '' })
const formFinalizar = ref({ hora_fin_real: '', observaciones: '' })
const formNovedad = ref({ tipo: 'incidente', severidad: 'baja', descripcion: '' })
const novedades = ref([])
const postaSeleccionada = ref(null)
const aspSeleccionado = ref(null)
const turnoSeleccionado = ref(null)
const paso = ref(1)
const aspFiltro = ref('')
const postaFiltro = ref('')
const turnoFiltro = ref('')

const aspsActivos = computed(() => asps.value.filter(a => a.estado === 'activo'))

const opcionesPosta = computed(() => [
  { label: 'Todas', value: null },
  ...postas.value.map(p => ({ label: p.nombre, value: p.id })),
])

const opcionesTurno = computed(() => {
  if (!postaSeleccionada.value) return []
  return turnos.value
    .filter(t => t.posta_id === postaSeleccionada.value.id && t.activo)
    .map(t => ({ label: labelTurno(t.id), value: t.id }))
})

const filtroAspsFiltrados = computed(() => {
  const query = filtroAspFiltro.value.trim().toLowerCase()
  if (!query) return asps.value
  return asps.value.filter(a => {
    const fullName = `${a.nombre} ${a.apellidos}`.toLowerCase()
    return fullName.includes(query) || String(a.ci || '').includes(query)
  })
})

const filtroPostasFiltradas = computed(() => {
  const query = filtroPostaFiltro.value.trim().toLowerCase()
  if (!query) return postas.value
  return postas.value.filter(p => p.nombre.toLowerCase().includes(query))
})

const aspsFiltrados = computed(() => {
  const query = aspFiltro.value.trim().toLowerCase()
  const fuente = aspsActivos.value
  if (!query) return fuente
  return fuente.filter(a => {
    const fullName = `${a.nombre} ${a.apellidos}`.toLowerCase()
    return fullName.includes(query) || String(a.ci || '').includes(query)
  })
})

const postasFiltradas = computed(() => {
  const query = postaFiltro.value.trim().toLowerCase()
  const base = postas.value.filter(p => turnosActivosPorPosta(p.id).length > 0)
  if (!query) return base
  return base.filter(p => p.nombre.toLowerCase().includes(query))
})

const turnosFiltrados = computed(() => {
  if (!postaSeleccionada.value) return []
  const query = turnoFiltro.value.trim().toLowerCase()
  const base = turnos.value.filter(t => t.posta_id === postaSeleccionada.value.id && t.activo)
  if (!query) return base
  return base.filter(t => t.nombre.toLowerCase().includes(query))
})

function labelEstado(estado) {
  return opcionesEstado.find(o => o.value === estado)?.label || 'Desconocido'
}

function severidadEstado(estado) {
  const map = {
    planificada: 'secondary',
    activa: 'success',
    finalizada: 'success',
    ausente: 'danger',
    cancelada: 'danger',
  }
  return map[estado] || 'secondary'
}

function puedeMostrarAccion(estado, accion) {
  const reglas = {
    editar: ['planificada', 'activa', 'ausente', 'cancelada'],
    ausencia: ['planificada'],
    llegada: ['planificada'],
    finalizar: ['activa'],
    novedad: ['activa'],
  }

  return reglas[accion]?.includes(estado) || false
}

function labelTipoNovedad(tipo) {
  return opcionesTipoNovedad.find(o => o.value === tipo)?.label || 'Otro'
}

function labelSeveridad(severidad) {
  return opcionesSeveridad.find(o => o.value === severidad)?.label || 'Baja'
}

function severidadNovedad(severidad) {
  const map = {
    baja: 'secondary',
    media: 'info',
    alta: 'warn',
    critica: 'danger',
  }
  return map[severidad] || 'secondary'
}

function formatFecha(value) {
  if (!value) return ''
  if (typeof value === 'string') return value.split('T')[0]
  const d = new Date(value)
  return d.toISOString().split('T')[0]
}

function formatHora(value) {
  if (!value) return ''
  const parts = String(value).split(':')
  if (parts.length < 2) return value
  return `${parts[0].padStart(2, '0')}:${parts[1].padStart(2, '0')}`
}

function formatFechaHora(value) {
  if (!value) return ''
  if (typeof value === 'string') return value.replace('T', ' ').slice(0, 16)
  const d = new Date(value)
  return d.toISOString().replace('T', ' ').slice(0, 16)
}

function nombreAsp(id) {
  const asp = asps.value.find(a => a.id === id)
  return asp ? `${asp.nombre} ${asp.apellidos}` : '-'
}

function labelTurno(turnoId) {
  const turno = turnosById.value[turnoId]
  if (!turno) return '-'
  const horario = `${formatHora(turno.hora_inicio)}-${formatHora(turno.hora_fin)}`
  return `${turno.posta_nombre} - ${turno.nombre} (${horario})`
}

function labelTipoPosta(tipo) {
  const map = {
    interior: 'Interior',
    perimetral: 'Perimetral',
    movil: 'Movil',
    punto_critico: 'Punto critico',
  }
  return map[tipo] || 'Otro'
}

function turnosPorPosta(postaId) {
  return turnos.value.filter(t => t.posta_id === postaId)
}

function turnosActivosPorPosta(postaId) {
  return turnos.value.filter(t => t.posta_id === postaId && t.activo)
}

async function cargarCatalogos() {
  const [aspRes, postasRes] = await Promise.all([
    aspApi.listar({ page: 1, size: 100 }),
    postaApi.listar({}),
  ])
  asps.value = aspRes.data.items || []
  postas.value = postasRes.data || []
  await cargarTurnos()
}

async function cargarTurnos() {
  const items = []
  const index = {}
  await Promise.all(
    postas.value.map(async posta => {
      const res = await postaApi.obtener(posta.id)
      const turnosPosta = res.data.turnos || []
      turnosPosta.forEach(turno => {
        const item = { ...turno, posta_id: posta.id, posta_nombre: posta.nombre }
        items.push(item)
        index[turno.id] = item
      })
    })
  )
  turnos.value = items
  turnosById.value = index
}

async function cargarGuardias() {
  cargando.value = true
  try {
    const params = {}
    if (filtros.value.fecha) params.fecha = formatFecha(filtros.value.fecha)
    if (filtros.value.estado) params.estado = filtros.value.estado
    if (filtros.value.asp_id) params.asp_id = filtros.value.asp_id
    if (filtros.value.posta_id) params.posta_id = filtros.value.posta_id
    const res = await guardiaApi.listar(params)
    guardias.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    cargando.value = false
  }
}

function abrirModal(guardia = null) {
  editando.value = guardia
  error.value = ''
  postaSeleccionada.value = null
  aspSeleccionado.value = null
  turnoSeleccionado.value = null
  paso.value = 1
  aspFiltro.value = ''
  postaFiltro.value = ''
  turnoFiltro.value = ''
  if (guardia) {
    const turno = turnosById.value[guardia.turno_posta_id]
    const posta = postas.value.find(p => p.id === turno?.posta_id)
    const asp = asps.value.find(a => a.id === guardia.asp_id)
    aspSeleccionado.value = asp || null
    postaSeleccionada.value = posta || null
    turnoSeleccionado.value = turno || null
    form.value = {
      asp_id: guardia.asp_id,
      turno_posta_id: guardia.turno_posta_id,
      fecha: guardia.fecha ? new Date(guardia.fecha) : null,
      observaciones: guardia.observaciones || '',
    }
  } else {
    form.value = { asp_id: null, turno_posta_id: null, fecha: null, observaciones: '' }
  }
  modalVisible.value = true
}

function cerrarModal() {
  modalVisible.value = false
  editando.value = null
}

function abrirModalFiltros() {
  modalFiltrosVisible.value = true
}

function cerrarModalFiltros() {
  modalFiltrosVisible.value = false
}

function seleccionarFiltroAsp(event) {
  filtroAspSeleccionado.value = event.data
  filtros.value.asp_id = event.data?.id || null
}

function seleccionarFiltroPosta(event) {
  filtroPostaSeleccionada.value = event.data
  filtros.value.posta_id = event.data?.id || null
}

function avanzarFiltroPaso() {
  filtroPaso.value += 1
}

function retrocederFiltroPaso() {
  filtroPaso.value = Math.max(1, filtroPaso.value - 1)
}

function limpiarFiltros() {
  filtros.value = { fecha: null, estado: '', asp_id: null, posta_id: null }
  filtroAspSeleccionado.value = null
  filtroPostaSeleccionada.value = null
  filtroAspFiltro.value = ''
  filtroPostaFiltro.value = ''
  filtroPaso.value = 1
  cargarGuardias()
}

function aplicarFiltros() {
  cargarGuardias()
  cerrarModalFiltros()
}

function seleccionarAsp(event) {
  aspSeleccionado.value = event.data
  form.value.asp_id = event.data.id
}

function seleccionarPosta(event) {
  postaSeleccionada.value = event.data
  turnoSeleccionado.value = null
  form.value.turno_posta_id = null
}

function seleccionarTurno(event) {
  turnoSeleccionado.value = event.data
  form.value.turno_posta_id = event.data.id
}

function avanzarPaso() {
  if (paso.value === 1 && !aspSeleccionado.value) {
    error.value = 'Selecciona un ASP para continuar'
    return
  }
  if (paso.value === 2 && !postaSeleccionada.value) {
    error.value = 'Selecciona una posta para continuar'
    return
  }
  error.value = ''
  paso.value += 1
}

function retrocederPaso() {
  paso.value = Math.max(1, paso.value - 1)
}

async function guardar() {
  error.value = ''
  guardando.value = true
  try {
    if (editando.value) {
      if (!form.value.asp_id || !form.value.turno_posta_id || !form.value.fecha) {
        error.value = 'Completa ASP, turno y fecha'
        return
      }
      const payload = {
        ...form.value,
        fecha: formatFecha(form.value.fecha),
      }
      await guardiaApi.actualizar(editando.value.id, payload)
      toast.add({ severity: 'success', summary: 'Guardia actualizada', detail: 'La guardia se actualizo correctamente', life: 3000 })
    } else {
      if (!form.value.asp_id || !form.value.turno_posta_id || !form.value.fecha) {
        error.value = 'Completa ASP, turno y fecha'
        return
      }
      const payload = {
        ...form.value,
        fecha: formatFecha(form.value.fecha),
      }
      await guardiaApi.crear(payload)
      toast.add({ severity: 'success', summary: 'Guardia creada', detail: 'La guardia se creo correctamente', life: 3000 })
    }
    cerrarModal()
    await cargarGuardias()
  } catch (e) {
    error.value = normalizeApiError(e, 'Error al guardar')
  } finally {
    guardando.value = false
  }
}

function abrirModalAusencia(guardia) {
  guardiaSeleccionada.value = guardia
  formAusencia.value = { justificada: null, motivo_ausencia: '', observaciones: '' }
  errorAusencia.value = ''
  modalAusenciaVisible.value = true
}

function cerrarModalAusencia() {
  modalAusenciaVisible.value = false
  guardiaSeleccionada.value = null
}

async function abrirModalInfo(guardia) {
  guardiaDetalle.value = null
  errorInfo.value = ''
  cargandoInfo.value = true
  modalInfoVisible.value = true
  try {
    const res = await guardiaApi.obtener(guardia.id)
    guardiaDetalle.value = res.data
  } catch (e) {
    errorInfo.value = normalizeApiError(e, 'Error al cargar informacion')
  } finally {
    cargandoInfo.value = false
  }
}

function cerrarModalInfo() {
  modalInfoVisible.value = false
  guardiaDetalle.value = null
}

async function guardarAusencia() {
  errorAusencia.value = ''
  guardandoAusencia.value = true
  try {
    if (formAusencia.value.justificada === null) {
      errorAusencia.value = 'Selecciona si es justificada'
      return
    }
    const payload = {}
    if (formAusencia.value.justificada === true) {
      if (!formAusencia.value.motivo_ausencia) {
        errorAusencia.value = 'Indica el motivo de ausencia'
        return
      }
      payload.motivo_ausencia = formAusencia.value.motivo_ausencia
    }
    if (formAusencia.value.justificada === false) {
      payload.motivo_ausencia = ''
    }
    if (formAusencia.value.observaciones) payload.observaciones = formAusencia.value.observaciones

    await guardiaApi.actualizar(guardiaSeleccionada.value.id, payload)
    toast.add({ severity: 'success', summary: 'Ausencia registrada', detail: 'La ausencia se guardo correctamente', life: 3000 })
    cerrarModalAusencia()
    await cargarGuardias()
  } catch (e) {
    errorAusencia.value = normalizeApiError(e, 'Error al guardar ausencia')
  } finally {
    guardandoAusencia.value = false
  }
}

function abrirModalLlegada(guardia) {
  guardiaSeleccionada.value = guardia
  formLlegada.value = { hora_llegada: '' }
  errorLlegada.value = ''
  modalLlegadaVisible.value = true
}

function cerrarModalLlegada() {
  modalLlegadaVisible.value = false
  guardiaSeleccionada.value = null
}

async function confirmarLlegada() {
  errorLlegada.value = ''
  if (!formLlegada.value.hora_llegada) {
    errorLlegada.value = 'Indica la hora de llegada'
    return
  }
  guardandoLlegada.value = true
  try {
    await guardiaApi.confirmarLlegada(guardiaSeleccionada.value.id, formLlegada.value.hora_llegada)
    toast.add({ severity: 'success', summary: 'Llegada confirmada', detail: 'La llegada fue registrada', life: 3000 })
    cerrarModalLlegada()
    await cargarGuardias()
  } catch (e) {
    errorLlegada.value = normalizeApiError(e, 'Error al confirmar llegada')
  } finally {
    guardandoLlegada.value = false
  }
}

function abrirModalFinalizar(guardia) {
  guardiaSeleccionada.value = guardia
  formFinalizar.value = { hora_fin_real: '', observaciones: '' }
  errorFinalizar.value = ''
  modalFinalizarVisible.value = true
}

function cerrarModalFinalizar() {
  modalFinalizarVisible.value = false
  guardiaSeleccionada.value = null
}

async function finalizar() {
  errorFinalizar.value = ''
  if (!formFinalizar.value.hora_fin_real) {
    errorFinalizar.value = 'Indica la hora de fin'
    return
  }
  guardandoFinalizar.value = true
  try {
    await guardiaApi.finalizar(guardiaSeleccionada.value.id, formFinalizar.value)
    toast.add({ severity: 'success', summary: 'Guardia finalizada', detail: 'La guardia fue finalizada', life: 3000 })
    cerrarModalFinalizar()
    await cargarGuardias()
  } catch (e) {
    errorFinalizar.value = normalizeApiError(e, 'Error al finalizar')
  } finally {
    guardandoFinalizar.value = false
  }
}

async function abrirModalNovedad(guardia) {
  guardiaSeleccionada.value = guardia
  formNovedad.value = { tipo: 'incidente', severidad: 'baja', descripcion: '' }
  errorNovedad.value = ''
  await cargarNovedades()
  modalNovedadVisible.value = true
}

function cerrarModalNovedad() {
  modalNovedadVisible.value = false
  guardiaSeleccionada.value = null
}

async function cargarNovedades() {
  const res = await guardiaApi.listarNovedades(guardiaSeleccionada.value.id)
  novedades.value = res.data || []
}

async function registrarNovedad() {
  errorNovedad.value = ''
  if (!formNovedad.value.descripcion) {
    errorNovedad.value = 'Completa la descripcion'
    return
  }
  guardandoNovedad.value = true
  try {
    await guardiaApi.registrarNovedad(guardiaSeleccionada.value.id, formNovedad.value)
    toast.add({ severity: 'success', summary: 'Novedad registrada', detail: 'La novedad fue guardada', life: 3000 })
    await cargarNovedades()
    await cargarGuardias()
    formNovedad.value = { tipo: 'incidente', severidad: 'baja', descripcion: '' }
  } catch (e) {
    errorNovedad.value = normalizeApiError(e, 'Error al registrar novedad')
  } finally {
    guardandoNovedad.value = false
  }
}

onMounted(async () => {
  await cargarCatalogos()
  await cargarGuardias()
})
</script>

<style scoped>
.guardias-page { display: flex; flex-direction: column; gap: 1rem; }
.guardias-header { align-items: center; gap: 1rem; flex-wrap: wrap; }
.page-title-block { display: flex; align-items: center; gap: 0.875rem; }
.page-title-icon { width: 2.625rem; height: 2.625rem; border-radius: 0.75rem; display: flex; align-items: center; justify-content: center; background: var(--brand-50); color: var(--brand-600); font-size: 1.25rem; }
.page-title { margin: 0; font-size: 1.6rem; font-weight: 700; line-height: 1.2; color: var(--text); }
.page-subtitle { margin: 0.2rem 0 0; font-size: 0.875rem; color: var(--text-muted); }
.header-actions { display: flex; gap: 0.75rem; align-items: center; margin-left: auto; flex-wrap: wrap; }
.button-icon { margin-right: 0.5rem; }

.panel-card { border: 1px solid color-mix(in srgb, var(--border) 75%, transparent); box-shadow: 0 16px 50px rgba(15, 23, 42, 0.05); }

.filters-top { display: flex; align-items: flex-end; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
.filters-summary { display: flex; flex-direction: column; gap: 0.4rem; }
.filters-summary-label { font-size: 0.8rem; font-weight: 600; color: var(--text-muted); }
.filters-summary-value { display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center; }
.filter-state-box { display: flex; flex-direction: column; gap: 0.35rem; min-width: 240px; }
.filter-state-box label { font-size: 0.8rem; font-weight: 600; color: var(--text-muted); }
.filter-state-controls { display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap; }
.filter-state-controls :deep(.p-select) { min-width: 190px; }

.table-shell { overflow-x: auto; }
.guardias-table { width: 100%; border-collapse: collapse; }
.guardias-table thead th { padding: 0.9rem 1rem; text-align: left; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; color: var(--text-muted); border-bottom: 1px solid color-mix(in srgb, var(--border) 70%, transparent); }
.guardias-table tbody td { padding: 0.95rem 1rem; border-bottom: 1px solid color-mix(in srgb, var(--border) 65%, transparent); vertical-align: middle; }
.guardias-table tbody tr:hover { background: color-mix(in srgb, var(--surface) 86%, transparent); }
.actions-col { width: 14rem; text-align: center; }
.actions { display: flex; justify-content: center; gap: 0.4rem; flex-wrap: wrap; }
.action-button { flex: 0 0 auto; }
.name-main { display: block; font-weight: 600; color: var(--text); }
.cell-muted { color: var(--text-muted); }
.mono { font-variant-numeric: tabular-nums; }

.empty-state { min-height: 16rem; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 0.75rem; color: var(--text-muted); text-align: center; }
.empty-icon { font-size: 2rem; }
.empty-title { margin: 0; font-weight: 600; color: var(--text); }
.empty-subtitle { margin: 0.25rem 0 0; font-size: 0.875rem; }
.spinner { width: 1.8rem; height: 1.8rem; border-radius: 9999px; border: 3px solid var(--brand-500); border-top-color: transparent; animation: spin 0.85s linear infinite; }

.wizard-layout { display: flex; flex-direction: column; gap: 1.5rem; }
.wizard { display: flex; flex-direction: column; gap: 1.25rem; }
.steps { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem; }
.step { padding: 1rem 1.1rem; border-radius: 1rem; border: 1px solid color-mix(in srgb, var(--border) 75%, transparent); background: color-mix(in srgb, var(--surface) 92%, transparent); color: var(--text-muted); font-size: 12px; font-weight: 600; }
.step.active { border-color: color-mix(in srgb, var(--brand-500) 35%, var(--border)); background: color-mix(in srgb, var(--brand-50) 50%, var(--surface)); color: var(--text); }
.step-content { display: flex; flex-direction: column; gap: 1.25rem; }

.wizard-steps { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem; }
.wizard-step { display: flex; align-items: center; gap: 1rem; border: 1px solid color-mix(in srgb, var(--border) 75%, transparent); border-radius: 1rem; padding: 1rem 1.1rem; background: color-mix(in srgb, var(--surface) 92%, transparent); }
.wizard-step.active { border-color: color-mix(in srgb, var(--brand-500) 35%, var(--border)); background: color-mix(in srgb, var(--brand-50) 50%, var(--surface)); }
.wizard-step.done { border-color: color-mix(in srgb, var(--brand-500) 22%, var(--border)); }
.wizard-step-index { width: 2rem; height: 2rem; border-radius: 9999px; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; background: var(--brand-50); color: var(--brand-600); flex: 0 0 auto; }
.wizard-step strong { display: block; font-size: 0.95rem; color: var(--text); }
.wizard-step small { display: block; margin-top: 0.15rem; color: var(--text-muted); }

.section-head h3 { margin: 0; font-size: 1rem; font-weight: 700; color: var(--text); }
.section-head p { margin: 0.35rem 0 0; font-size: 0.85rem; color: var(--text-muted); }

.search-inline { display: flex; align-items: center; gap: 1rem; }
.search-field { position: relative; }
.search-field-flex { flex: 1 1 auto; }
.search-icon { position: absolute; left: 0.9rem; top: 50%; transform: translateY(-50%); color: var(--text-muted); pointer-events: none; }
.search-input { width: 100%; padding-left: 2.4rem; }
.search-inline .p-button { flex: 0 0 auto; }

.results-shell { overflow: hidden; border: 1px solid color-mix(in srgb, var(--border) 75%, transparent); border-radius: 1rem; margin-top: 0.35rem; }
.wizard-results-shell { max-height: 320px; overflow: auto; }
.results-table { width: 100%; border-collapse: collapse; }
.results-table thead th { padding: 0.95rem 1.1rem; text-align: left; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; color: var(--text-muted); border-bottom: 1px solid color-mix(in srgb, var(--border) 70%, transparent); background: color-mix(in srgb, var(--surface) 95%, transparent); }
.results-table tbody td { padding: 1rem 1.1rem; border-bottom: 1px solid color-mix(in srgb, var(--border) 65%, transparent); vertical-align: middle; }
.results-table tbody tr:hover, .results-table tbody tr.selected { background: color-mix(in srgb, var(--brand-50) 42%, var(--surface)); }

.selected-posta-banner { border: 1px solid color-mix(in srgb, var(--border) 75%, transparent); background: color-mix(in srgb, var(--surface) 92%, transparent); border-radius: 1rem; padding: 1rem 1.1rem; }
.selected-posta-label { font-size: 0.75rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; color: var(--text-muted); }
.selected-posta-value { font-size: 0.95rem; font-weight: 600; color: var(--text); }

.dialog-footer { display: flex; justify-content: space-between; gap: 1rem; padding-top: 0.75rem; align-items: center; width: 100%; }
.dialog-actions { display: flex; gap: 0.75rem; align-items: center; }
.wizard-footer { margin-top: 0.75rem; }

.compact-empty { min-height: 10rem; }

.results-table .actions-col { width: 9rem; }

.field label { display: block; font-size: 12px; font-weight: 600; color: var(--text-muted); margin-bottom: 6px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px 20px; }
.span-2 { grid-column: span 2; }
.resume-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; border: 1px solid color-mix(in srgb, var(--border) 75%, transparent); background: color-mix(in srgb, var(--surface) 92%, transparent); border-radius: 12px; padding: 12px 14px; }
.resume-label { margin: 0; color: var(--text-muted); font-size: 12px; }
.resume-value { margin: 4px 0 0; font-weight: 600; }
.wizard-actions { display: flex; gap: 8px; justify-content: flex-end; }

.novedad-form { display: grid; grid-template-columns: 1fr 1fr; gap: 12px 16px; margin-bottom: 12px; }
.novedad-actions { grid-column: span 2; display: flex; justify-content: flex-end; }

.info-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; padding: 12px; border-radius: 12px; border: 1px solid color-mix(in srgb, var(--border) 75%, transparent); background: color-mix(in srgb, var(--surface) 92%, transparent); }
.info-col { display: flex; flex-direction: column; gap: 12px; }
.info-item { display: flex; flex-direction: column; justify-content: space-between; padding: 10px 12px; border-radius: 10px; border: 1px solid color-mix(in srgb, var(--border) 75%, transparent); background: color-mix(in srgb, var(--surface) 88%, transparent); }
.info-label { display: block; font-size: 12px; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; color: var(--brand-700); margin-bottom: 6px; }
.info-value { display: block; font-weight: 600; color: var(--text); }
.info-section { margin-top: 14px; }
.info-section h4 { margin: 0 0 8px; }

@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 960px) {
  .guardias-header { align-items: flex-start; }
  .header-actions { margin-left: 0; width: 100%; }
  .filters-top { align-items: stretch; }
  .filter-state-box { min-width: 0; width: 100%; }
  .filter-state-controls { width: 100%; }
  .filter-state-controls > * { flex: 1 1 180px; }
  .steps,
  .resume-grid,
  .novedad-form,
  .info-grid,
  .form-grid {
    grid-template-columns: 1fr;
  }
  .span-2,
  .novedad-actions {
    grid-column: auto;
  }
  .wizard-actions,
  .novedad-actions {
    width: 100%;
    flex-wrap: wrap;
  }
  .wizard-actions > *,
  .novedad-actions > * {
    flex: 1 1 150px;
  }
  .wizard-steps,
  .steps,
  .form-grid,
  .resume-grid,
  .novedad-form,
  .info-grid {
    grid-template-columns: 1fr;
  }
  .search-inline {
    flex-direction: column;
    align-items: stretch;
  }
  .search-inline > * {
    width: 100%;
  }
}

@media (max-width: 640px) {
  .actions { width: 100%; }
  .actions > * { flex: 1 1 auto; }
  .page-title { font-size: 1.35rem; }
  .actions-col { width: auto; }
  .dialog-actions, .header-actions { width: 100%; flex-direction: column; }
  .dialog-actions > *, .header-actions > * { width: 100%; }
}
</style>

<style>
.p-dialog .p-inputtext,
.p-dialog .p-textarea,
.p-dialog .p-select,
.p-dialog .p-datepicker {
  width: 100%;
}
</style>
