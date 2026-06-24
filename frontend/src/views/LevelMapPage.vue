<template>
  <div class="level-map-page">
    <!-- Header with topic name -->
    <header class="map-header">
      <button @click="goBack" class="btn-back">← Back</button>
      <div class="topic-info">
        <h1>{{ topic.name }}</h1>
        <p v-if="topic.description" class="description">{{ topic.description }}</p>
      </div>
    </header>

    <!-- Progress Bar -->
    <div v-if="progress.length > 0" class="progress-section">
      <div class="progress-label">
        <span>Topic Mastery: {{ mastery }}%</span>
        <span>{{ completedLevels }} / {{ levels.length }} Levels</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: mastery + '%' }"></div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Loading levels...</p>
    </div>

    <!-- Levels Grid -->
    <div v-else class="levels-container">
      <!-- Regular Levels -->
      <div class="levels-grid">
        <div
          v-for="(level, index) in regularLevels"
          :key="level.id"
          class="level-card"
          :class="[
            `difficulty-${level.difficulty}`,
            `state-${level.state}`,
            { locked: level.is_locked }
          ]"
          @click="selectLevel(level)"
        >
          <div class="level-number">{{ index + 1 }}</div>
          <div class="level-content">
            <h3>{{ level.title }}</h3>
            <div class="level-meta">
              <span class="difficulty">{{ level.difficulty }}</span>
              <span class="xp">{{ level.xp_reward }} XP</span>
            </div>
          </div>
          <div class="level-status">
            <span v-if="level.state === 'completed'" class="badge completed">✓ DONE</span>
            <span v-else-if="level.state === 'in_progress'" class="badge in-progress">→ IN PROGRESS</span>
            <span v-else-if="level.is_locked" class="badge locked">🔒 LOCKED</span>
            <span v-else class="badge unlocked">🎮 READY</span>
          </div>
          <div v-if="level.state === 'completed'" class="stars">
            <span v-for="i in level.stars" :key="i">⭐</span>
          </div>
        </div>
      </div>

      <!-- Boss Levels -->
      <div v-if="bossLevels.length > 0" class="boss-section">
        <h2>🔥 Boss Levels</h2>
        <div class="boss-grid">
          <div
            v-for="level in bossLevels"
            :key="level.id"
            class="boss-card"
            :class="{ locked: level.is_locked }"
            @click="selectLevel(level)"
          >
            <div class="boss-badge">BOSS</div>
            <div class="boss-icon">👹</div>
            <h3>{{ level.title }}</h3>
            <p class="boss-description">{{ level.difficulty }} Challenge</p>
            <div class="boss-reward">{{ level.xp_reward * 2 }} XP</div>
            <div class="boss-status">
              <span v-if="level.state === 'completed'" class="status completed">✓ DEFEATED</span>
              <span v-else-if="level.is_locked" class="status locked">🔒 LOCKED</span>
              <span v-else class="status ready">⚔️ READY TO FIGHT</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Level Details Modal -->
    <div v-if="selectedLevel && !loading" class="level-modal-overlay" @click="closeModal">
      <div class="level-modal" @click.stop>
        <button @click="closeModal" class="modal-close">✕</button>
        <h2>{{ selectedLevel.title }}</h2>
        <p>{{ selectedLevel.difficulty }} Difficulty</p>

        <div class="level-details">
          <div class="detail">
            <span class="label">Questions:</span>
            <span class="value">{{ selectedLevel.question_count }}</span>
          </div>
          <div class="detail">
            <span class="label">Time Limit:</span>
            <span class="value">{{ Math.floor(selectedLevel.time_limit / 60) }} minutes</span>
          </div>
          <div class="detail">
            <span class="label">Pass Score:</span>
            <span class="value">{{ selectedLevel.pass_score }}%</span>
          </div>
          <div class="detail">
            <span class="label">Reward:</span>
            <span class="value">{{ selectedLevel.xp_reward }} XP</span>
          </div>
          <div v-if="selectedLevel.best_score > 0" class="detail">
            <span class="label">Your Best:</span>
            <span class="value">{{ selectedLevel.best_score }}%</span>
          </div>
        </div>

        <div class="modal-actions">
          <button @click="closeModal" class="btn btn-secondary">Cancel</button>
          <button
            @click="playLevel(selectedLevel)"
            :disabled="selectedLevel.is_locked"
            class="btn btn-primary"
          >
            {{ selectedLevel.is_locked ? '🔒 Locked' : '▶ Play Level' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useGameStore } from '@/store/game_store'

const router = useRouter()
const route = useRoute()
const gameStore = useGameStore()

const topicId = ref(null)
const topic = ref({})
const levels = ref([])
const loading = ref(false)
const selectedLevel = ref(null)
const mastery = ref(0)
const completedLevels = ref(0)

const regularLevels = computed(() => levels.value.filter(l => l.level_type !== 'boss'))
const bossLevels = computed(() => levels.value.filter(l => l.level_type === 'boss'))
const progress = computed(() => levels.value.filter(l => l.state === 'completed'))

function goBack() {
  router.back()
}

async function loadLevels() {
  try {
    loading.value = true
    const data = await gameStore.fetchLevels(topicId.value)
    levels.value = data || []
    completedLevels.value = levels.value.filter(l => l.state === 'completed').length
    mastery.value = levels.value.length > 0 ? Math.round((completedLevels.value / levels.value.length) * 100) : 0
  } catch (error) {
    console.error('Error loading levels:', error)
  } finally {
    loading.value = false
  }
}

function selectLevel(level) {
  selectedLevel.value = level
}

function closeModal() {
  selectedLevel.value = null
}

async function playLevel(level) {
  if (level.is_locked) return
  try {
    loading.value = true
    await gameStore.startLevel(level.id)
    router.push(`/game/play/${level.id}`)
  } catch (error) {
    console.error('Error starting level:', error)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  topicId.value = route.params.topicId
  topic.value = route.params.topic || { name: 'Topic' }
  await loadLevels()
})
</script>

<style scoped lang="scss">
.level-map-page {
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.map-header {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 30px;
  background: rgba(255, 255, 255, 0.95);
  padding: 20px;
  border-radius: 12px;

  .btn-back {
    background: none;
    border: none;
    font-size: 18px;
    cursor: pointer;
    padding: 5px 10px;
    border-radius: 6px;
    transition: 0.2s;

    &:hover {
      background: rgba(0, 0, 0, 0.1);
    }
  }

  .topic-info {
    flex: 1;

    h1 {
      margin: 0;
      color: #333;
      font-size: 24px;
    }

    .description {
      margin: 8px 0 0 0;
      color: #666;
      font-size: 14px;
    }
  }
}

.progress-section {
  background: rgba(255, 255, 255, 0.95);
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 30px;

  .progress-label {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
    font-size: 14px;
    color: #666;
    font-weight: 600;
  }

  .progress-bar {
    height: 8px;
    background: rgba(0, 0, 0, 0.1);
    border-radius: 4px;
    overflow: hidden;

    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, #667eea, #764ba2);
      transition: width 0.3s ease;
    }
  }
}

.levels-container {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.levels-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.level-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  border: 2px solid transparent;

  &.state-completed {
    border-color: #4caf50;
    background: rgba(76, 175, 80, 0.1);
  }

  &.state-in_progress {
    border-color: #ff9800;
    background: rgba(255, 152, 0, 0.1);
  }

  &.locked {
    opacity: 0.6;
    cursor: not-allowed;
  }

  &:not(.locked):hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 20px rgba(0, 0, 0, 0.2);
  }

  .level-number {
    position: absolute;
    top: 10px;
    right: 10px;
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: bold;
    font-size: 14px;
  }

  .level-content {
    margin-bottom: 15px;

    h3 {
      margin: 0 0 8px 0;
      color: #333;
      font-size: 16px;
    }

    .level-meta {
      display: flex;
      gap: 10px;
      font-size: 12px;

      .difficulty {
        padding: 4px 8px;
        background: rgba(0, 0, 0, 0.1);
        border-radius: 4px;
        color: #666;
      }

      .xp {
        color: #667eea;
        font-weight: 600;
      }
    }
  }

  .level-status {
    margin-bottom: 10px;

    .badge {
      display: inline-block;
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;

      &.completed {
        background: #4caf50;
        color: white;
      }

      &.in-progress {
        background: #ff9800;
        color: white;
      }

      &.locked {
        background: #f44336;
        color: white;
      }

      &.unlocked {
        background: #2196f3;
        color: white;
      }
    }
  }

  .stars {
    display: flex;
    gap: 4px;
    font-size: 16px;
  }
}

