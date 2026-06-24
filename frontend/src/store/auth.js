import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'
import { toast } from 'vue3-toastify'
import { clearCurrentQuizCache } from '@/utils/quizHistory'

export const useAuthStore = defineStore('auth', () => {
  let savedUser = null
  try { savedUser = JSON.parse(localStorage.getItem('amy_user')) } catch {}
  const user  = ref(savedUser)
  const token = ref(localStorage.getItem('amy_token') || null)

  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const isAdmin    = computed(() => ['admin','superadmin'].includes(user.value?.role))
  const isPaid     = computed(() => ['basic','pro','premium'].includes(user.value?.subscription_plan))

  function setAuth(data) {
    token.value = data.token
    user.value  = data.user
    localStorage.setItem('amy_token', data.token)
    localStorage.setItem('amy_user',  JSON.stringify(data.user))
  }

  function clearAuth() {
    clearCurrentQuizCache()
    token.value = null
    user.value  = null
    localStorage.removeItem('amy_token')
    localStorage.removeItem('amy_user')
  }

  async function login(email, password) {
  const res = await api.post('/auth/login', { email, password })
  setAuth(res.data)
  toast.success(`Welcome back, ${res.data.user.name}! 👋`)
  await new Promise(resolve => setTimeout(resolve, 100))
  const { default: router } = await import('@/router')
  const dest = ['admin','superadmin'].includes(res.data.user.role) ? '/admin' : '/dashboard'
  await router.push(dest)
  return res.data
}

  async function register(name, email, password, referral_code) {
    const res = await api.post('/auth/register', { name, email, password, referral_code })
    setAuth(res.data)
    toast.success('Account created! Welcome to Amy Learning 🎉')
    const { default: router } = await import('@/router')
    await router.push('/dashboard')
    return res.data
  }

  async function fetchMe() {
    try {
      const res = await api.get('/auth/me')
      user.value = res.data
      localStorage.setItem('amy_user', JSON.stringify(res.data))
      return res.data
    } catch {
      clearAuth()
    }
  }

  async function updateProfile(data) {
    const res = await api.put('/auth/profile', data)
    user.value = res.data.user
    localStorage.setItem('amy_user', JSON.stringify(res.data.user))
    toast.success('Profile updated!')
    return res.data
  }

  async function logout() {
    clearAuth()
    const { default: router } = await import('@/router')
    router.push('/login')
    toast.info('Logged out')
  }

  return { user, token, isLoggedIn, isAdmin, isPaid,
           login, register, logout, fetchMe, updateProfile, setAuth }
})
