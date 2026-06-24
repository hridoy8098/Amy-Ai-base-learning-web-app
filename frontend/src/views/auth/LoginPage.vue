<template>
  <div class="auth-page">
    <div class="auth-bg">
      <div class="auth-blob b1"></div>
      <div class="auth-blob b2"></div>
    </div>

    <div class="auth-card card">
      <!-- Logo -->
      <div class="auth-logo">
        <div class="logo-icon">🤖</div>
        <div>
          <h1 class="logo-name">Amy<span>Learn</span></h1>
          <p>AI-powered English learning</p>
        </div>
      </div>

      <h2>Welcome back!</h2>
      <p class="auth-sub">Sign in to continue your learning journey</p>

      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label class="form-label">Email</label>
          <input v-model="email" type="email" class="form-input" :class="{error: errors.email}"
            placeholder="your@email.com" required autocomplete="email" />
          <span class="form-error" v-if="errors.email">{{ errors.email }}</span>
        </div>

        <div class="form-group">
          <label class="form-label">Password</label>
          <div class="input-pw-wrap">
            <input v-model="password" :type="showPw ? 'text' : 'password'"
              class="form-input" :class="{error: errors.password}"
              placeholder="••••••••" required autocomplete="current-password" />
            <button type="button" class="pw-toggle" @click="showPw = !showPw">
              {{ showPw ? '🙈' : '👁️' }}
            </button>
          </div>
          <span class="form-error" v-if="errors.password">{{ errors.password }}</span>
        </div>

        <button type="submit" class="btn btn-primary w-full btn-lg" :disabled="loading">
          <span class="spinner" v-if="loading"></span>
          <span v-else>Sign In</span>
        </button>
      </form>

      <div class="auth-divider"><span>or</span></div>

      <div class="auth-footer">
        Don't have an account?
        <router-link to="/register">Create account</router-link>
      </div>

      <!-- Demo credentials -->
      <div class="demo-note">
        <span>🔑 Demo admin:</span>
        <code>admin@amy.com / admin123</code>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useAuthStore } from '@/store/auth'

const auth     = useAuthStore()
const email    = ref('')
const password = ref('')
const showPw   = ref(false)
const loading  = ref(false)
const errors   = reactive({})

async function handleLogin() {
  Object.keys(errors).forEach(k => delete errors[k])
  loading.value = true
  try {
    await auth.login(email.value, password.value)
  } catch(e) {
    const msg = e.response?.data?.detail || 'Login failed'
    errors.email = msg
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
.auth-blob {
  position: absolute; border-radius: 50%;
  filter: blur(80px); opacity: 0.15;
}
.b1 { width: 500px; height: 500px; background: var(--p); top: -100px; left: -100px; }
.b2 { width: 400px; height: 400px; background: #a78bfa; bottom: -100px; right: -100px; }

.auth-card {
  width: 100%; max-width: 440px; position: relative; z-index: 1;
  padding: 40px;
}
.auth-logo {
  display: flex; align-items: center; gap: 14px;
  margin-bottom: 28px;
}
.logo-icon { font-size: 42px; }
.logo-name { font-size: 24px; font-weight: 800; color: var(--text); margin: 0; }
.logo-name span { color: var(--p); }
.auth-logo p { font-size: 13px; color: var(--text3); margin: 0; }

h2 { font-size: 22px; font-weight: 800; margin-bottom: 4px; }
.auth-sub { color: var(--text3); font-size: 14px; margin-bottom: 28px; }

.auth-form { display: flex; flex-direction: column; gap: 16px; }

.input-pw-wrap { position: relative; }
.input-pw-wrap .form-input { padding-right: 44px; }
.pw-toggle {
  position: absolute; right: 12px; top: 50%;
  transform: translateY(-50%);
  background: none; border: none; cursor: pointer; font-size: 16px; padding: 0;
}

.auth-divider {
  display: flex; align-items: center; gap: 12px;
  margin: 20px 0; color: var(--text3); font-size: 13px;
}
.auth-divider::before, .auth-divider::after {
  content: ''; flex: 1; height: 1px; background: var(--border);
}

.auth-footer { text-align: center; font-size: 14px; color: var(--text2); }
.auth-footer a { font-weight: 600; }

.demo-note {
  margin-top: 16px; padding: 10px 14px;
  background: var(--bg3); border-radius: var(--r);
  font-size: 12px; color: var(--text3);
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
}
.demo-note code {
  background: var(--p-soft); color: var(--p);
  padding: 2px 8px; border-radius: 6px; font-size: 11px;
}
</style>
