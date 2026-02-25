import axios from 'axios'

export const api = axios.create({
  baseURL: '/api/v1',
  withCredentials: true
})

api.interceptors.request.use((config) => {
  const csrf = document.cookie.split('; ').find((x) => x.startsWith('csrf_token='))?.split('=')[1]
  if (csrf) config.headers['X-CSRF-Token'] = csrf
  return config
})
