<template>
  <div class="level-game-page">
    <!-- HUD (Heads Up Display) -->
    <div class="game-hud">
      <div class="hud-left">
        <button @click="goBack" class="btn-back">← Exit</button>
        <div class="game-title">
          <h2>{{ currentLevel?.title }}</h2>
          <span class="level-number">Level {{ currentLevel?.level_number }}</span>
        </div>
      </div>

      <div class="hud-center">
        <div class="progress">
          <span class="progress-text">{{ getCurrentQuestionIndex + 1 }} / {{ getTotalQuestions }}</span>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: getProgressPercentage + '%' }"></div>
          </div>
        </div>
      </div>

      <div class="hud-right">
        <div class="hearts">
          <span v-for="i in maxHearts" :key="i" class="heart" :class="{ empty: i > currentHearts }">
            ❤️
          </span>
        </div>
        <div class="timer">
          <span class="timer-icon">⏱️</span>
          <span class="timer-value" :class="{ warning: timeLeft < 60 }">
            {{ formatTime(timeLeft) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loadingQuestion" class="loading-screen">
      <div class="spinner"></div>
      <p>Loading question...</p>
    </div>

    <!-- Question Display -->
    <div v-else-if="currentQuestion" class="game-container">
      <!-- Question -->
      <div class="question-section">
        <div class="question-header">
          <div class="difficulty-badge" :class="`difficulty-${currentLevel?.difficulty}`">
            {{ currentLevel?.difficulty }}
          </div>
          <span class="question-type">{{ currentQuestion.question_type }}</span>
        </div>

        <div class="question-text">
          {{ currentQuestion.question_text }}
        </div>

        <div v-if="currentQuestion.image_url" class="question-image">
          <img :src="currentQuestion.image_url" :alt="currentQuestion.question_text" />
        </div>

        <!-- Question Type Components -->
        <!-- Multiple Choice -->
        <div v-if="currentQuestion.question_type === 'multiple_choice'" class="answers-grid">
          <button
            v-for="(option, index) in currentQuestion.options"
            :key="index"
            class="answer-option"
            :class="{
              selected: userAnswer === option,
              correct: showResult && option === currentQuestion.correct_answer,
              incorrect: showResult && userAnswer === option && userAnswer !== currentQuestion.correct_answer
            }"
            @click="selectAnswer(option)"
            :disabled="showResult"
          >
            <span class="option-letter">{{ String.fromCharCode(65 + index) }}</span>
            <span class="option-text">{{ option }}</span>
          </button>
        </div>

        <!-- Fill in the Blank -->
        <div v-else-if="currentQuestion.question_type === 'fill_blank'" class="fill-blank">
          <input
            v-model="userAnswer"
            type="text"
            placeholder="Type your answer..."
            @keyup.enter="submitAnswer"
            :disabled="showResult"
            class="blank-input"
          />
          <small v-if="currentQuestion.hint" class="hint">💡 Hint: {{ currentQuestion.hint }}</small>
        </div>

        <!-- Matching -->
        <div v-else-if="currentQuestion.question_type === 'matching'" class="matching">
          <div class="matching-columns">
            <div class="column left">
              <div
                v-for="(item, index) in currentQuestion.left_items"
                :key="'left-' + index"
                class="matching-item"
                @click="selectMatch('left', index)"
                :class="{ selected: selectedMatch?.side === 'left' && selectedMatch?.index === index }"
              >
                {{ item }}
              </div>
            </div>
            <div class="lines"></div>
            <div class="column right">
              <div
                v-for="(item, index) in currentQuestion.right_items"
                :key="'right-' + index"
                class="matching-item"
                @click="selectMatch('right', index)"
                :class="{ selected: selectedMatch?.side === 'right' && selectedMatch?.index === index }"
              >
                {{ item }}
              </div>
            </div>
          </div>
        </div>

        <!-- Ordering -->
        <div v-else-if="currentQuestion.question_type === 'ordering'" class="ordering">
          <p class="instruction">Drag items to arrange them in correct order:</p>
          <div class="order-items">
            <div
              v-for="(item, index) in currentQuestion.options"
              :key="index"
              draggable="true"
              @dragstart="dragStart(index)"
              @dragover.prevent
              @drop="drop(index)"
              class="order-item"
            >
              <span class="number">{{ index + 1 }}</span>
              <span>{{ item }}</span>
            </div>
          </div>
        </div>

        <!-- Essay/Short Answer -->
        <div v-else-if="currentQuestion.question_type === 'essay'" class="essay">
          <textarea
            v-model="userAnswer"
            placeholder="Write your answer here..."
            :disabled="showResult"
            rows="6"
            class="essay-textarea"
          ></textarea>
          <small v-if="currentQuestion.word_limit" class="word-limit">
            Max {{ currentQuestion.word_limit }} words. ({{ userAnswer.split(' ').length }} / {{ currentQuestion.word_limit }})
          </small>
        </div>

        <!-- Confidence Level (after answer is submitted) -->
        <div v-if="showResult && !showExplanation" class="confidence-section">
          <p>How confident were you?</p>
          <div class="confidence-options">
            <button
              v-for="level in confidenceLevels"
              :key="level"
              @click="setConfidence(level)"
              :class="{ selected: confidence === level }"
              class="confidence-btn"
            >
              {{ level }}
            </button>
          </div>
        </div>

        <!-- Explanation -->
        <div v-if="showExplanation" class="explanation">
          <div class="result-badge" :class="isAnswerCorrect ? 'correct' : 'incorrect'">
            {{ isAnswerCorrect ? '✓ CORRECT!' : '✗ INCORRECT' }}
          </div>
          <div class="explanation-text">
            <strong>Explanation:</strong>
            <p>{{ currentQuestion.explanation }}</p>
          </div>
          <div v-if="!isAnswerCorrect" class="correct-answer">
            <strong>Correct Answer:</strong>
            <p>{{ currentQuestion.correct_answer }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Result Screen -->
    <div v-else-if="resultScreen" class="result-screen">
      <div class="result-card">
        <div class="result-header" :class="resultScreen.passed ? 'passed' : 'failed'">
          <span v-if="resultScreen.passed" class="result-emoji">🎉</span>
          <span v-else class="result-emoji">😔</span>
          <h1>{{ resultScreen.passed ? 'Level Completed!' : 'Try Again' }}</h1>
        </div>

        <div class="result-stats">
          <div class="stat">
            <span class="label">Score</span>
            <span class="value">{{ resultScreen.score }}%</span>
          </div>
          <div class="stat">
            <span class="label">Correct</span>
            <span class="value">{{ resultScreen.correct }} / {{ resultScreen.total }}</span>
          </div>
          <div class="stat">
            <span class="label">Time</span>
            <span class="value">{{ formatTime(resultScreen.time_taken) }}</span>
          </div>
          <div v-if="resultScreen.xp_earned > 0" class="stat">
            <span class="label">XP Earned</span>
            <span class="value xp">+{{ resultScreen.xp_earned }} 🌟</span>
          </div>
        </div>

        <div v-if="resultScreen.stars > 0" class="stars-earned">
          <span v-for="i in resultScreen.stars" :key="i">⭐</span>
        </div>

        <div class="result-feedback">
          {{ resultScreen.feedback }}
        </div>

        <div class="result-actions">
          <button @click="retryLevel" class="btn btn-secondary">↻ Try Again</button>
          <button @click="nextLevel" class="btn btn-primary" v-if="resultScreen.passed">
            Continue →
          </button>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div v-if="currentQuestion && !resultScreen" class="action-buttons">
      <button
        @click="prevQuestion"
        :disabled="getCurrentQuestionIndex === 0"
        class="btn btn-secondary"
      >
        ← Previous
      </button>

      <button
        v-if="!showResult"
        @click="submitAnswer"
        :disabled="!userAnswer"
        class="btn btn-primary"
      >
        Submit Answer
      </button>

      <button
        v-else-if="!showExplanation"
        @click="continueToExplanation"
        class="btn btn-primary"
      >
        Continue
      </button>

      <button
        v-else
        @click="nextQuestion"
        :disabled="isLastQuestion"
        class="btn btn-primary"
      >
        {{ isLastQuestion ? 'Finish' : 'Next Question' }} →
      </button>
    </div>

    <!-- Pause Menu -->
    <div v-if="showPauseMenu" class="pause-overlay" @click="showPauseMenu = false">
      <div class="pause-menu" @click.stop>
        <h2>Game Paused</h2>
        <div class="pause-options">
          <button @click="showPauseMenu = false" class="btn btn-primary">Resume</button>
          <button @click="goBack" class="btn btn-secondary">Exit Level</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useGameStore } from '@/store/game_store'

const router = useRouter()
const route = useRoute()
const gameStore = useGameStore()

const levelId = ref(null)
const userAnswer = ref('')
const confidence = ref(null)
const showResult = ref(false)
const showExplanation = ref(false)
const showPauseMenu = ref(false)
const timeLeft = ref(300)
const timerInterval = ref(null)
const startTime = ref(null)
const selectedMatch = ref(null)
const draggedIndex = ref(null)
const resultScreen = ref(null)
const loadingQuestion = ref(false)
const confidenceLevels = ['Not sure', 'Somewhat sure', 'Very sure']
const maxHearts = ref(3)
const currentHearts = ref(3)
const isAnswerCorrect = ref(false)

const currentAttempt = computed(() => gameStore.currentAttempt)
const currentQuestions = computed(() => gameStore.currentQuestions)
const currentLevel = computed(() => gameStore.currentLevel)
const loadingGameStart = computed(() => gameStore.loadingGameStart)
const currentQuestion = computed(() => gameStore.currentQuestion)
const isLastQuestion = computed(() => gameStore.isLastQuestion)
const getProgressPercentage = computed(() => gameStore.progressPercentage)
const getTotalQuestions = computed(() => gameStore.totalQuestions)
const getCurrentQuestionIndex = computed(() => gameStore.questionsAnswered)

function selectAnswer(option) {
  if (!showResult.value) {
    userAnswer.value = option
  }
}

function selectMatch(side, index) {
  if (selectedMatch.value?.side === side && selectedMatch.value?.index === index) {
    selectedMatch.value = null
  } else {
    selectedMatch.value = { side, index }
  }
}

function dragStart(index) {
  draggedIndex.value = index
}

function drop(index) {
  if (draggedIndex.value !== null && draggedIndex.value !== index && Array.isArray(userAnswer.value)) {
    const items = [...userAnswer.value]
    ;[items[draggedIndex.value], items[index]] = [items[index], items[draggedIndex.value]]
    userAnswer.value = items
  }
}

function setConfidence(level) {
  confidence.value = level
  setTimeout(() => {
    showExplanation.value = true
  }, 300)
}

async function submitAnswerHandler() {
  if (!currentQuestion.value) return
  try {
    loadingQuestion.value = true
    const data = await gameStore.submitAnswer({
      attemptId: currentAttempt.value,
      questionId: currentQuestion.value.id,
      answer: userAnswer.value,
      timeTaken: Math.round((Date.now() - startTime.value) / 1000),
      confidence: confidence.value || 'not_sure'
    })

    isAnswerCorrect.value = data.is_correct
    showResult.value = true

    if (isAnswerCorrect.value) {
      currentHearts.value = Math.min(currentHearts.value + 1, maxHearts.value)
    } else {
      currentHearts.value = Math.max(currentHearts.value - 1, 0)
    }
  } catch (error) {
    console.error('Error submitting answer:', error)
  } finally {
    loadingQuestion.value = false
  }
}

function submitAnswer() {
  return submitAnswerHandler()
}

function prevQuestion() {
  if (getCurrentQuestionIndex.value > 0) {
    gameStore.prevQuestion()
  }
}

function nextQuestion() {
  return nextQuestionHandler()
}

function continueToExplanation() {
  showExplanation.value = true
}

async function nextQuestionHandler() {
  if (isLastQuestion.value) {
    await finishLevel()
  } else {
    userAnswer.value = ''
    showResult.value = false
    showExplanation.value = false
    confidence.value = null
    startTime.value = Date.now()
    gameStore.nextQuestion()
  }
}

async function finishLevel() {
  try {
    const data = await gameStore.completeLevel(currentAttempt.value)
    resultScreen.value = {
      passed: data.is_passed,
      score: data.final_score,
      correct: data.results.correct,
      total: data.results.total,
      time_taken: data.duration_seconds,
      xp_earned: data.rewards.total_xp,
      stars: data.stars_earned,
      feedback: data.rewards.total_xp > 0 ? 'Great job!' : 'Level complete'
    }
  } catch (error) {
    console.error('Error completing level:', error)
  }
}

function retryLevel() {
  gameStore.resetGame()
  router.push(`/game/play/${levelId.value}`)
}

function nextLevel() {
  router.back()
}

function goBack() {
  if (confirm('Are you sure you want to exit this level?')) {
    gameStore.resetGame()
    router.back()
  }
}

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function startTimer() {
  startTime.value = Date.now()
  timerInterval.value = window.setInterval(() => {
    timeLeft.value--
    if (timeLeft.value <= 0) {
      clearInterval(timerInterval.value)
      finishLevel()
    }
  }, 1000)
}

onBeforeUnmount(() => {
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
  }
})

