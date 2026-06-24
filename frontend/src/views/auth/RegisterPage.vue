<template>
  <div class="auth-page">
    <div class="auth-bg">
      <div class="auth-blob b1"></div>
      <div class="auth-blob b2"></div>
    </div>

    <div class="auth-card card">
      <div class="auth-logo">
        <div class="logo-icon">🤖</div>
        <div>
          <h1 class="logo-name">Amy<span>Learn</span></h1>
          <p>AI-powered English learning</p>
        </div>
      </div>

      <h2>Create your account</h2>
      <p class="auth-sub">Start learning English with Amy today — it's free!</p>

      <form @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label class="form-label">Full Name</label>
          <input v-model="form.name" type="text" class="form-input"
            placeholder="Your name" required />
        </div>
        <div class="form-group">
          <label class="form-label">Email</label>
          <input v-model="form.email" type="email" class="form-input"
            placeholder="your@email.com" required />
        </div>
        <div class="form-group">
          <label class="form-label">Password</label>
          <div class="input-pw-wrap">
            <input v-model="form.password" :type="showPw ? 'text' : 'password'"
              class="form-input" :class="{error: errors.password}"
              placeholder="Min 6 characters" required />
            <button type="button" class="pw-toggle" @click="showPw = !showPw">
              {{ showPw ? '🙈' : '👁️' }}
            </button>
          </div>
          <span class="form-error" v-if="errors.password">{{ errors.password }}</span>
        </div>
        <div class="form-group">
          <label class="form-label">Referral Code <span class="optional">(optional)</span></label>
          <input v-model="form.referral_code" type="text" class="form-input"
            placeholder="Friend's referral code" />
        </div>

        <span class="form-error" v-if="errors.general">{{ errors.general }}</span>

        <button type="submit" class="btn btn-primary w-full btn-lg" :disabled="loading">
          <span class="spinner" v-if="loading"></span>
          <span v-else>Create Account</span>
        </button>
      </form>

      <div class="auth-footer">
        Already have an account?
        <router-link to="/login">Sign in</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useAuthStore } from '@/store/auth'

const auth    = useAuthStore()
const showPw  = ref(false)
const loading = ref(false)
const errors  = reactive({})
const form    = reactive({ name:'', email:'', password:'', referral_code:'' })

async function handleRegister() {
  Object.keys(errors).forEach(k => delete errors[k])
  if (form.password.length < 6) { errors.password = 'Password must be at least 6 characters'; return }
  loading.value = true
  try {
    await auth.register(form.name, form.email, form.password, form.referral_code || undefined)
  } catch(e) {
    errors.general = e.response?.data?.detail || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh; display: flex;
  align-items: center; justify-content: center;
  padding: 24px; position: relative; overflow: hidden;
  background: var(--bg);
}
.auth-bg { position: absolute; inset: 0; pointer-events: none; }
.auth-blob { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.15; }
.b1 { width: 500px; height: 500px; background: var(--p); top: -100px; right: -100px; }
.b2 { width: 400px; height: 400px; background: #a78bfa; bottom: -100px; left: -100px; }
.auth-card { width: 100%; max-width: 440px; position: relative; z-index: 1; padding: 40px; }
.auth-logo { display: flex; align-items: center; gap: 14px; margin-bottom: 28px; }
.logo-icon { font-size: 42px; }
.logo-name { font-size: 24px; font-weight: 800; color: var(--text); margin: 0; }
.logo-name span { color: var(--p); }
.auth-logo p { font-size: 13px; color: var(--text3); margin: 0; }
h2 { font-size: 22px; font-weight: 800; margin-bottom: 4px; }
.auth-sub { color: var(--text3); font-size: 14px; margin-bottom: 28px; }
.auth-form { display: flex; flex-direction: column; gap: 16px; }
.input-pw-wrap { position: relative; }
.input-pw-wrap .form-input { padding-right: 44px; }
.pw-toggle { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); background: none; border: none; cursor: pointer; font-size: 16px; padding: 0; }
.optional { color: var(--text3); font-weight: 400; font-size: 11px; }
.auth-footer { text-align: center; font-size: 14px; color: var(--text2); margin-top: 20px; }
.auth-footer a { font-weight: 600; }
</style>
