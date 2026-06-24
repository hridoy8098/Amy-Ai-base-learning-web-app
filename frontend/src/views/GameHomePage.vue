<template>
  <div class="game-home-page">
    <!-- Header -->
    <div class="header">
      <div class="header-content">
        <h1>🎮 Game Learning</h1>
        <div class="user-stats">
          <div class="stat">
            <span class="label">Total XP</span>
            <span class="value">{{ formatNumber(gamification.totalXP) }}</span>
          </div>
          <div class="stat">
            <span class="label">Tier</span>
            <span class="value">{{ gamification.tierDisplay }}</span>
          </div>
          <div class="stat">
            <span class="label">🔥 Streak</span>
            <span class="value">{{ gamification.currentStreak }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loadingSubjects" class="loading">
      <div class="spinner"></div>
      <p>Loading subjects...</p>
    </div>

    <!-- Subjects Grid -->
    <div v-else class="subjects-grid">
      <div
        v-for="subject in subjects"
        :key="subject.id"
        :style="{ backgroundColor: subject.color }"
        class="subject-card"
        @click="selectSubject(subject)"
      >
        <div class="subject-header">
          <span class="icon">{{ subject.icon }}</span>
          <h2>{{ subject.name }}</h2>
        </div>
        <div class="subject-stats">
          <p class="description">{{ subject.description }}</p>
          <div class="progress-info">
            <span>📚 {{ subject.topic_count }} topics</span>
            <span>{{ subject.xp_earned }} XP</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Weak Areas Alert -->
    <div v-if="weakAreasCount > 0" class="weak-areas-alert">
      <h3>⚠️ Practice These Topics</h3>
      <p>You have {{ weakAreasCount }} weak areas. Practice to improve!</p>
      <button @click="goToWeakAreas" class="btn btn-secondary">Practice Weak Areas</button>
    </div>

    <!-- Leaderboard Preview -->
    <div v-if="topPlayers.length > 0" class="leaderboard-preview">
      <h3>🏆 Top Players (Weekly)</h3>
      <div class="mini-leaderboard">
        <div v-for="(player, index) in topPlayers.slice(0, 3)" :key="player.rank" class="player-card">
          <span class="medal">{{ getMedal(index) }}</span>
          <span class="name">{{ player.player }}</span>
          <span class="xp">{{ formatNumber(player.xp) }} XP</span>
        </div>
      </div>
      <router-link to="/game/leaderboard" class="link">View Full Leaderboard →</router-link>
    </div>

    <!-- Quick Stats -->
    <div class="quick-stats">
      <h3>Your Progress</h3>
      <div class="stats-grid">
        <div class="stat-item">
          <span class="stat-icon">❤️</span>
          <span class="stat-text">{{ gamification.currentHearts }} / {{ gamification.maxHearts }} Hearts</span>
        </div>
        <div class="stat-item">
          <span class="stat-icon">⭐</span>
          <span class="stat-text">{{ starCount }} Stars Earned</span>
        </div>
        <div class="stat-item">
          <span class="stat-icon">🎯</span>
          <span class="stat-text">{{ levelsCompleted }} Levels Complete</span>
        </div>
        <div class="stat-item">
          <span class="stat-icon">🔥</span>
          <span class="stat-text">{{ gamification.currentStreak }} Day Streak</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '@/store/game_store'
import { useGamificationStore } from '@/store/gamification_store'

const router = useRouter()
const gameStore = useGameStore()
const gamificationStore = useGamificationStore()

const topPlayers = ref([])
const starCount = ref(0)
const levelsCompleted = ref(0)

const subjects = computed(() => gameStore.subjects)
const loadingSubjects = computed(() => gameStore.loadingSubjects)
const error = computed(() => gameStore.error)
const gamification = gamificationStore
const weakAreasCount = computed(() => gamificationStore.weakAreasCount)

function getMedal(index) {
  const medals = ['🥇', '🥈', '🥉']
  return medals[index] || ''
}

function formatNumber(value) {
  if (value == null) return '0'
  return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

async function selectSubject(subject) {
  gameStore.setCurrentSubject(subject)
  await router.push(`/game/subject/${subject.id}`)
}

function goToWeakAreas() {
  router.push('/game/weak-areas')
}

async function fetchLeaderboard() {
  try {
    const data = await gameStore.fetchLeaderboard('weekly', 10)
    topPlayers.value = data.leaderboard || []
  } catch (error) {
    console.error('Error fetching leaderboard:', error)
  }
}

async function loadData() {
  await gameStore.fetchSubjects()
  await gamificationStore.fetchUserProgress()
  await gamificationStore.fetchWeakAreas()
  await fetchLeaderboard()
}

onMounted(loadData)
</script>

<style scoped lang="scss">
.game-home-page {
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.header {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);

  h1 {
    margin: 0 0 15px 0;
    color: #333;
    font-size: 28px;
  }
}

.user-stats {
  display: flex;
  gap: 30px;
  flex-wrap: wrap;

  .stat {
    display: flex;
    flex-direction: column;
    gap: 5px;

    .label {
      font-size: 12px;
      color: #999;
      text-transform: uppercase;
    }

    .value {
      font-size: 20px;
      font-weight: bold;
      color: #667eea;
    }
  }
}

.subjects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.subject-card {
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: white;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);

  &:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.2);
  }

  .subject-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 15px;

    .icon {
      font-size: 32px;
    }

    h2 {
      margin: 0;
      font-size: 20px;
    }
  }

  .subject-stats {
    .description {
      margin: 0 0 10px 0;
      opacity: 0.9;
      font-size: 14px;
    }

    .progress-info {
      display: flex;
      justify-content: space-between;
      font-size: 13px;
      opacity: 0.85;
    }
  }
}

.weak-areas-alert {
  background: rgba(255, 193, 7, 0.1);
  border: 2px solid #ffc107;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  color: #fff;

  h3 {
    margin: 0 0 10px 0;
  }

  p {
    margin: 0 0 15px 0;
  }
}

.leaderboard-preview {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;

  h3 {
    margin: 0 0 15px 0;
    color: #333;
  }

  .mini-leaderboard {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 15px;
  }

  .player-card {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 10px;
    background: #f5f5f5;
    border-radius: 8px;

    .medal {
      font-size: 20px;
      min-width: 30px;
    }

    .name {
      flex: 1;
      color: #333;
      font-weight: 500;
    }

    .xp {
      color: #667eea;
      font-weight: bold;
    }
  }

  .link {
    color: #667eea;
    text-decoration: none;
    font-weight: 600;

    &:hover {
      text-decoration: underline;
    }
  }
}

.quick-stats {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 20px;

  h3 {
    margin: 0 0 15px 0;
    color: #333;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 15px;
  }

  .stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 15px;
    background: #f5f5f5;
    border-radius: 8px;
    gap: 10px;

    .stat-icon {
      font-size: 24px;
    }

    .stat-text {
      text-align: center;
      color: #333;
      font-size: 13px;
      font-weight: 600;
    }
  }
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;

  .spinner {
    width: 50px;
    height: 50px;
    border: 4px solid rgba(255, 255, 255, 0.3);
    border-top: 4px solid white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  p {
    margin-top: 20px;
    color: white;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .subjects-grid {
    grid-template-columns: 1fr;
  }

  .header {
    h1 {
      font-size: 22px;
    }
  }

  .user-stats {
    gap: 15px;
  }
}
</style>
