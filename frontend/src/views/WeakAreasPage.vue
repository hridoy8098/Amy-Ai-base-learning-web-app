<template>
  <div class="weak-areas-page">
    <!-- Header -->
    <header class="header">
      <button @click="goBack" class="btn-back">← Back</button>
      <h1>⚠️ Practice Weak Areas</h1>
      <p class="subtitle">Master these topics to improve your overall performance</p>
    </header>

    <!-- Loading State -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Loading weak areas...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="weakAreas.length === 0" class="empty-state">
      <div class="empty-icon">🎯</div>
      <h2>No Weak Areas Found!</h2>
      <p>You're doing great! Keep practicing to maintain your performance.</p>
      <button @click="goBack" class="btn btn-primary">Continue Learning</button>
    </div>

    <!-- Weak Areas List -->
    <div v-else class="weak-areas-list">
      <div class="stats-header">
        <div class="stat">
          <span class="label">Weak Areas</span>
          <span class="value">{{ weakAreas.length }}</span>
        </div>
        <div class="stat">
          <span class="label">Avg Accuracy</span>
          <span class="value">{{ avgAccuracy }}%</span>
        </div>
        <div class="stat">
          <span class="label">Priority</span>
          <span class="value">{{ priorityLevel }}</span>
        </div>
      </div>

      <div class="areas-grid">
        <div
          v-for="(area, index) in weakAreas"
          :key="area.id"
          class="area-card"
          :class="`priority-${area.priority}`"
          @click="selectArea(area)"
        >
          <div class="area-header">
            <h3>{{ area.topic_name }}</h3>
            <span class="priority-badge">{{ area.priority }}</span>
          </div>

          <div class="area-details">
            <div class="detail">
              <span class="label">Last Attempted</span>
              <span class="value">{{ formatDate(area.last_attempted) }}</span>
            </div>
            <div class="detail">
              <span class="label">Accuracy</span>
              <span class="value">{{ area.accuracy }}%</span>
            </div>
            <div class="detail">
              <span class="label">Attempts</span>
              <span class="value">{{ area.attempts }}</span>
            </div>
          </div>

          <div class="accuracy-bar">
            <div
              class="accuracy-fill"
              :style="{ 
                width: area.accuracy + '%',
                backgroundColor: getAccuracyColor(area.accuracy)
              }"
            ></div>
          </div>

          <button class="btn-practice">🎮 Practice Now →</button>
        </div>
      </div>
    </div>

    <!-- Area Details Modal -->
    <div v-if="selectedArea && !loading" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <button @click="closeModal" class="modal-close">✕</button>
        
        <h2>{{ selectedArea.topic_name }}</h2>
        <p class="subject">Subject: {{ selectedArea.subject_name }}</p>

        <div class="stats-grid">
          <div class="stat">
            <span class="label">Accuracy</span>
            <span class="value">{{ selectedArea.accuracy }}%</span>
          </div>
          <div class="stat">
            <span class="label">Attempts</span>
            <span class="value">{{ selectedArea.attempts }}</span>
          </div>
          <div class="stat">
            <span class="label">Correct</span>
            <span class="value">{{ selectedArea.correct_answers }} / {{ selectedArea.total_questions }}</span>
          </div>
          <div class="stat">
            <span class="label">Priority</span>
            <span class="value">{{ selectedArea.priority }}</span>
          </div>
        </div>

        <div class="recommendations">
          <h3>📝 Recommendations</h3>
          <ul>
            <li>Review the concept explanations for this topic</li>
            <li>Practice with easier difficulty levels first</li>
            <li>Focus on question types you find challenging</li>
            <li>Take breaks between practice sessions</li>
          </ul>
        </div>

        <div class="modal-actions">
          <button @click="closeModal" class="btn btn-secondary">Cancel</button>
          <button @click="practiceTopic(selectedArea)" class="btn btn-primary">
            🎮 Start Practice Session
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useGamificationStore } from '@/store/gamification_store'

export default {
  name: 'WeakAreasPage',
  setup() {
    const gamificationStore = useGamificationStore()
    return { gamificationStore }
  },
  data() {
    return {
      weakAreas: [],
      loading: false,
      selectedArea: null
    }
  },
  computed: {
    avgAccuracy() {
      if (this.weakAreas.length === 0) return 0
      const sum = this.weakAreas.reduce((acc, area) => acc + area.accuracy, 0)
      return Math.round(sum / this.weakAreas.length)
    },
    priorityLevel() {
      const count = this.weakAreas.length
      if (count <= 2) return 'Low'
      if (count <= 5) return 'Medium'
      return 'High'
    }
  },
  methods: {
    async loadWeakAreas() {
      try {
        this.loading = true
        await this.gamificationStore.fetchWeakAreas()
        this.weakAreas = this.gamificationStore.weakAreas
      } catch (error) {
        console.error('Error loading weak areas:', error)
      } finally {
        this.loading = false
      }
    },

    selectArea(area) {
      this.selectedArea = area
    },

    closeModal() {
      this.selectedArea = null
    },

    async practiceTopic(area) {
      // Navigate to level map for this topic
      this.$router.push(`/game/topic/${area.topic_id}`)
    },

    formatDate(date) {
      if (!date) return 'Never'
      const d = new Date(date)
      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    },

    getAccuracyColor(accuracy) {
      if (accuracy >= 80) return '#4caf50'
      if (accuracy >= 60) return '#ff9800'
      return '#f44336'
    },

    goBack() {
      this.$router.back()
    }
  },
  mounted() {
    this.loadWeakAreas()
  }
}
</script>

