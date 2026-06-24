<template>
  <div class="subject-topics-page">
    <!-- Header -->
    <header class="header">
      <button @click="goBack" class="btn-back">← Back</button>
      <div class="subject-info">
        <h1 :style="{ color: subject.color }">{{ subject.icon }} {{ subject.name }}</h1>
        <p v-if="subject.description" class="description">{{ subject.description }}</p>
      </div>
    </header>

    <!-- Progress -->
    <div class="progress-section">
      <div class="progress-label">
        <span>Topic mastery: {{ mastery }}%</span>
        <span>{{ completedTopics }} / {{ topics.length }} topics</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: mastery + '%' }"></div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Loading topics...</p>
    </div>

    <!-- Topics Grid -->
    <div v-else class="topics-grid">
      <div
        v-for="(topic, index) in topics"
        :key="topic.id"
        class="topic-card"
        :class="{ completed: topic.progress?.mastery === 100 }"
        @click="selectTopic(topic)"
      >
        <div class="topic-number">{{ index + 1 }}</div>
        <div class="topic-icon">{{ topic.icon || '📚' }}</div>
        <h3>{{ topic.name }}</h3>
        <p class="topic-description">{{ topic.description }}</p>
        
        <div class="topic-meta">
          <span class="level-count">{{ topic.level_count }} levels</span>
          <span class="xp">{{ topic.xp_earned || 0 }} XP</span>
        </div>

        <div class="topic-progress">
          <div class="mini-progress-bar">
            <div class="mini-progress-fill" :style="{ width: (topic.progress?.mastery || 0) + '%' }"></div>
          </div>
          <span class="mastery">{{ topic.progress?.mastery || 0 }}%</span>
        </div>

        <div v-if="topic.progress?.mastery === 100" class="completed-badge">
          ✓ MASTERED
        </div>
      </div>
    </div>

    <!-- Topic Details Modal -->
    <div v-if="selectedTopic && !loading" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <button @click="closeModal" class="modal-close">✕</button>
        <h2>{{ selectedTopic.name }}</h2>
        <p>{{ selectedTopic.description }}</p>

        <div class="topic-stats">
          <div class="stat">
            <span class="label">Levels</span>
            <span class="value">{{ selectedTopic.level_count }}</span>
          </div>
          <div class="stat">
            <span class="label">Mastery</span>
            <span class="value">{{ selectedTopic.progress?.mastery || 0 }}%</span>
          </div>
          <div class="stat">
            <span class="label">XP Earned</span>
            <span class="value">{{ selectedTopic.xp_earned || 0 }}</span>
          </div>
        </div>

        <div class="modal-actions">
          <button @click="closeModal" class="btn btn-secondary">Cancel</button>
          <button @click="playTopic(selectedTopic)" class="btn btn-primary">Start Topic →</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useGameStore } from '@/store/game_store'

export default {
  name: 'SubjectTopicsPage',
  setup() {
    const gameStore = useGameStore()
    return { gameStore }
  },
  data() {
    return {
      subjectId: null,
      subject: { name: 'Subject', icon: '📚', color: '#667eea' },
      topics: [],
      loading: false,
      selectedTopic: null,
      mastery: 0,
      completedTopics: 0
    }
  },
  methods: {
    goBack() {
      this.$router.back()
    },

    async loadTopics() {
      try {
        this.loading = true
        this.topics = await this.gameStore.fetchTopics(this.subjectId)
        
        // Calculate mastery
        this.completedTopics = this.topics.filter(t => (t.progress?.mastery || 0) === 100).length
        this.mastery = Math.round((this.completedTopics / this.topics.length) * 100 || 0)
      } catch (error) {
        console.error('Error loading topics:', error)
      } finally {
        this.loading = false
      }
    },

    selectTopic(topic) {
      this.selectedTopic = topic
    },

    closeModal() {
      this.selectedTopic = null
    },

    async playTopic(topic) {
      this.gameStore.setCurrentTopic(topic)
      this.$router.push(`/game/topic/${topic.id}`)
    }
  },
  mounted() {
    this.subjectId = this.$route.params.subjectId
    this.subject = this.$route.params.subject || this.gameStore.currentSubject || this.subject
    this.loadTopics()
  }
}
</script>

<style scoped lang="scss">
.subject-topics-page {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  padding: 20px;
}

.header {
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

    &:hover {
      background: rgba(0, 0, 0, 0.1);
    }
  }

  .subject-info {
    flex: 1;

    h1 {
      margin: 0 0 8px 0;
      color: #333;
      font-size: 28px;
    }

    .description {
      margin: 0;
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

.topics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.topic-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  border: 2px solid transparent;

  &:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 20px rgba(0, 0, 0, 0.2);
    border-color: #667eea;
  }

  &.completed {
    background: rgba(76, 175, 80, 0.1);
    border-color: #4caf50;
  }

  .topic-number {
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

  .topic-icon {
    font-size: 40px;
    margin-bottom: 12px;
    display: block;
  }

  h3 {
    margin: 0 0 8px 0;
    color: #333;
    font-size: 16px;
  }

  .topic-description {
    margin: 0 0 12px 0;
    color: #666;
    font-size: 13px;
    line-height: 1.4;
    min-height: 26px;
  }

  .topic-meta {
    display: flex;
    gap: 12px;
    font-size: 12px;
    margin-bottom: 12px;

    .level-count {
      background: rgba(102, 126, 234, 0.1);
      padding: 4px 8px;
      border-radius: 4px;
      color: #667eea;
    }

    .xp {
      color: #ff9800;
      font-weight: 600;
    }
  }

  .topic-progress {
    margin-bottom: 12px;

    .mini-progress-bar {
      height: 4px;
      background: rgba(0, 0, 0, 0.1);
      border-radius: 2px;
      overflow: hidden;
      margin-bottom: 4px;

      .mini-progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #4caf50, #8bc34a);
        transition: width 0.3s ease;
      }
    }

    .mastery {
      font-size: 12px;
      color: #999;
      font-weight: 600;
    }
  }

  .completed-badge {
    display: inline-block;
    background: #4caf50;
    color: white;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
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
      margin: 0 0 10px 0;
      color: #333;
    }

    > p {
      margin: 0 0 20px 0;
      color: #666;
    }

    .topic-stats {
      background: #f5f5f5;
      border-radius: 12px;
      padding: 20px;
      margin: 20px 0;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 15px;

      .stat {
        display: flex;
        flex-direction: column;
        gap: 5px;
        text-align: center;

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
  .topics-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }

  .header {
    flex-direction: column;
  }

  .modal-overlay .modal {
    .topic-stats {
      grid-template-columns: 1fr;
    }
  }
}
</style>
