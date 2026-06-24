<template>
  <AppLayout>
    <div class="dashboard">
      <!-- Welcome -->
      <div class="welcome-banner">
        <div class="wb-left">
          <h1>Hello, {{ auth.user?.name?.split(' ')[0] }}! 👋</h1>
          <p>Continue your English learning journey. You're doing great!</p>
          <div class="wb-actions">
            <router-link to="/amy" class="btn btn-primary">Chat with Amy 🤖</router-link>
            <router-link to="/quiz" class="btn btn-secondary">Take a Quiz 🧠</router-link>
          </div>
        </div>
        <div class="wb-robot">🤖</div>
      </div>

      <!-- Stats -->
      <div class="stats-grid">
        <div class="stat-card card">
          <div class="stat-icon">⭐</div>
          <div class="stat-val">{{ stats.xp_points || 0 }}</div>
          <div class="stat-label">XP Points</div>
        </div>
        <div class="stat-card card">
          <div class="stat-icon">🔥</div>
          <div class="stat-val">{{ stats.streak_days || 0 }}</div>
          <div class="stat-label">Day Streak</div>
        </div>
        <div class="stat-card card">
          <div class="stat-icon">📚</div>
          <div class="stat-val">{{ stats.enrolled_courses || 0 }}</div>
          <div class="stat-label">Courses</div>
        </div>
        <div class="stat-card card">
          <div class="stat-icon">🎓</div>
          <div class="stat-val">{{ stats.completed_courses || 0 }}</div>
          <div class="stat-label">Completed</div>
        </div>
        <div class="stat-card card">
          <div class="stat-icon">🧠</div>
          <div class="stat-val">{{ stats.quiz_taken || 0 }}</div>
          <div class="stat-label">Quizzes</div>
        </div>
        <div class="stat-card card">
          <div class="stat-icon">💬</div>
          <div class="stat-val">{{ stats.amy_messages || 0 }}</div>
          <div class="stat-label">Amy Chats</div>
        </div>
      </div>

      <!-- Level progress -->
      <div class="level-card card">
        <div class="level-header">
          <div>
            <h3>Level {{ auth.user?.level || 1 }}</h3>
            <p>{{ xpToNextLevel }} XP to next level</p>
          </div>
          <div class="level-badge">Lv.{{ auth.user?.level || 1 }}</div>
        </div>
        <div class="progress-bar mt-2">
          <div class="progress-fill" :style="`width: ${levelProgress}%`"></div>
        </div>
        <div class="level-labels">
          <span>{{ currentLevelXP }} XP</span>
          <span>{{ nextLevelXP }} XP</span>
        </div>
      </div>

      <!-- My courses + Amy usage -->
      <div class="dash-grid">
        <!-- My courses -->
        <div>
          <div class="section-header">
            <h3>My Courses</h3>
            <router-link to="/my-courses" class="btn btn-outline btn-sm">View all</router-link>
          </div>
          <div v-if="myCourses.length === 0" class="empty-state">
            <div class="icon">📚</div>
            <h3>No courses yet</h3>
            <p>Browse courses and start learning</p>
            <router-link to="/courses" class="btn btn-primary btn-sm mt-4">Browse Courses</router-link>
          </div>
          <div class="course-list" v-else>
            <router-link v-for="c in myCourses.slice(0,4)" :key="c.course_id"
              :to="`/courses/${c.slug}`" class="course-item card card-hover">
              <div class="ci-thumb">
                <img v-if="c.thumbnail" :src="c.thumbnail" :alt="c.title" />
                <div v-else class="ci-thumb-placeholder">📖</div>
              </div>
              <div class="ci-info">
                <div class="ci-title">{{ c.title }}</div>
                <div class="progress-bar mt-1">
                  <div class="progress-fill" :style="`width:${c.progress}%`"></div>
                </div>
                <div class="ci-prog">{{ c.progress.toFixed(0) }}% complete</div>
              </div>
              <span class="chip chip-green" v-if="c.completed">Done</span>
            </router-link>
          </div>
        </div>

        <!-- Amy usage + quick actions -->
        <div>
          <!-- Amy usage -->
          <div class="card mb-4" v-if="amyUsage">
            <h3 class="mb-4">Amy Usage Today</h3>
            <div class="usage-row">
              <span>💬 Messages</span>
              <div class="usage-bar-wrap">
                <div class="progress-bar">
                  <div class="progress-fill" :style="`width:${usagePct(amyUsage.messages_used, amyUsage.messages_limit)}%`"></div>
                </div>
              </div>
              <span class="usage-count">{{ amyUsage.messages_used }}/{{ amyUsage.is_paid ? '∞' : amyUsage.messages_limit }}</span>
            </div>
            <div class="usage-row mt-2">
              <span>🎤 Voice</span>
              <div class="usage-bar-wrap">
                <div class="progress-bar">
                  <div class="progress-fill" :style="`width:${usagePct(amyUsage.voice_used, amyUsage.voice_limit)}%`"></div>
                </div>
              </div>
              <span class="usage-count">{{ amyUsage.voice_used }}/{{ amyUsage.is_paid ? '∞' : amyUsage.voice_limit }}</span>
            </div>
            <router-link v-if="!amyUsage.is_paid" to="/pricing" class="btn btn-primary btn-sm w-full mt-4">
              ⚡ Upgrade for Unlimited
            </router-link>
          </div>

          <!-- Quick actions -->
          <div class="quick-actions card">
            <h3 class="mb-4">Quick Actions</h3>
            <div class="qa-grid">
              <router-link to="/amy" class="qa-btn">
                <span class="qa-icon">🤖</span>
                <span>Talk to Amy</span>
              </router-link>
              <router-link to="/quiz" class="qa-btn">
                <span class="qa-icon">🧠</span>
                <span>Take Quiz</span>
              </router-link>
              <router-link to="/courses" class="qa-btn">
                <span class="qa-icon">📚</span>
                <span>Browse Courses</span>
              </router-link>
              <router-link to="/leaderboard" class="qa-btn">
                <span class="qa-icon">🏆</span>
                <span>Leaderboard</span>
              </router-link>
            </div>
          </div>

          <div class="card mt-4" v-if="leaderboard.length">
            <div class="section-header">
              <h3>Top 4 Learners</h3>
              <router-link to="/leaderboard" class="btn btn-outline btn-sm">Full board</router-link>
            </div>
            <div class="leaderboard-mini">
              <div v-for="user in leaderboard" :key="user.rank" class="lb-mini-row" :class="{ me: isMe(user) }">
                <div class="lb-mini-rank">{{ user.rank }}</div>
                <div class="lb-mini-info">
                  <div class="lb-mini-name">{{ user.name }} <span v-if="isMe(user)">(You)</span></div>
                  <div class="lb-mini-meta">Lv.{{ user.level }} · {{ user.streak }} day streak</div>
                </div>
                <div class="lb-mini-xp">{{ user.xp }} XP</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent badges -->
      <div v-if="badges.length > 0">
        <div class="section-header">
          <h3>My Badges</h3>
          <router-link to="/profile" class="btn btn-outline btn-sm">View all</router-link>
        </div>
        <div class="badges-row">
          <div v-for="b in badges.slice(0,8)" :key="b.id" class="badge-card card" :title="b.description">
            <div class="badge-icon">{{ b.icon || '🏅' }}</div>
            <div class="badge-name">{{ b.name }}</div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useAuthStore } from '@/store/auth'