<style scoped lang="scss">
.weak-areas-page {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  padding: 20px;
}

.header {
  background: rgba(255, 255, 255, 0.95);
  padding: 30px 20px;
  border-radius: 12px;
  margin-bottom: 30px;
  display: flex;
  flex-direction: column;
  gap: 10px;

  .btn-back {
    align-self: flex-start;
    background: none;
    border: none;
    font-size: 18px;
    cursor: pointer;
    padding: 5px 10px;
    border-radius: 6px;

    &:hover {
      background: rgba(0, 0, 0, 0.1);
    }
  }

  h1 {
    margin: 0 0 8px 0;
    color: #333;
    font-size: 28px;
  }

  .subtitle {
    margin: 0;
    color: #666;
    font-size: 14px;
  }
}

.stats-header {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 30px;

  .stat {
    background: rgba(255, 255, 255, 0.95);
    padding: 20px;
    border-radius: 12px;
    display: flex;
    flex-direction: column;
    gap: 8px;

    .label {
      font-size: 12px;
      color: #999;
      text-transform: uppercase;
    }

    .value {
      font-size: 24px;
      font-weight: bold;
      color: #333;
    }
  }
}

.weak-areas-list {
  max-width: 1000px;
  margin: 0 auto;
}

.areas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.area-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 5px solid #ccc;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 20px rgba(0, 0, 0, 0.15);
  }

  &.priority-high {
    border-left-color: #f44336;
  }

  &.priority-medium {
    border-left-color: #ff9800;
  }

  &.priority-low {
    border-left-color: #4caf50;
  }

  .area-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 15px;

    h3 {
      margin: 0;
      color: #333;
      font-size: 16px;
    }

    .priority-badge {
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;

      .priority-high & {
        background: rgba(244, 67, 54, 0.2);
        color: #f44336;
      }

      .priority-medium & {
        background: rgba(255, 152, 0, 0.2);
        color: #ff9800;
      }

      .priority-low & {
        background: rgba(76, 175, 80, 0.2);
        color: #4caf50;
      }
    }
  }

  .area-details {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-bottom: 15px;
    font-size: 12px;

    .detail {
      display: flex;
      flex-direction: column;
      gap: 4px;

      .label {
        color: #999;
        text-transform: uppercase;
      }

      .value {
        color: #333;
        font-weight: 600;
      }
    }
  }

  .accuracy-bar {
    height: 6px;
    background: rgba(0, 0, 0, 0.1);
    border-radius: 3px;
    overflow: hidden;
    margin-bottom: 15px;

    .accuracy-fill {
      height: 100%;
      transition: width 0.3s ease;
    }
  }

  .btn-practice {
    width: 100%;
    padding: 10px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    transition: transform 0.2s;

    &:hover {
      transform: scale(1.02);
    }
  }
}

.empty-state {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 60px 20px;
  text-align: center;
  max-width: 600px;
  margin: 0 auto;

  .empty-icon {
    font-size: 64px;
    margin-bottom: 20px;
  }

  h2 {
    margin: 0 0 10px 0;
    color: #333;
    font-size: 24px;
  }

  p {
    margin: 0 0 30px 0;
    color: #666;
  }
}

.modal-overlay {
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

  .modal {
    background: white;
    border-radius: 16px;
    padding: 40px;
    max-width: 500px;
    width: 90%;
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
      margin: 0 0 8px 0;
      color: #333;
    }

    .subject {
      margin: 0 0 20px 0;
      color: #999;
      font-size: 14px;
    }

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 15px;
      margin: 20px 0;
      padding: 20px;
      background: #f5f5f5;
      border-radius: 12px;

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
          font-size: 18px;
          font-weight: 600;
          color: #333;
        }
      }
    }

    .recommendations {
      background: rgba(255, 193, 7, 0.1);
      border: 1px solid #ffc107;
      border-radius: 12px;
      padding: 15px;
      margin: 20px 0;

      h3 {
        margin: 0 0 10px 0;
        color: #333;
        font-size: 14px;
      }

      ul {
        margin: 0;
        padding-left: 20px;
        list-style: none;

        li {
          margin: 8px 0;
          color: #666;
          font-size: 13px;

          &:before {
            content: '✓ ';
            color: #ffc107;
            font-weight: 600;
            margin-right: 8px;
          }
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
  .areas-grid {
    grid-template-columns: 1fr;
  }

  .stats-header {
    grid-template-columns: 1fr;
  }
}
</style>
