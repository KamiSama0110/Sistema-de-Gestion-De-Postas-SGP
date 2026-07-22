import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'

import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

const sgpCorporate = {
  dark: false,
  colors: {
    background: '#F5F5F5',
    'surface-bright': '#FFFFFF',
    primary: '#1565C0',
    'primary-darken-1': '#0D47A1',
    secondary: '#475569',
    'secondary-darken-1': '#334155',
    accent: '#0F766E',
    error: '#B3261E',
    'error-darken-1': '#8C1D18',
    warning: '#E65100',
    info: '#1565C0',
    success: '#2E7D32',
    surface: '#FFFFFF',
    'surface-variant': '#F1F5F9',
    'surface-container': '#F8FAFC',
    'surface-container-low': '#F1F5F9',
    'surface-container-high': '#E2E8F0',
    'on-background': '#1C1B1F',
    'on-surface': '#1C1B1F',
    'on-surface-variant': '#49454F',
    outline: '#79747E',
    'outline-variant': '#CAC4D0',
    'inverse-surface': '#1C1B1F',
    'inverse-on-surface': '#F5F5F5',
  },
}

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'sgpCorporate',
    themes: { sgpCorporate },
  },
  defaults: {
    VBtn: {
      rounded: 'lg',
      fontWeight: 600,
      letterSpacing: 0,
    },
    VCard: {
      rounded: 'lg',
      elevation: 0,
    },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
    },
    VTextarea: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
    },
    VSelect: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
    },
    VAutocomplete: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
    },
    VDialog: {
      maxWidth: 640,
      locationStrategy: 'connected',
    },
    VDataTable: {
      hover: true,
    },
    VChip: {
      rounded: 'lg',
    },
    VAlert: {
      rounded: 'lg',
    },
    VNavigationDrawer: {
      elevation: 0,
    },
  },
})

export default vuetify