import api from '@/api'

const auth      = useAuthStore()
const stats     = ref({})
const myCourses = ref([])
const amyUsage  = ref(null)
const badges    = ref([])
const leaderboard = ref([])

const LEVEL_XP = [0,100,300,600,1000,1500,2200,3000,4000,5500,7500]

const userXP = computed(() => auth.user?.xp_points || 0)
const userLvl = computed(() => auth.user?.level || 1)
const currentLevelXP = computed(() => LEVEL_XP[userLvl.value - 1] || 0)
const nextLevelXP    = computed(() => LEVEL_XP[userLvl.value] || 9999)
const xpToNextLevel  = computed(() => Math.max(0, nextLevelXP.value - userXP.value))
const levelProgress  = computed(() => {
  const range = nextLevelXP.value - currentLevelXP.value
  const done  = userXP.value - currentLevelXP.value
  return Math.min(100, Math.round((done / range) * 100))
})

function usagePct(used, limit) {
  if (!limit || limit > 9000) return 0
  return Math.min(100, Math.round((used / limit) * 100))
}

function isMe(user) {
  return user.name === auth.user?.name
}

onMounted(async () => {
  const [s, mc, u, b, lb] = await Promise.allSettled([
    api.get('/auth/stats'),
    api.get('/users/my-courses'),
    api.get('/amy/usage'),
    api.get('/users/badges'),
    api.get('/users/leaderboard', { params: { limit: 4 } }),
  ])
  if (s.status === 'fulfilled')  stats.value     = s.value.data
  if (mc.status === 'fulfilled') myCourses.value = mc.value.data
  if (u.status === 'fulfilled')  amyUsage.value  = u.value.data
  if (b.status === 'fulfilled')  badges.value    = b.value.data
  if (lb.status === 'fulfilled') leaderboard.value = lb.value.data
})
</script>

<style scoped>
.dashboard { display: flex; flex-direction: column; gap: 28px; }