onMounted(async () => {
  levelId.value = route.params.levelId

  if (!currentAttempt.value || currentQuestions.value.length === 0 || currentLevel.value?.id !== Number(levelId.value)) {
    await gameStore.startLevel(levelId.value)
  }

  startTimer()
})
</script>

<style scoped lang="scss">
.level-game-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
}

.game-hud {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  background: rgba(255, 255, 255, 0.95);
  padding: 15px 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

  .hud-left {
    display: flex;
    align-items: center;
    gap: 15px;
    flex: 1;

    .btn-back {
      background: none;
      border: none;
      font-size: 16px;
      cursor: pointer;
      padding: 5px 10px;
      border-radius: 6px;
      transition: 0.2s;

      &:hover {
        background: rgba(0, 0, 0, 0.1);
      }
    }

    .game-title {
      h2 {
        margin: 0;
        color: #333;
        font-size: 18px;
      }

      .level-number {
        color: #667eea;
        font-size: 12px;
        font-weight: 600;
      }
    }
  }

  .hud-center {
    flex: 2;

    .progress {
      display: flex;
      align-items: center;
      gap: 15px;

      .progress-text {
        font-size: 12px;
        color: #666;
        font-weight: 600;
        white-space: nowrap;
      }

      .progress-bar {
        flex: 1;
        height: 6px;
        background: rgba(0, 0, 0, 0.1);
        border-radius: 3px;
        overflow: hidden;

        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, #667eea, #764ba2);
          transition: width 0.3s ease;
        }
      }
    }
  }

  .hud-right {
    display: flex;
    align-items: center;
    gap: 20px;
    flex: 1;
    justify-content: flex-end;

    .hearts {
      display: flex;
      gap: 5px;

      .heart {
        font-size: 18px;
        opacity: 1;
        transition: opacity 0.2s;

        &.empty {
          opacity: 0.3;
          filter: grayscale(100%);
        }
      }
    }

    .timer {
      display: flex;
      align-items: center;
      gap: 8px;
      background: rgba(102, 126, 234, 0.1);
      padding: 8px 12px;
      border-radius: 6px;

      .timer-icon {
        font-size: 16px;
      }

      .timer-value {
        font-weight: 600;
        color: #667eea;
        font-size: 14px;

        &.warning {
          color: #ff9800;
        }
      }
    }
  }
}

