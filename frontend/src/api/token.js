let accessToken = null

export function getAccessToken() {
  return accessToken
}

export function setAccessToken(token) {
  accessToken = token
}

export function clearAccessToken() {
  accessToken = null
}

export function getRefreshToken() {
  return sessionStorage.getItem('refresh_token')
}

export function setRefreshToken(token) {
  sessionStorage.setItem('refresh_token', token)
}

export function clearRefreshToken() {
  sessionStorage.removeItem('refresh_token')
}

export function clearTokens() {
  clearAccessToken()
  clearRefreshToken()
}
