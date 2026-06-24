<template>
  <AppLayout>
    <div class="profile-page">
      <div class="profile-grid">

        <!-- Left: Avatar + info -->
        <div class="profile-left">
          <div class="card avatar-card">
            <div class="avatar-wrap">
              <div class="avatar avatar-xl" style="position:relative">
                <img v-if="auth.user?.avatar" :src="auth.user.avatar" alt="avatar"
                  style="width:100%;height:100%;border-radius:50%;object-fit:cover" />
                <span v-else>{{ initials }}</span>
                <label class="avatar-upload-btn" title="Change avatar">
                  📷
                  <input type="file" accept="image/*" @change="uploadAvatar" hidden />
                </label>
              </div>
            </div>
            <h2 class="mt-4 text-center">{{ auth.user?.name }}</h2>
            <p class="text-center text-muted text-sm">{{ auth.user?.email }}</p>
            <div class="text-center mt-2">
              <span class="chip chip-purple">{{ auth.user?.subscription_plan || 'free' }}</span>
            </div>

            <div class="stats-mini">
              <div class="sm-item">
                <div class="sm-val">{{ auth.user?.xp_points || 0 }}</div>
                <div class="sm-label">XP</div>
              </div>
              <div class="sm-item">
                <div class="sm-val">{{ auth.user?.streak_days || 0 }}</div>
                <div class="sm-label">Streak</div>
              </div>
              <div class="sm-item">
                <div class="sm-val">Lv.{{ auth.user?.level || 1 }}</div>
                <div class="sm-label">Level</div>
              </div>
            </div>

            <!-- Referral code -->
            <div class="referral-box mt-4" v-if="auth.user?.referral_code">
              <div class="ref-label">🎁 Your Referral Code</div>
              <div class="ref-code" @click="copyRef">
                {{ auth.user.referral_code }}
                <span class="ref-copy">📋</span>
              </div>
              <p class="text-xs text-muted mt-1">Share & earn 50 XP per referral</p>
            </div>
          </div>
        </div>

        <!-- Right: Edit forms -->
        <div class="profile-right">
          <!-- Edit profile -->
          <div class="card mb-4">
            <h3 class="mb-4">Edit Profile</h3>
            <form @submit.prevent="saveProfile" class="form-cols">
              <div class="form-group">
                <label class="form-label">Full Name</label>
                <input v-model="profileForm.name" type="text" class="form-input" required />
              </div>
              <div class="form-group">
                <label class="form-label">Email</label>
                <input v-model="profileForm.email" type="email" class="form-input" required />
              </div>
              <div class="form-group" style="grid-column: 1/-1">
                <label class="form-label">Bio</label>
                <textarea v-model="profileForm.bio" class="form-input" rows="3"
                  placeholder="Tell us about yourself..."></textarea>
              </div>
              <div style="grid-column: 1/-1">
                <button type="submit" class="btn btn-primary" :disabled="saving">
                  <span class="spinner" v-if="saving"></span>
                  <span v-else>Save Changes</span>
                </button>
              </div>
            </form>
          </div>

          <!-- Change password -->
          <div class="card">
            <h3 class="mb-4">Change Password</h3>
            <form @submit.prevent="changePassword" class="form-cols">
              <div class="form-group">
                <label class="form-label">Current Password</label>
                <input v-model="pwForm.current" type="password" class="form-input" required />
              </div>
              <div class="form-group">
                <label class="form-label">New Password</label>
                <input v-model="pwForm.newPw" type="password" class="form-input"
                  :class="{error: pwError}" required />
                <span class="form-error" v-if="pwError">{{ pwError }}</span>
              </div>
              <div class="form-group">
                <label class="form-label">Confirm Password</label>
                <input v-model="pwForm.confirm" type="password" class="form-input" required />
              </div>
              <div style="grid-column: 1/-1">
                <button type="submit" class="btn btn-outline" :disabled="pwSaving">
                  <span class="spinner" v-if="pwSaving"></span>
                  <span v-else>Update Password</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useAuthStore } from '@/store/auth'
import { toast } from 'vue3-toastify'
import api from '@/api'

const auth = useAuthStore()
const saving  = ref(false)
const pwSaving = ref(false)
const pwError  = ref('')

const initials = computed(() => {
  const name = auth.user?.name || ''
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0,2)
})

const profileForm = reactive({ name: '', email: '', bio: '' })
const pwForm = reactive({ current: '', newPw: '', confirm: '' })

onMounted(() => {
  profileForm.name  = auth.user?.name  || ''
  profileForm.email = auth.user?.email || ''
  profileForm.bio   = auth.user?.bio   || ''
})

async function saveProfile() {
  saving.value = true
  try {
    await auth.updateProfile(profileForm)
  } catch(e) {
    toast.error(e.response?.data?.detail || 'Failed to update')
  } finally {
    saving.value = false
  }
}

async function changePassword() {
  pwError.value = ''
  if (pwForm.newPw !== pwForm.confirm) { pwError.value = 'Passwords do not match'; return }
  if (pwForm.newPw.length < 6) { pwError.value = 'Min 6 characters'; return }
  pwSaving.value = true
  try {
    await api.post('/auth/change-password', {
      current_password: pwForm.current,
      new_password: pwForm.newPw,
    })
    toast.success('Password changed!')
    pwForm.current = pwForm.newPw = pwForm.confirm = ''
  } catch(e) {
    pwError.value = e.response?.data?.detail || 'Failed'
  } finally {
    pwSaving.value = false
  }
}

async function uploadAvatar(e) {
  const file = e.target.files[0]
  if (!file) return
  const fd = new FormData()
  fd.append('file', file)
  try {
    await api.post('/upload/avatar', fd)
    await auth.fetchMe()
    toast.success('Avatar updated!')
  } catch(e) {
    toast.error('Upload failed')
  }
}

function copyRef() {
  navigator.clipboard.writeText(auth.user?.referral_code || '')
  toast.success('Referral code copied!')
}
</script>

<style scoped>
.profile-grid { display: grid; grid-template-columns: 300px 1fr; gap: 24px; align-items: start; }
.profile-left .card { text-align: center; }
.avatar-wrap { display: flex; justify-content: center; }
.avatar.avatar-xl { position: relative; width: 96px; height: 96px; font-size: 32px; }
.avatar-upload-btn {
  position: absolute; bottom: 0; right: 0;
  width: 28px; height: 28px; border-radius: 50%;
  background: var(--p); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; cursor: pointer; border: 2px solid var(--bg2);
}
.stats-mini { display: flex; justify-content: center; gap: 20px; margin-top: 16px; }
.sm-item { text-align: center; }
.sm-val { font-size: 18px; font-weight: 800; color: var(--p); }
.sm-label { font-size: 11px; color: var(--text3); }
.referral-box { background: var(--bg3); border-radius: var(--r); padding: 12px; }
.ref-label { font-size: 12px; color: var(--text3); margin-bottom: 6px; }
.ref-code {
  font-size: 16px; font-weight: 800; color: var(--p);
  letter-spacing: 0.1em; cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 8px;
}
.ref-copy { font-size: 14px; opacity: 0.7; }
.form-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 768px) {
  .profile-grid { grid-template-columns: 1fr; }
  .form-cols { grid-template-columns: 1fr; }
}
</style>