.game-container {
  flex: 1;
  overflow-y: auto;
  padding: 30px 20px;

  .question-section {
    max-width: 800px;
    margin: 0 auto;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 16px;
    padding: 40px;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);

    .question-header {
      display: flex;
      align-items: center;
      gap: 15px;
      margin-bottom: 20px;

      .difficulty-badge {
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        color: white;

        &.difficulty-easy {
          background: #4caf50;
        }

        &.difficulty-medium {
          background: #ff9800;
        }

        &.difficulty-hard {
          background: #f44336;
        }
      }

      .question-type {
        font-size: 12px;
        color: #666;
        background: rgba(0, 0, 0, 0.05);
        padding: 6px 12px;
        border-radius: 6px;
      }
    }

    .question-text {
      font-size: 18px;
      color: #333;
      margin-bottom: 30px;
      line-height: 1.6;
    }

    .question-image {
      margin: 30px 0;
      border-radius: 12px;
      overflow: hidden;

      img {
        max-width: 100%;
        height: auto;
      }
    }

    .answers-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 15px;
      margin: 30px 0;

      .answer-option {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 20px;
        background: rgba(0, 0, 0, 0.05);
        border: 2px solid transparent;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s;
        font-size: 14px;

        &:hover:not(:disabled) {
          border-color: #667eea;
          background: rgba(102, 126, 234, 0.1);
        }

        &.selected {
          border-color: #667eea;
          background: rgba(102, 126, 234, 0.2);
        }

        &.correct {
          border-color: #4caf50;
          background: rgba(76, 175, 80, 0.2);
        }

        &.incorrect {
          border-color: #f44336;
          background: rgba(244, 67, 54, 0.2);
        }

        &:disabled {
          cursor: not-allowed;
        }

        .option-letter {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 32px;
          height: 32px;
          background: linear-gradient(135deg, #667eea, #764ba2);
          color: white;
          border-radius: 50%;
          font-weight: bold;
          flex-shrink: 0;
        }

        .option-text {
          flex: 1;
          text-align: left;
        }
      }
    }

    .fill-blank {
      margin: 30px 0;

      .blank-input {
        width: 100%;
        padding: 15px;
        font-size: 16px;
        border: 2px solid rgba(0, 0, 0, 0.1);
        border-radius: 10px;
        transition: border-color 0.3s;

        &:focus {
          outline: none;
          border-color: #667eea;
        }

        &:disabled {
          background: rgba(0, 0, 0, 0.05);
        }
      }

      .hint {
        display: block;
        margin-top: 10px;
        color: #999;
        font-size: 13px;
      }
    }

    .confidence-section {
      margin-top: 30px;
      padding: 20px;
      background: rgba(102, 126, 234, 0.1);
      border-radius: 10px;
      text-align: center;

      p {
        margin: 0 0 15px 0;
        color: #333;
        font-weight: 600;
      }

      .confidence-options {
        display: flex;
        gap: 10px;
        justify-content: center;

        .confidence-btn {
          padding: 10px 20px;
          border: 2px solid #667eea;
          background: white;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.3s;
          font-size: 13px;

          &:hover {
            background: #667eea;
            color: white;
          }

          &.selected {
            background: #667eea;
            color: white;
          }
        }
      }
    }

    .explanation {
      margin-top: 30px;
      padding: 20px;
      background: rgba(0, 0, 0, 0.05);
      border-left: 4px solid #667eea;
      border-radius: 8px;

      .result-badge {
        display: inline-block;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
        margin-bottom: 15px;

        &.correct {
          background: rgba(76, 175, 80, 0.2);
          color: #4caf50;
        }

        &.incorrect {
          background: rgba(244, 67, 54, 0.2);
          color: #f44336;
        }
      }

      .explanation-text,
      .correct-answer {
        margin: 15px 0 0 0;

        strong {
          display: block;
          margin-bottom: 8px;
          color: #333;
        }

        p {
          margin: 0;
          color: #666;
          line-height: 1.6;
        }
      }
    }

    .matching,
    .ordering,
    .essay {
      margin: 30px 0;

      .instruction {
        margin: 0 0 20px 0;
        color: #666;
      }

      .essay-textarea {
        width: 100%;
        padding: 15px;
        font-size: 14px;
        font-family: inherit;
        border: 2px solid rgba(0, 0, 0, 0.1);
        border-radius: 10px;
        transition: border-color 0.3s;

        &:focus {
          outline: none;
          border-color: #667eea;
        }

        &:disabled {
          background: rgba(0, 0, 0, 0.05);
        }
      }

      .word-limit {
        display: block;
        margin-top: 10px;
        color: #999;
        font-size: 13px;
      }
    }
  }
}