.boss-section {
  margin-top: 40px;

  h2 {
    color: white;
    margin-bottom: 20px;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  }

  .boss-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 20px;
  }

  .boss-card {
    background: rgba(244, 67, 54, 0.1);
    border: 2px solid #f44336;
    border-radius: 15px;
    padding: 30px 20px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;

    &:hover:not(.locked) {
      transform: scale(1.05);
      background: rgba(244, 67, 54, 0.2);
      box-shadow: 0 15px 30px rgba(244, 67, 54, 0.3);
    }

    &.locked {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .boss-badge {
      position: absolute;
      top: -10px;
      left: 50%;
      transform: translateX(-50%);
      background: #f44336;
      color: white;
      padding: 5px 15px;
      border-radius: 20px;
      font-weight: bold;
      font-size: 12px;
    }

    .boss-icon {
      font-size: 48px;
      margin: 20px 0;
    }

    h3 {
      color: #f44336;
      margin: 0 0 8px 0;
    }

    .boss-description {
      color: #666;
      font-size: 14px;
      margin: 0 0 15px 0;
    }

    .boss-reward {
      background: rgba(255, 152, 0, 0.2);
      color: #ff9800;
      padding: 10px;
      border-radius: 8px;
      font-weight: bold;
      margin-bottom: 15px;
      font-size: 14px;
    }

    .boss-status {
      .status {
        display: block;
        font-weight: 600;
        padding: 8px;
        border-radius: 6px;

        &.completed {
          background: #4caf50;
          color: white;
        }

        &.locked {
          background: #f44336;
          color: white;
        }

        &.ready {
          background: #ff9800;
          color: white;
        }
      }
    }
  }
}