.welcome-banner {
  background: linear-gradient(135deg, var(--p), #a78bfa);
  border-radius: var(--r2); padding: 32px;
  display: flex; align-items: center; justify-content: space-between;
  color: #fff;
}
.welcome-banner h1 { color: #fff; margin-bottom: 6px; font-size: 1.8rem; }
.welcome-banner p  { color: rgba(255,255,255,0.85); font-size: 15px; margin-bottom: 20px; }
.wb-actions { display: flex; gap: 10px; flex-wrap: wrap; }
.wb-actions .btn-primary  { background: #fff; color: var(--p); box-shadow: none; }
.wb-actions .btn-secondary { background: rgba(255,255,255,0.2); color: #fff; border-color: rgba(255,255,255,0.4); }
.wb-robot { font-size: 80px; opacity: 0.9; flex-shrink: 0; }

.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.stat-card { text-align: center; padding: 20px 16px; }
.stat-icon { font-size: 28px; margin-bottom: 8px; }
.stat-val  { font-size: 28px; font-weight: 800; color: var(--p); }
.stat-label { font-size: 12px; color: var(--text3); font-weight: 600; margin-top: 2px; }

.level-card { }
.level-header { display: flex; justify-content: space-between; align-items: center; }
.level-header h3 { margin-bottom: 2px; }
.level-header p  { font-size: 13px; color: var(--text3); margin: 0; }
.level-badge {
  width: 52px; height: 52px; border-radius: 50%;
  background: linear-gradient(135deg, var(--p), #a78bfa);
  color: #fff; font-size: 13px; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
}
.level-labels { display: flex; justify-content: space-between; font-size: 11px; color: var(--text3); margin-top: 4px; }

.dash-grid { display: grid; grid-template-columns: 1fr 360px; gap: 24px; align-items: start; }
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.section-header h3 { margin: 0; }

.course-list { display: flex; flex-direction: column; gap: 10px; }
.course-item { display: flex; align-items: center; gap: 12px; padding: 14px; text-decoration: none; }
.ci-thumb { width: 56px; height: 42px; border-radius: var(--r); overflow: hidden; flex-shrink: 0; background: var(--bg3); display: flex; align-items: center; justify-content: center; }
.ci-thumb img { width: 100%; height: 100%; object-fit: cover; }
.ci-thumb-placeholder { font-size: 22px; }
.ci-info { flex: 1; min-width: 0; }
.ci-title { font-size: 13px; font-weight: 600; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ci-prog  { font-size: 11px; color: var(--text3); margin-top: 4px; }

.usage-row { display: flex; align-items: center; gap: 10px; font-size: 13px; color: var(--text2); }
.usage-bar-wrap { flex: 1; }
.usage-count { font-size: 12px; font-weight: 600; color: var(--text3); white-space: nowrap; }

.qa-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.qa-btn {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  padding: 16px 10px; border-radius: var(--r);
  background: var(--bg3); border: 1px solid var(--border);
  text-decoration: none; color: var(--text2);
  font-size: 12px; font-weight: 600;
  transition: all var(--t);
}
.qa-btn:hover { border-color: var(--p); color: var(--p); background: var(--p-soft); }
.qa-icon { font-size: 22px; }

.badges-row { display: flex; flex-wrap: wrap; gap: 12px; }
.badge-card { padding: 14px 18px; text-align: center; cursor: default; }
.badge-icon { font-size: 28px; margin-bottom: 4px; }
.badge-name { font-size: 11px; font-weight: 600; color: var(--text2); }
.leaderboard-mini { display: flex; flex-direction: column; gap: 10px; }
.lb-mini-row { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border); }
.lb-mini-row:last-child { border-bottom: 0; padding-bottom: 0; }
.lb-mini-row.me { background: var(--p-soft); margin: 0 -12px; padding: 10px 12px; border-radius: var(--r); border-bottom: 0; }
.lb-mini-rank { width: 28px; height: 28px; border-radius: 50%; background: var(--bg3); display: flex; align-items: center; justify-content: center; font-weight: 800; color: var(--p); }
.lb-mini-info { flex: 1; min-width: 0; }
.lb-mini-name { font-size: 13px; font-weight: 700; color: var(--text); }
.lb-mini-name span { color: var(--p); }
.lb-mini-meta { font-size: 11px; color: var(--text3); margin-top: 2px; }
.lb-mini-xp { font-size: 12px; font-weight: 800; color: var(--amber); white-space: nowrap; }

@media (max-width: 1024px) { .dash-grid { grid-template-columns: 1fr; } }
@media (max-width: 768px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .welcome-banner { flex-direction: column; text-align: center; }
  .wb-robot { display: none; }
  .wb-actions { justify-content: center; }
}
</style>