.action-buttons {
  display: flex;
  gap: 15px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.1);
  justify-content: center;
}

.loading-screen,
.result-screen {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  padding: 40px;
}

.loading-screen {
  flex-direction: column;

  .spinner {
    width: 60px;
    height: 60px;
    border: 5px solid rgba(255, 255, 255, 0.3);
    border-top: 5px solid white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  p {
    margin-top: 25px;
    color: white;
    font-size: 16px;
  }
}

.result-card {
  background: white;
  border-radius: 20px;
  padding: 50px 40px;
  text-align: center;
  max-width: 600px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);

  .result-header {
    margin-bottom: 40px;
    padding-bottom: 20px;
    border-bottom: 3px solid #f0f0f0;

    .result-emoji {
      font-size: 64px;
      display: block;
      margin-bottom: 15px;
    }

    h1 {
      margin: 0;
      font-size: 32px;
      color: #333;

      &.passed {
        color: #4caf50;
      }

      &.failed {
        color: #f44336;
      }
    }
  }

  .result-stats {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 30px;
    margin: 40px 0;

    .stat {
      display: flex;
      flex-direction: column;
      gap: 8px;

      .label {
        font-size: 12px;
        color: #999;
        text-transform: uppercase;
      }

      .value {
        font-size: 32px;
        font-weight: bold;
        color: #333;

        &.xp {
          color: #ff9800;
        }
      }
    }
  }

  .stars-earned {
    font-size: 40px;
    margin: 30px 0;
    letter-spacing: 5px;
  }

  .result-feedback {
    background: rgba(0, 0, 0, 0.05);
    padding: 20px;
    border-radius: 10px;
    margin: 30px 0;
    color: #666;
    line-height: 1.6;
  }

  .result-actions {
    display: flex;
    gap: 15px;
    margin-top: 30px;
    justify-content: center;
  }
}

.pause-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;

  .pause-menu {
    background: white;
    padding: 40px;
    border-radius: 16px;
    text-align: center;

    h2 {
      margin: 0 0 30px 0;
      color: #333;
    }

    .pause-options {
      display: flex;
      gap: 15px;
      justify-content: center;
    }
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .game-hud {
    flex-direction: column;
    gap: 15px;

    .hud-left,
    .hud-center,
    .hud-right {
      width: 100%;
    }
  }

  .game-container {
    padding: 15px;

    .question-section {
      padding: 25px;
    }
  }

  .action-buttons {
    flex-wrap: wrap;
  }

  .result-card {
    padding: 30px 25px;

    .result-stats {
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }
  }
}
</style>
