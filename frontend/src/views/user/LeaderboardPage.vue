<template>
  <AppLayout>
    <div class="leaderboard-page">
      <div class="page-head">
        <div>
          <h1>Leaderboard</h1>
          <p class="text-muted">All user er moddhe top performer ra automatically ekhane rank hoy.</p>
        </div>
        <button class="btn btn-outline btn-sm" @click="loadLeaderboard" :disabled="loading">
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>

      <div class="card your-rank" v-if="myEntry">
        <div>
          <div class="your-rank-label">Your Position</div>
          <div class="your-rank-name">{{ myEntry.name }}</div>
        </div>
        <div class="your-rank-stats">
          <span>#{{ myEntry.rank }}</span>
          <span>{{ myEntry.xp }} XP</span>
          <span>Level {{ myEntry.level }}</span>
        </div>
      </div>

      <div class="card empty-state" v-if="loading">
        <h3>Loading leaderboard...</h3>
        <p>Top learners der data niye aschi.</p>
      </div>

      <template v-else>
        <div class="podium-grid" v-if="topFour.length">
          <div v-for="user in topFour" :key="user.rank" class="podium-card card" :class="`podium-${user.rank}`">
            <div class="podium-rank">#{{ user.rank }}</div>
            <div class="podium-name">{{ user.name }} <span v-if="isMe(user)">(You)</span></div>
            <div class="podium-xp">{{ user.xp }} XP</div>
            <div class="podium-meta">Lv.{{ user.level }} - {{ user.streak }} day streak</div>
          </div>
        </div>

        <div class="card empty-state" v-if="!users.length">
          <h3>No leaderboard data yet</h3>
          <p>Users start appearing here automatically after they earn XP.</p>
        </div>

        <div class="lb-list card" v-else>
          <div v-for="user in users" :key="user.rank" class="lb-row" :class="{ me: isMe(user) }">
            <div class="lb-rank">{{ user.rank }}</div>
            <div class="avatar avatar-sm">{{ user.name[0].toUpperCase() }}</div>
            <div class="lb-info">
              <div class="lb-name">{{ user.name }} <span v-if="isMe(user)">(You)</span></div>
              <div class="lb-meta">{{ user.streak }} day streak - Level {{ user.level }}</div>
            </div>
            <div class="lb-xp">{{ user.xp }} XP</div>
          </div>
        </div>
      </template>
    </div>
  </AppLayout>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

import api from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useAuthStore } from '@/store/auth'

const auth = useAuthStore()
const users = ref([])
const loading = ref(true)

const topFour = computed(() => users.value.slice(0, 4))
const myEntry = computed(() => users.value.find(user => isMe(user)) || null)

function isMe(user) {
  return user.name === auth.user?.name
}

async function loadLeaderboard() {
  loading.value = true
  try {
    const response = await api.get('/users/leaderboard')
    users.value = response.data
  } catch {
    users.value = []
  } finally {
    loading.value = false
  }
}

onMounted(loadLeaderboard)
</script>

<style scoped>
.leaderboard-page { display: flex; flex-direction: column; gap: 20px; max-width: 860px; }
.page-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.page-head h1 { margin-bottom: 4px; }
.your-rank { display: flex; align-items: center; justify-content: space-between; gap: 12px; border: 1px solid var(--border); }
.your-rank-label { font-size: 12px; font-weight: 700; color: var(--text3); text-transform: uppercase; letter-spacing: .08em; }
.your-rank-name { font-size: 18px; font-weight: 800; color: var(--text); margin-top: 4px; }
.your-rank-stats { display: flex; gap: 14px; flex-wrap: wrap; font-size: 13px; font-weight: 700; color: var(--p); }
.podium-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.podium-card { text-align: center; padding: 18px 14px; border: 1px solid var(--border); }
.podium-1 { background: linear-gradient(180deg, rgba(255, 191, 71, 0.15), var(--bg2)); }
.podium-2 { background: linear-gradient(180deg, rgba(148, 163, 184, 0.18), var(--bg2)); }
.podium-3 { background: linear-gradient(180deg, rgba(251, 146, 60, 0.16), var(--bg2)); }
.podium-4 { background: linear-gradient(180deg, rgba(59, 130, 246, 0.12), var(--bg2)); }
.podium-rank { font-size: 26px; font-weight: 900; color: var(--p); }
.podium-name { font-size: 14px; font-weight: 700; color: var(--text); margin-top: 8px; }
.podium-name span { color: var(--p); }
.podium-xp { font-size: 20px; font-weight: 900; color: var(--amber); margin-top: 8px; }
.podium-meta { font-size: 12px; color: var(--text3); margin-top: 4px; }
.lb-list { padding: 0; overflow: hidden; }
.lb-row { display: flex; align-items: center; gap: 14px; padding: 14px 20px; border-bottom: 1px solid var(--border); transition: background .15s; }
.lb-row:last-child { border-bottom: none; }
.lb-row:hover { background: var(--bg3); }
.lb-row.me { background: var(--p-soft); }
.lb-rank { width: 36px; text-align: center; font-size: 20px; font-weight: 800; color: var(--text3); flex-shrink: 0; }
.lb-info { flex: 1; }
.lb-name { font-size: 14px; font-weight: 600; color: var(--text); }
.lb-name span { color: var(--p); }
.lb-meta { font-size: 12px; color: var(--text3); }
.lb-xp { font-size: 14px; font-weight: 700; color: var(--amber); flex-shrink: 0; }
.empty-state { text-align: center; }
.empty-state h3 { margin-bottom: 6px; }
.empty-state p { margin: 0; color: var(--text3); }
@media (max-width: 768px) {
  .page-head, .your-rank { flex-direction: column; align-items: flex-start; }
  .podium-grid { grid-template-columns: 1fr 1fr; }
}
</style>
