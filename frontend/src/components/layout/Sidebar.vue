<template>
  <aside class="sidebar" :class="{ collapsed: !open, open: open && isMobile }">
    <!-- Logo -->
    <div class="sidebar-logo">
      <div class="logo-icon">🤖</div>
      <span class="logo-text">Amy<span class="logo-accent">Learn</span></span>
      <span class="logo-version">v3</span>
    </div>

    <!-- Nav -->
    <nav class="sidebar-nav">

      <div class="nav-section">
        <span class="nav-label">Main</span>
        <router-link to="/dashboard"     class="nav-item"><span class="ni">🏠</span><span>Dashboard</span></router-link>
        <router-link to="/amy"           class="nav-item amy-nav"><span class="ni">🤖</span><span>Amy AI Tutor</span><span class="badge-new">AI</span></router-link>
        <router-link to="/quiz"          class="nav-item"><span class="ni">🧠</span><span>Quiz</span></router-link>
        <router-link to="/courses"       class="nav-item"><span class="ni">📚</span><span>Courses</span></router-link>
        <router-link to="/my-courses"    class="nav-item"><span class="ni">🎯</span><span>My Courses</span></router-link>
        <router-link to="/learning-path" class="nav-item"><span class="ni">🗺️</span><span>Learning Path</span><span class="badge-new">AI</span></router-link>
      </div>

      <div class="nav-section">
        <span class="nav-label">Game Learning</span>
        <router-link to="/game"              class="nav-item"><span class="ni">🎮</span><span>Game Learning</span><span class="badge-new">BETA</span></router-link>
        <router-link to="/game/leaderboard"  class="nav-item"><span class="ni">🏆</span><span>Game Leaderboard</span></router-link>
        <router-link to="/game/weak-areas"   class="nav-item"><span class="ni">💪</span><span>Weak Areas</span></router-link>
      </div>

      <div class="nav-section">
        <span class="nav-label">Practice</span>
        <router-link to="/placement-test"   class="nav-item"><span class="ni">🧪</span><span>Placement Test</span></router-link>
        <router-link to="/mini-games"        class="nav-item"><span class="ni">🎮</span><span>Mini Games</span></router-link>
        <router-link to="/daily-challenge"   class="nav-item"><span class="ni">⚡</span><span>Daily Challenge</span></router-link>
        <router-link to="/pronunciation"     class="nav-item"><span class="ni">🎙️</span><span>Pronunciation</span></router-link>
        <router-link to="/essay-checker"     class="nav-item"><span class="ni">📝</span><span>Essay Checker</span></router-link>
        <router-link to="/coding-interview"  class="nav-item"><span class="ni">👨‍💻</span><span>Coding Interview</span></router-link>
      </div>

      <div class="nav-section">
        <span class="nav-label">Learn</span>
        <router-link to="/industry-english"  class="nav-item"><span class="ni">💼</span><span>Industry English</span></router-link>
        <router-link to="/news-learning"     class="nav-item"><span class="ni">📰</span><span>News Learning</span></router-link>
        <router-link to="/song-learning"     class="nav-item"><span class="ni">🎵</span><span>Song Learning</span></router-link>
        <router-link to="/cultural"          class="nav-item"><span class="ni">🌐</span><span>Cultural Context</span></router-link>
        <router-link to="/accent-training"   class="nav-item"><span class="ni">🌍</span><span>Accent Training</span></router-link>
        <router-link to="/sleep-learning"    class="nav-item"><span class="ni">🌙</span><span>Sleep Learning</span></router-link>
      </div>

      <div class="nav-section">
        <span class="nav-label">Progress</span>
        <router-link to="/fluency"           class="nav-item"><span class="ni">📊</span><span>Fluency Score</span></router-link>
        <router-link to="/mistake-journal"   class="nav-item"><span class="ni">🔁</span><span>Mistake Journal</span></router-link>
        <router-link to="/goals"             class="nav-item"><span class="ni">🏁</span><span>Goal Tracking</span></router-link>
        <router-link to="/vocabulary"        class="nav-item"><span class="ni">📖</span><span>Vocabulary</span></router-link>
        <router-link to="/learning-style"    class="nav-item"><span class="ni">🧬</span><span>Learning Style</span></router-link>
        <router-link to="/amy-memory"        class="nav-item"><span class="ni">💭</span><span>Amy Memory</span></router-link>
      </div>

      <div class="nav-section">
        <span class="nav-label">Compete</span>
        <router-link to="/tournament"        class="nav-item"><span class="ni">🏆</span><span>Tournament</span></router-link>
        <router-link to="/micro-certs"       class="nav-item"><span class="ni">📜</span><span>Micro Certs</span></router-link>
        <router-link to="/leaderboard"       class="nav-item"><span class="ni">📈</span><span>Leaderboard</span></router-link>
      </div>

      <div class="nav-section">
        <span class="nav-label">Account</span>
        <router-link to="/profile"           class="nav-item"><span class="ni">👤</span><span>Profile</span></router-link>
        <router-link to="/certificates"      class="nav-item"><span class="ni">🎓</span><span>Certificates</span></router-link>
        <router-link to="/reminders"         class="nav-item"><span class="ni">📅</span><span>Reminders</span></router-link>
        <router-link to="/payments"          class="nav-item"><span class="ni">💳</span><span>Payments</span></router-link>
        <router-link to="/notifications"     class="nav-item">
          <span class="ni">🔔</span><span>Notifications</span>
          <span v-if="unreadCount > 0" class="badge-count">{{ unreadCount > 9 ? '9+' : unreadCount }}</span>
        </router-link>
      </div>

      <div class="nav-section" v-if="auth.isLoggedIn && auth.isAdmin">
        <span class="nav-label">Admin</span>
        <router-link to="/admin"                  class="nav-item"><span class="ni">⚡</span><span>Dashboard</span></router-link>
        <router-link to="/admin/users"            class="nav-item"><span class="ni">👥</span><span>Users</span></router-link>
        <router-link to="/admin/courses"          class="nav-item"><span class="ni">📖</span><span>Courses</span></router-link>
        <router-link to="/admin/categories"       class="nav-item"><span class="ni">🏷️</span><span>Categories</span></router-link>
        <router-link to="/admin/payments"         class="nav-item"><span class="ni">💰</span><span>Payments</span></router-link>
        <router-link to="/admin/coupons"          class="nav-item"><span class="ni">🎫</span><span>Coupons</span></router-link>
        <router-link to="/admin/badges"           class="nav-item"><span class="ni">🏅</span><span>Badges</span></router-link>
      </div>

      <div class="nav-section" v-if="auth.isLoggedIn && auth.isAdmin">
        <span class="nav-label">Admin - Game System</span>
        <router-link to="/admin/game"              class="nav-item"><span class="ni">🎮</span><span>Game Dashboard</span></router-link>
        <router-link to="/admin/game/subjects"     class="nav-item"><span class="ni">📚</span><span>Manage Subjects</span></router-link>
        <router-link to="/admin/game/topics"       class="nav-item"><span class="ni">📖</span><span>Manage Topics</span></router-link>
        <router-link to="/admin/game/levels"       class="nav-item"><span class="ni">🎯</span><span>Manage Levels</span></router-link>
        <router-link to="/admin/game/questions"    class="nav-item"><span class="ni">❓</span><span>Manage Questions</span></router-link>
      </div>

      <!-- DEBUG: Show user role -->
      <div v-if="auth.user" class="nav-section" style="background: #f0f0f0; opacity: 0.7; font-size: 11px;">
        <span class="nav-label">DEBUG</span>
        <p style="padding: 8px; margin: 0; color: #666;">Role: {{ auth.user?.role || 'none' }}</p>
        <p style="padding: 8px; margin: 0; color: #666;">isAdmin: {{ auth.isAdmin }}</p>
        <p style="padding: 8px; margin: 0; color: #666;">isLoggedIn: {{ auth.isLoggedIn }}</p>
      </div>

    </nav>

    <!-- User -->
    <div class="sidebar-user">
      <div class="avatar avatar-sm">
        <img v-if="auth.user?.avatar" :src="auth.user.avatar" alt="avatar" style="width:100%;height:100%;border-radius:50%;object-fit:cover" />
        <span v-else>{{ initials }}</span>
      </div>
      <div class="user-info">
        <div class="user-name">{{ auth.user?.name }}</div>
        <div class="user-plan">{{ (auth.user?.subscription_plan || 'free').toUpperCase() }}</div>
      </div>
      <button class="logout-btn" @click="auth.logout()" title="Logout">↪</button>
    </div>

    <button class="mobile-close" @click="open = false">✕</button>
  </aside>

  <div class="sidebar-overlay" v-if="open && isMobile" @click="open = false"></div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import api from '@/api'

const auth        = useAuthStore()
const open        = ref(window.innerWidth > 768)
const isMobile    = ref(window.innerWidth <= 768)
const unreadCount = ref(0)

const initials = computed(() => {
  const name = auth.user?.name || ''
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
})

const handleResize = () => {
  isMobile.value = window.innerWidth <= 768
  if (isMobile.value) open.value = false
  else open.value = true
}

onMounted(async () => {
  window.addEventListener('resize', handleResize)
  if (auth.isLoggedIn) {
    try {
      const r = await api.get('/users/notifications')
      unreadCount.value = r.data.filter(n => !n.is_read).length
    } catch {}
  }
})
onUnmounted(() => window.removeEventListener('resize', handleResize))
</script>