.level-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;

  .level-modal {
    background: white;
    border-radius: 16px;
    padding: 40px;
    max-width: 500px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
    position: relative;

    .modal-close {
      position: absolute;
      top: 15px;
      right: 15px;
      background: none;
      border: none;
      font-size: 24px;
      cursor: pointer;
      color: #999;

      &:hover {
        color: #333;
      }
    }

    h2 {
      margin: 0 0 10px 0;
      color: #333;
    }

    > p {
      margin: 0 0 20px 0;
      color: #666;
    }

    .level-details {
      background: #f5f5f5;
      border-radius: 12px;
      padding: 20px;
      margin: 20px 0;
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 15px;

      .detail {
        display: flex;
        flex-direction: column;
        gap: 5px;

        .label {
          font-size: 12px;
          color: #999;
          text-transform: uppercase;
        }

        .value {
          font-size: 16px;
          font-weight: 600;
          color: #333;
        }
      }
    }

    .modal-actions {
      display: flex;
      gap: 15px;
      margin-top: 20px;
    }
  }
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 20px;

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
  .level-map-page {
    padding: 15px;
  }

  .map-header {
    flex-direction: column;
    gap: 15px;
  }

  .levels-grid {
    grid-template-columns: 1fr;
  }

  .boss-grid {
    grid-template-columns: 1fr;
  }

  .level-modal-overlay {
    .level-modal {
      padding: 25px;
      width: 95%;
    }
  }
}
</style>
