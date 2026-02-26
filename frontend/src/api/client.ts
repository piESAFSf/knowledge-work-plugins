import axios from 'axios'

export const api = axios.create({
  baseURL: '/api/v1',
  withCredentials: true,
})

api.interceptors.request.use((config) => {
  const token = document.cookie.split('; ').find((row) => row.startsWith('csrf_token='))?.split('=')[1]
  if (token) config.headers['X-CSRF-Token'] = token
  return config
})
