<template>
  <AppLayout>
    <div class="feature-page">
      <div class="feature-header">
        <h1>🏆 Weekly Tournament</h1>
        <p class="text-muted">Compete with learners worldwide. Top XP wins prizes!</p>
      </div>

      <div v-if="loading" class="loading-state"><div class="spinner spinner-lg"></div></div>
      <div v-else-if="data" class="tourn-layout">

        <!-- Timer + your rank -->
        <div class="tourn-top">
          <div class="card timer-card">
            <div class="timer-label">Tournament ends in</div>
            <div class="timer-val">{{ data.days_left }}d left</div>
            <div class="timer-sub">{{ data.week_start?.slice(0,10) }} → {{ data.week_end?.slice(0,10) }}</div>
          </div>
          <div class="card rank-card" v-if="data.your_rank">
            <div class="rank-num">#{{ data.your_rank }}</div>
            <div class="rank-lbl">Your Rank</div>
            <div class="rank-xp">⭐ {{ data.your_xp?.toLocaleString() }} XP</div>
          </div>
          <div class="card prizes-card">
            <h3 class="mb-3">🎁 Prizes</h3>
            <div v-for="p in data.prizes" :key="p.rank" class="prize-row">
              <span class="prize-rank">{{ p.rank }}</span>
              <span class="prize-desc">{{ p.prize }}</span>
            </div>
          </div>
        </div>

        <!-- Leaderboard -->
        <div class="card">
          <h3 class="mb-4">🏅 Top Learners This Week</h3>
          <div class="lb-list">
            <div v-for="u in data.leaderboard" :key="u.rank"
              class="lb-row" :class="{me: u.name === authUser?.name, podium: u.rank <= 3}">
              <div class="lb-rank">
                <span v-if="u.rank===1">🥇</span>
                <span v-else-if="u.rank===2">🥈</span>
                <span v-else-if="u.rank===3">🥉</span>
                <span v-else class="rank-num-sm">#{{ u.rank }}</span>
              </div>
              <div class="avatar avatar-sm">{{ u.name?.[0]?.toUpperCase() }}</div>
              <div class="lb-info">
                <div class="lb-name">{{ u.name }} <span v-if="u.name===authUser?.name" class="you-tag">You</span></div>
                <div class="lb-sub">🔥 {{ u.streak }} streak · Lv.{{ u.level }}</div>
              </div>
              <div class="lb-xp">⭐ {{ u.xp?.toLocaleString() }}</div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </AppLayout>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useAuthStore } from '@/store/auth'
import api from '@/api'
const auth = useAuthStore()
const authUser = auth.user
const data = ref(null); const loading = ref(true)
onMounted(async () => {
  try { const r = await api.get('/tournament/current'); data.value = r.data }
  catch { data.value = { days_left: 5, your_rank: null, your_xp: 0, leaderboard: [], prizes: [], week_start:'', week_end:'' } }
  finally { loading.value = false }
})
</script>
<style scoped>
.tourn-layout { display: flex; flex-direction: column; gap: 20px; }
.tourn-top { display: grid; grid-template-columns: 1fr 1fr 2fr; gap: 16px; }
@media (max-width: 768px) { .tourn-top { grid-template-columns: 1fr; } }
.timer-card { text-align: center; padding: 28px; background: linear-gradient(135deg, rgba(124,92,191,.15), rgba(157,126,224,.08)); border-color: var(--border2); }
.timer-label { font-size: 12px; text-transform: uppercase; letter-spacing: .1em; color: var(--text3); font-family: 'Outfit', sans-serif; }
.timer-val { font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 900; color: var(--p); margin: 6px 0; }
.timer-sub { font-size: 11px; color: var(--text3); }
.rank-card { text-align: center; padding: 28px; }
.rank-num { font-family: 'Outfit', sans-serif; font-size: 2.5rem; font-weight: 900; color: var(--amber); }
.rank-lbl { font-size: 13px; color: var(--text3); }
.rank-xp { margin-top: 8px; font-weight: 700; color: var(--p); }
.prizes-card h3 { font-size: 1rem; }
.prize-row { display: flex; gap: 10px; padding: 7px 0; border-bottom: 1px solid var(--border); font-size: 13px; }
.prize-row:last-child { border-bottom: none; }
.prize-rank { font-weight: 700; color: var(--p); min-width: 40px; flex-shrink: 0; font-family: 'Outfit', sans-serif; }
.prize-desc { color: var(--text2); }
.lb-list { display: flex; flex-direction: column; }
.lb-row { display: flex; align-items: center; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--border); transition: background var(--t); }
.lb-row:last-child { border-bottom: none; }
.lb-row.me { background: var(--p-soft); border-radius: var(--r); padding: 12px 10px; margin: 0 -10px; }
.lb-row.podium .lb-name { font-weight: 700; }
.lb-rank { width: 32px; text-align: center; font-size: 20px; flex-shrink: 0; }
.rank-num-sm { font-size: 13px; font-weight: 700; color: var(--text3); font-family: 'Outfit', sans-serif; }
.lb-info { flex: 1; }
.lb-name { font-size: 14px; font-weight: 600; display: flex; align-items: center; gap: 6px; }
.lb-sub { font-size: 11px; color: var(--text3); margin-top: 2px; }
.lb-xp { font-weight: 700; color: var(--amber); font-size: 13px; font-family: 'Outfit', sans-serif; flex-shrink: 0; }
.you-tag { background: var(--p); color: #fff; font-size: 9px; padding: 1px 6px; border-radius: 99px; font-weight: 700; }
</style>
