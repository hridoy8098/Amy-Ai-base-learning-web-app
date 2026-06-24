<template>
  <div class="game-results-page">
    <!-- Header -->
    <header class="results-header">
      <button @click="goHome" class="btn-home">← Home</button>
      <h1>📊 Level Results</h1>
    </header>

    <!-- Loading State -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Loading results...</p>
    </div>

    <!-- Results Card -->
    <div v-else-if="result" class="results-container">
      <!-- Main Result -->
      <div class="result-card" :class="result.passed ? 'passed' : 'failed'">
        <div class="result-header">
          <span v-if="result.passed" class="result-emoji">🎉</span>
          <span v-else class="result-emoji">😔</span>
          <h2>{{ result.passed ? 'Excellent!' : 'Keep Trying' }}</h2>
        </div>

        <!-- Score -->
        <div class="score-display">
          <div class="score-circle">
            <span class="score-percent">{{ result.score }}%</span>
            <svg class="score-ring" viewBox="0 0 100 100">
              <circle
                cx="50"
                cy="50"
                r="45"
                :class="result.passed ? 'passed' : 'failed'"
                :style="{ 'stroke-dashoffset': 282 - (2.82 * result.score) }"
              />
            </svg>
          </div>
        </div>

        <!-- Stats Grid -->
        <div class="stats-grid">
          <div class="stat">
            <span class="label">Correct</span>
            <span class="value">{{ result.correct }} / {{ result.total }}</span>
          </div>
          <div class="stat">
            <span class="label">Time</span>
            <span class="value">{{ formatTime(result.time_taken) }}</span>
          </div>
          <div class="stat">
            <span class="label">XP Earned</span>
            <span class="value xp">+{{ result.xp_earned }}</span>
          </div>
          <div class="stat">
            <span class="label">Stars</span>
            <span class="value stars">
              <span v-for="i in result.stars" :key="i">⭐</span>
            </span>
          </div>
        </div>

        <!-- Feedback -->
        <div class="feedback">
          <p>{{ result.feedback }}</p>
        </div>

        <!-- Actions -->
        <div class="result-actions">
          <button @click="goHome" class="btn btn-secondary">← Back to Map</button>
          <button @click="retryLevel" class="btn btn-secondary">↻ Try Again</button>
          <button v-if="result.passed" @click="nextLevel" class="btn btn-primary">
            Continue →
          </button>
        </div>
      </div>

      <!-- Answer Review -->
      <div class="answer-review">
        <h3>📝 Answer Review</h3>
        <div class="review-items">
          <div
            v-for="(review, index) in result.answer_reviews"
            :key="index"
            class="review-item"
            :class="review.is_correct ? 'correct' : 'incorrect'"
          >
            <div class="review-header">
              <span class="question-num">Question {{ index + 1 }}</span>
              <span v-if="review.is_correct" class="badge correct">✓ Correct</span>
              <span v-else class="badge incorrect">✗ Incorrect</span>
            </div>
            <p class="question-text">{{ review.question_text }}</p>
            <div class="answers">
              <div class="user-answer">
                <strong>Your Answer:</strong> {{ review.user_answer }}
              </div>
              <div v-if="!review.is_correct" class="correct-answer">
                <strong>Correct Answer:</strong> {{ review.correct_answer }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recommendations -->
      <div class="recommendations">
        <h3>💡 Recommendations</h3>
        <ul>
          <li v-if="result.score < 60">Review the topic concepts before trying again</li>
          <li v-if="result.score < 80">Practice similar questions to build confidence</li>
          <li v-if="result.time_taken > 300">Try to complete levels faster for bonus points</li>
          <li>Review your wrong answers regularly</li>
          <li>Practice weak areas daily for better retention</li>
        </ul>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <p>No results found</p>
      <button @click="goHome" class="btn btn-primary">← Go Home</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GameResultsPage',
  data() {
    return {
      attemptId: null,
      result: null,
      loading: false
    }
  },
  methods: {
    async loadResults() {
      try {
        this.loading = true
        // In a real app, this would fetch from API
        // For now, use mock data or get from route params
        this.result = this.$route.params.result || this.getMockResult()
      } catch (error) {
        console.error('Error loading results:', error)
      } finally {
        this.loading = false
      }
    },

    getMockResult() {
      return {
        id: 1,
        passed: true,
        score: 85,
        correct: 17,
        total: 20,
        time_taken: 180,
        xp_earned: 150,
        stars: 2,
        feedback: 'Great job! You scored above the pass mark. Keep practicing to improve further!',
        answer_reviews: [
          {
            question_num: 1,
            question_text: 'What is a noun?',
            user_answer: 'A person, place, or thing',
            correct_answer: 'A person, place, or thing',
            is_correct: true
          },
          {
            question_num: 2,
            question_text: 'Define a verb',
            user_answer: 'An object',
            correct_answer: 'An action or state of being',
            is_correct: false
          }
        ]
      }
    },

    formatTime(seconds) {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins}m ${secs}s`
    },

    goHome() {
      this.$router.push('/game')
    },

    retryLevel() {
      this.$router.back()
    },

    nextLevel() {
      this.$router.push('/game')
    }
  },
  mounted() {
    this.attemptId = this.$route.params.attemptId
    this.loadResults()
  }
}
</script>

<style scoped lang="scss">
.game-results-page {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  padding: 20px;
}

.results-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
  background: rgba(255, 255, 255, 0.95);
  padding: 20px;
  border-radius: 12px;

  .btn-home {
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
    margin: 0;
    flex: 1;
    color: #333;
  }
}

.results-container {
  max-width: 1000px;
  margin: 0 auto;
}

.result-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 40px;
  margin-bottom: 30px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);

  &.passed {
    border-top: 4px solid #4caf50;
  }

  &.failed {
    border-top: 4px solid #f44336;
  }

  .result-header {
    text-align: center;
    margin-bottom: 30px;

    .result-emoji {
      font-size: 64px;
      display: block;
      margin-bottom: 15px;
    }

    h2 {
      margin: 0;
      color: #333;
      font-size: 32px;
    }
  }

  .score-display {
    display: flex;
    justify-content: center;
    margin: 30px 0;

    .score-circle {
      position: relative;
      width: 200px;
      height: 200px;
      display: flex;
      align-items: center;
      justify-content: center;

      .score-percent {
        font-size: 48px;
        font-weight: bold;
        color: #667eea;
        z-index: 1;
      }

      .score-ring {
        position: absolute;
        width: 100%;
        height: 100%;
        transform: rotate(-90deg);

        circle {
          fill: none;
          stroke-width: 8;
          stroke-linecap: round;
          transition: stroke-dashoffset 0.8s ease;
          stroke-dasharray: 282;

          &.passed {
            stroke: #4caf50;
          }

          &.failed {
            stroke: #f44336;
          }
        }
      }
    }
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 15px;
    margin: 30px 0;
    padding: 20px;
    background: #f5f5f5;
    border-radius: 12px;

    .stat {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;

      .label {
        font-size: 12px;
        color: #999;
        text-transform: uppercase;
      }

      .value {
        font-size: 20px;
        font-weight: bold;
        color: #333;

        &.xp {
          color: #ff9800;
        }

        &.stars {
          font-size: 18px;
          letter-spacing: 3px;
        }
      }
    }
  }

  .feedback {
    background: rgba(102, 126, 234, 0.1);
    border: 1px solid #667eea;
    border-radius: 12px;
    padding: 20px;
    margin: 20px 0;
    text-align: center;

    p {
      margin: 0;
      color: #333;
      line-height: 1.6;
    }
  }

  .result-actions {
    display: flex;
    gap: 15px;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 30px;
  }
}

.answer-review {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 30px;
  margin-bottom: 30px;

  h3 {
    margin: 0 0 20px 0;
    color: #333;
  }

  .review-items {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }

  .review-item {
    padding: 20px;
    background: #f5f5f5;
    border-radius: 12px;
    border-left: 4px solid #ccc;

    &.correct {
      border-left-color: #4caf50;
      background: rgba(76, 175, 80, 0.05);
    }

    &.incorrect {
      border-left-color: #f44336;
      background: rgba(244, 67, 54, 0.05);
    }

    .review-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;

      .question-num {
        font-weight: 600;
        color: #333;
      }

      .badge {
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;

        &.correct {
          background: #4caf50;
          color: white;
        }

        &.incorrect {
          background: #f44336;
          color: white;
        }
      }
    }

    .question-text {
      margin: 0 0 12px 0;
      color: #333;
      font-weight: 500;
    }

    .answers {
      display: flex;
      flex-direction: column;
      gap: 8px;
      font-size: 13px;

      .user-answer,
      .correct-answer {
        padding: 8px 12px;
        background: rgba(0, 0, 0, 0.05);
        border-radius: 6px;
        color: #333;

        strong {
          display: block;
          margin-bottom: 4px;
          color: #666;
        }
      }

      .correct-answer {
        background: rgba(76, 175, 80, 0.1);
      }
    }
  }
}

.recommendations {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 30px;
  margin-bottom: 30px;

  h3 {
    margin: 0 0 15px 0;
    color: #333;
  }

  ul {
    margin: 0;
    padding: 0;
    list-style: none;

    li {
      padding: 12px;
      background: rgba(255, 193, 7, 0.1);
      border-left: 3px solid #ffc107;
      margin-bottom: 10px;
      border-radius: 6px;
      color: #333;

      &:before {
        content: '💡 ';
        margin-right: 8px;
      }
    }
  }
}

.empty-state {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 60px 20px;
  text-align: center;

  p {
    color: #666;
    margin: 0 0 20px 0;
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
  .result-card {
    padding: 25px;

    .score-display .score-circle {
      width: 150px;
      height: 150px;

      .score-percent {
        font-size: 36px;
      }
    }

    .stats-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  .result-actions {
    flex-direction: column;

    .btn {
      width: 100%;
    }
  }
}
</style>
