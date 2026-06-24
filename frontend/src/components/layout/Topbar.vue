<template>
  <header class="topbar">
    <div class="topbar-left">
      <button class="menu-btn" @click="$emit('toggle-sidebar')">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
          <rect x="0" y="3" width="18" height="2" rx="1" fill="currentColor"/>
          <rect x="0" y="8" width="12" height="2" rx="1" fill="currentColor"/>
          <rect x="0" y="13" width="18" height="2" rx="1" fill="currentColor"/>
        </svg>
      </button>
      <div class="page-title">{{ pageTitle }}</div>
    </div>
    <div class="topbar-right">
      <div class="xp-chip" v-if="auth.user">
        <span>⭐</span><span>{{ auth.user.xp_points?.toLocaleString() }} XP</span>
      </div>
      <div class="streak-chip" v-if="auth.user?.streak_days > 0">
        <span>🔥</span><span>{{ auth.user.streak_days }}d</span>
      </div>
      <button class="icon-btn theme-btn" @click="theme.toggle()" :title="theme.isDark ? 'Light mode' : 'Dark mode'">
        <span v-if="theme.isDark">☀️</span>
        <span v-else>🌙</span>
      </button>
      <router-link to="/notifications" class="icon-btn notif-btn">
        <span>🔔</span>
        <span class="notif-dot" v-if="unreadCount > 0">{{ unreadCount > 9 ? '9+' : unreadCount }}</span>
      </router-link>
      <router-link to="/profile" class="avatar-btn">
        <div class="avatar avatar-sm">
          <img v-if="auth.user?.avatar" :src="auth.user.avatar" alt="avatar" style="width:100%;height:100%;border-radius:50%;object-fit:cover" />
          <span v-else>{{ initials }}</span>
        </div>
      </router-link>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useThemeStore } from '@/store/theme'
import api from '@/api'

defineEmits(['toggle-sidebar'])

const auth  = useAuthStore()
const theme = useThemeStore()
const route = useRoute()
const unreadCount = ref(0)

const initials = computed(() => {
  const name = auth.user?.name || ''
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0,2)
})

const PAGE_TITLES = {
  'Home': '🏠 Home', 'Dashboard': '🏠 Dashboard', 'Amy': '🤖 Amy AI Tutor',
  'Quiz': '🧠 Quiz Generator', 'QuizTake': '🧠 Take Quiz',
  'Courses': '📚 Courses', 'CourseDetail': '📚 Course',
  'MyCourses': '🎯 My Courses', 'Lesson': '📖 Lesson',
  'Profile': '👤 My Profile', 'Leaderboard': '🏆 Leaderboard',
  'Certificates': '🎓 Certificates', 'Payments': '💳 Payments',
  'Notifications': '🔔 Notifications', 'Pricing': '💎 Pricing',
  'LearningPath': '🗺️ Learning Path', 'PlacementTest': '🧪 Placement Test',
  'MiniGames': '🎮 Mini Games', 'DailyChallenge': '⚡ Daily Challenge',
  'Pronunciation': '🎙️ Pronunciation', 'EssayChecker': '📝 Essay Checker',
  'CodingInterview': '👨‍💻 Coding Interview', 'IndustryEnglish': '💼 Industry English',
  'NewsLearning': '📰 News Learning', 'SongLearning': '🎵 Song Learning',
  'CulturalContext': '🌐 Cultural Context', 'AccentTraining': '🌍 Accent Training',
  'SleepLearning': '🌙 Sleep Learning', 'Fluency': '📊 Fluency Score',
  'MistakeJournal': '🔁 Mistake Journal', 'Goals': '🎯 Goal Tracking',
  'Vocabulary': '📖 Vocabulary', 'LearningStyle': '🧬 Learning Style',
  'AmyMemory': '🤖 Amy Memory', 'Tournament': '🏆 Tournament',
  'MicroCerts': '📜 Micro Certificates', 'Reminders': '📅 Reminders',
  'Cultural': '🌐 Cultural Context',
  'AdminDash': '⚡ Admin Dashboard', 'AdminUsers': '👥 User Management',
  'AdminCourses': '📖 Course Management', 'AdminLessons': '📝 Lessons',
  'AdminCategories': '🏷️ Categories', 'AdminPayments': '💰 Payments',
  'AdminCoupons': '🎫 Coupons', 'AdminBadges': '🏅 Badges',
}

const pageTitle = computed(() => PAGE_TITLES[route.name] || 'Amy Learning')

onMounted(async () => {
  try {
    const res = await api.get('/users/notifications')
    unreadCount.value = res.data.filter(n => !n.is_read).length
  } catch {}
})
</script>
