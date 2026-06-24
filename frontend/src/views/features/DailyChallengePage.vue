<template>
  <AppLayout>
    <div class="feature-page">
      <div class="feature-header">
        <h1>⚡ Daily Challenge</h1>
        <p class="text-muted">Complete daily challenges to earn bonus XP and build your streak</p>
      </div>

      <div class="dc-grid">
        <!-- Today's Challenge -->
        <div class="card dc-main" v-if="challenge">
          <div class="dc-date">{{ today }}</div>
          <div class="dc-icon">{{ challenge.icon }}</div>
          <h2>{{ challenge.title }}</h2>
          <p class="dc-desc">{{ challenge.description }}</p>
          <div class="dc-xp">+{{ challenge.xp }} XP</div>
          <button v-if="!completed" class="btn btn-primary btn-lg w-full mt-4" @click="complete" :disabled="loading">
            <span class="spinner" v-if="loading"></span>
            <span v-else>Complete Challenge ✓</span>
          </button>
          <div v-else class="dc-done">
            <span>🎉</span> Challenge completed! +{{ challenge.xp }} XP earned
          </div>
        </div>
        <div class="card dc-main loading-state" v-else><div class="spinner spinner-lg"></div></div>

        <!-- Right side -->
        <div class="dc-right">
          <!-- Streak -->
          <div class="card dc-streak">
            <div class="streak-fire">🔥</div>
            <div class="streak-num">{{ streak }}</div>
            <div class="streak-lbl">Day Streak</div>
            <div class="streak-bar">
              <div v-for="i in 7" :key="i" class="streak-dot" :class="{active: i <= (streak % 7 || 7)}"></div>
            </div>
            <p class="text-xs text-muted mt-2">Complete 7 days for a weekly bonus!</p>
          </div>

          <!-- All challenge types -->
          <div class="card">
            <h3 class="mb-3">All Challenges</h3>
            <div v-for="c in allChallenges" :key="c.id" class="ctype-row">
              <span class="ctype-icon">{{ c.icon }}</span>
              <div class="ctype-info">
                <div class="ctype-name">{{ c.title }}</div>
                <div class="text-xs text-muted">+{{ c.xp }} XP</div>
              </div>
              <span class="chip chip-purple">{{ c.type }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
<script setup>
import { ref, onMounted, computed } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { toast } from 'vue3-toastify'
import api from '@/api'

const challenge = ref(null)
const completed  = ref(false)
const streak     = ref(0)
const loading    = ref(false)

const today = new Date().toLocaleDateString('en-US', { weekday:'long', month:'long', day:'numeric' })

const allChallenges = [
  { id:1, type:'vocabulary', icon:'📖', title:'Word of the Day',     xp:20 },
  { id:2, type:'grammar',    icon:'✏️',  title:'Grammar Fix',         xp:25 },
  { id:3, type:'speaking',   icon:'🎤', title:'Speaking Challenge',  xp:30 },
  { id:4, type:'quiz',       icon:'🧠', title:'Quick Quiz',          xp:35 },
  { id:5, type:'writing',    icon:'📝', title:'Write a Paragraph',   xp:30 },
  { id:6, type:'roleplay',   icon:'🎭', title:'Roleplay Scenario',   xp:40 },
  { id:7, type:'reading',    icon:'📰', title:'Read & Summarize',    xp:25 },
]

async function load() {
  try {
    const r = await api.get('/daily-challenge/today')
    challenge.value = r.data.challenge
    completed.value = r.data.completed
    streak.value = r.data.streak
  } catch { challenge.value = allChallenges[new Date().getDay() % allChallenges.length] }
}

async function complete() {
  loading.value = true
  try {
    const r = await api.post('/daily-challenge/complete')
    completed.value = true
    streak.value = r.data.streak
    toast.success(`🎉 +${r.data.xp_earned} XP earned! Streak: ${r.data.streak} days 🔥`)
  } catch(e) { toast.error('Failed to complete challenge') }
  finally { loading.value = false }
}

onMounted(load)
</script>
<style scoped>
.dc-grid { display: grid; grid-template-columns: 1fr 360px; gap: 20px; }
@media (max-width: 900px) { .dc-grid { grid-template-columns: 1fr; } }
.dc-main { text-align: center; padding: 36px 28px; }
.dc-date { font-size: 12px; color: var(--text3); text-transform: uppercase; letter-spacing: .1em; margin-bottom: 16px; font-family: 'Outfit', sans-serif; }
.dc-icon { font-size: 56px; margin-bottom: 14px; }
.dc-main h2 { font-size: 1.5rem; margin-bottom: 10px; }
.dc-desc { color: var(--text2); font-size: 15px; max-width: 380px; margin: 0 auto; }
.dc-xp { display: inline-block; margin-top: 16px; padding: 6px 18px; background: linear-gradient(135deg, var(--p), var(--p2)); color: #fff; border-radius: 99px; font-weight: 800; font-size: 15px; font-family: 'Outfit', sans-serif; }
.dc-done { background: rgba(16,185,129,.12); border: 1px solid rgba(16,185,129,.25); color: var(--green); border-radius: var(--r); padding: 14px; margin-top: 16px; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 8px; }
.dc-right { display: flex; flex-direction: column; gap: 16px; }
.dc-streak { text-align: center; padding: 28px; }
.streak-fire { font-size: 40px; margin-bottom: 6px; }
.streak-num { font-family: 'Outfit', sans-serif; font-size: 3rem; font-weight: 900; color: var(--amber); line-height: 1; }
.streak-lbl { font-size: 13px; color: var(--text3); margin-top: 4px; }
.streak-bar { display: flex; gap: 6px; justify-content: center; margin-top: 14px; }
.streak-dot { width: 28px; height: 8px; border-radius: 99px; background: var(--bg3); transition: background .3s; }
.streak-dot.active { background: var(--amber); box-shadow: 0 0 8px rgba(245,158,11,.4); }
.ctype-row { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid var(--border); }
.ctype-row:last-child { border-bottom: none; }
.ctype-icon { font-size: 20px; width: 28px; text-align: center; flex-shrink: 0; }
.ctype-info { flex: 1; }
.ctype-name { font-size: 13px; font-weight: 600; color: var(--text); }
</style>
