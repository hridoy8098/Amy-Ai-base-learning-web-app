import axios from 'axios'
import { toast } from 'vue3-toastify'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// Attach token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('amy_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Handle responses
api.interceptors.response.use(
  res => res,
  err => {
    const status  = err.response?.status
    const message = err.response?.data?.detail || err.message
    const url     = err.config?.url || ''

    if (status === 401) {
      // login/register এ 401 আসলে logout করো না
      const isAuthCall = url.includes('/auth/login') || url.includes('/auth/register')
      if (!isAuthCall) {
        localStorage.removeItem('amy_token')
        localStorage.removeItem('amy_user')
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login'
        }
      }
      return Promise.reject(err)
    }

    if (status === 402) {
      toast.warning(message || 'Upgrade your plan to continue')
      return Promise.reject(err)
    }

    // 403 এ কিছু করো না — sidebar/topbar এ notification fail হলে logout হবে না
    if (status === 403) {
      return Promise.reject(err)
    }

    if (status >= 500) {
      toast.error('Server error. Please try again.')
    }

    return Promise.reject(err)
  }
)

export default api