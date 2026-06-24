<template>
  <AppLayout>
    <div class="quiz-take" v-if="quiz && !submitted">
      <div class="qt-header card">
        <div>
          <h2>{{ quiz.topic }}</h2>
          <p>{{ difficultyLabel }} · {{ languageLabel }} · {{ quiz.total }} questions</p>
        </div>
        <div class="qt-side">
          <div class="qt-progress">
            <div class="progress-bar"><div class="progress-fill" :style="`width:${progressPercent}%`"></div></div>
            <span>{{ currentQ }}/{{ quiz.total }}</span>
          </div>
          <div class="timer-box" :class="{ danger: secondsLeft <= 10 }">
            <div class="timer-label">Time Left</div>
            <div class="timer-value">{{ timerText }}</div>
          </div>
        </div>
      </div>

      <div class="question-card card">
        <div class="q-top">
          <div class="q-num">Question {{ currentQ }} of {{ quiz.total }}</div>
          <div class="chip chip-amber">{{ timePerQuestion }} sec / question</div>
        </div>
        <h3 class="q-text">{{ currentQuestion.question }}</h3>
        <div class="options">
          <button
            v-for="(option, index) in currentQuestion.options"
            :key="index"
            class="option-btn"
            :class="{ selected: answers[currentQ - 1] === index }"
            @click="selectAnswer(index)"
          >
            <span class="opt-letter">{{ ['A', 'B', 'C', 'D'][index] }}</span>
            <span>{{ option }}</span>
          </button>
        </div>
      </div>

      <div class="qt-nav">
        <button class="btn btn-outline" @click="prev" :disabled="currentQ === 1">Previous</button>
        <div class="dots">
          <button
            v-for="index in quiz.total"
            :key="index"
            class="dot"
            :class="{ answered: answers[index - 1] !== undefined, current: index === currentQ }"
            @click="jumpTo(index)"
          ></button>
        </div>
        <button v-if="currentQ < quiz.total" class="btn btn-primary" @click="next">
          Next
        </button>
        <button v-else class="btn btn-primary" @click="submitQuiz()" :disabled="submitting">
          <span class="spinner" v-if="submitting"></span>
          <span v-else>Submit Quiz</span>
        </button>
      </div>

      <div class="answered-count">{{ answeredCount }}/{{ quiz.total }} answered</div>
    </div>

    <div class="quiz-result card" v-if="result">
      <div class="result-icon">{{ result.passed ? 'PASS' : 'TRY' }}</div>
      <h2>{{ result.passed ? 'Congratulations!' : 'Keep practicing!' }}</h2>
      <div class="result-score" :class="result.score >= 80 ? 'exc' : result.score >= 60 ? 'good' : 'low'">
        {{ result.score }}%
      </div>
      <p>{{ result.correct || 0 }} / {{ result.total || quiz?.total || 0 }} correct answers</p>
      <div class="chip chip-amber" v-if="result.xp_earned > 0">+{{ result.xp_earned }} XP earned</div>

      <div class="feedback-list mt-6" v-if="result.feedback?.length">
        <h3 class="mb-4">Answer Review</h3>
        <div v-for="(feedback, index) in result.feedback" :key="index" class="feedback-item" :class="feedback.is_correct ? 'correct' : 'wrong'">
          <div class="fb-q">{{ index + 1 }}. {{ feedback.question }}</div>
          <div class="fb-ans">
            <span class="fb-label">Your answer:</span> {{ feedback.your_answer }}
            <span v-if="!feedback.is_correct"> · <span class="fb-correct">Correct: {{ feedback.correct_answer }}</span></span>
          </div>
          <div class="fb-exp" v-if="feedback.explanation">{{ feedback.explanation }}</div>
        </div>
      </div>

      <div class="result-actions mt-6">
        <router-link to="/quiz" class="btn btn-primary">New Quiz</router-link>
        <router-link to="/quiz" class="btn btn-secondary">Quiz Leaderboard</router-link>
      </div>
    </div>

    <div class="loading-state" v-if="!quiz && !result"><div class="spinner"></div></div>
  </AppLayout>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { toast } from 'vue3-toastify'

import api from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useAuthStore } from '@/store/auth'
import { getRecentQuizCache, getTimerForDifficulty, upsertRecentQuiz } from '@/utils/quizHistory'

const route = useRoute()
const auth = useAuthStore()
const quiz = ref(null)
const answers = ref([])
const currentQ = ref(1)
const submitted = ref(false)
const submitting = ref(false)
const result = ref(null)
const secondsLeft = ref(0)

let timerId = null

const languageNames = {
  en: 'English',
  bn: 'Bangla',
  hi: 'Hindi',
  ur: 'Urdu',
  ar: 'Arabic',
  zh: 'Chinese',
  ja: 'Japanese',
  ko: 'Korean',
  ta: 'Tamil',
  th: 'Thai',
  id: 'Indonesian',
  ms: 'Malay',
  vi: 'Vietnamese',
}

const currentQuestion = computed(() => quiz.value?.questions?.[currentQ.value - 1] || null)
const answeredCount = computed(() => answers.value.filter(answer => answer !== undefined).length)
const timePerQuestion = computed(() => quiz.value?.time_per_question || getTimerForDifficulty(quiz.value?.difficulty))
const progressPercent = computed(() => quiz.value ? Math.round((currentQ.value / quiz.value.total) * 100) : 0)
const timerText = computed(() => `${String(Math.floor(secondsLeft.value / 60)).padStart(2, '0')}:${String(secondsLeft.value % 60).padStart(2, '0')}`)
const difficultyLabel = computed(() => quiz.value?.difficulty ? quiz.value.difficulty[0].toUpperCase() + quiz.value.difficulty.slice(1) : 'Intermediate')
const languageLabel = computed(() => languageNames[quiz.value?.language] || quiz.value?.language?.toUpperCase() || 'English')

function clearTimer() {
  if (timerId) {
    clearInterval(timerId)
    timerId = null
  }
}

function startTimer() {
  if (!quiz.value || submitted.value || result.value) return
  clearTimer()
  secondsLeft.value = timePerQuestion.value
  timerId = setInterval(() => {
    if (secondsLeft.value > 0) {
      secondsLeft.value -= 1
      return
    }
    handleTimeUp()
  }, 1000)
}

function selectAnswer(index) {
  answers.value[currentQ.value - 1] = index
}

function jumpTo(index) {
  currentQ.value = index
}

function next() {
  if (!quiz.value) return
  if (currentQ.value < quiz.value.total) currentQ.value += 1
}

function prev() {
  if (currentQ.value > 1) currentQ.value -= 1
}

function saveQuizSnapshot(extra = {}) {
  if (!quiz.value) return
  upsertRecentQuiz({
    id: quiz.value.result_id,
    topic: quiz.value.topic,
    difficulty: quiz.value.difficulty,
    language: quiz.value.language,
    total_q: quiz.value.total,
    questions: quiz.value.questions,
    time_per_question: timePerQuestion.value,
    created_at: extra.created_at || new Date().toISOString(),
    score: extra.score ?? 0,
    correct: extra.correct ?? 0,
    xp_earned: extra.xp_earned ?? 0,
    submitted_result: extra.submitted_result || null,
  })
}

function handleTimeUp() {
  clearTimer()
  toast.info(currentQ.value < quiz.value.total ? 'Time up, moving to next question' : 'Time up, submitting your quiz')
  if (currentQ.value < quiz.value.total) {
    currentQ.value += 1
  } else {
    submitQuiz({ autoSubmit: true })
  }
}

async function submitQuiz({ autoSubmit = false } = {}) {
  if (!quiz.value || submitting.value) return
  if (!autoSubmit && answeredCount.value < quiz.value.total) {
    toast.warning(`Please answer all ${quiz.value.total} questions`)
    return
  }

  clearTimer()
  submitting.value = true
  try {
    const response = await api.post('/quiz/submit', {
      result_id: parseInt(route.params.id, 10),
      answers: answers.value,
    })
    result.value = response.data
    submitted.value = true
    if (auth.user) auth.user.xp_points += response.data.xp_earned || 0
    saveQuizSnapshot({
      score: response.data.score,
      correct: response.data.correct,
      xp_earned: response.data.xp_earned,
      submitted_result: response.data,
    })
    toast.success(`Score: ${response.data.score}% · +${response.data.xp_earned} XP`)
  } catch (error) {
    toast.error(error.response?.data?.detail || 'Submission failed')
    if (!result.value) startTimer()
  } finally {
    submitting.value = false
  }
}

function hydrateQuiz(payload) {
  if (!payload) return false
  quiz.value = {
    result_id: payload.result_id ?? payload.id,
    topic: payload.topic,
    difficulty: payload.difficulty || 'intermediate',
    language: payload.language || 'en',
    total: payload.total ?? payload.total_q ?? payload.questions?.length ?? 0,
    questions: payload.questions || [],
    time_per_question: payload.time_per_question || getTimerForDifficulty(payload.difficulty),
  }
  answers.value = new Array(quiz.value.total).fill(undefined)
  saveQuizSnapshot({ created_at: payload.created_at })
  return true
}

async function loadQuiz() {
  const stateQuiz = window.history.state?.quiz
  const stateResult = window.history.state?.submittedResult
  if (stateResult) {
    result.value = stateResult
    submitted.value = true
  }
  if (hydrateQuiz(stateQuiz)) return

  const cachedQuiz = getRecentQuizCache().find(item => String(item.id) === String(route.params.id))
  if (cachedQuiz?.submitted_result) {
    result.value = cachedQuiz.submitted_result
    submitted.value = true
  }
  if (hydrateQuiz(cachedQuiz)) return

  try {
    const historyResponse = await api.get('/quiz/history')
    const found = historyResponse.data.find(item => String(item.id) === String(route.params.id))

    if (found) {
      if (found.score > 0) {
        const cachedResult = getRecentQuizCache().find(item => String(item.id) === String(found.id))?.submitted_result
        result.value = cachedResult || {
          result_id: found.id,
          score: found.score,
          correct: found.correct,
          total: found.total_q,
          xp_earned: found.xp_earned,
          passed: found.score >= 60,
          feedback: [],
        }
        submitted.value = true
      }

      hydrateQuiz(found)
      return
    }
    toast.error('This quiz is not available for your account')
  } catch (error) {
    toast.error(`Unable to load quiz: ${error.response?.data?.detail || error.message}`)
  }
}

watch(currentQ, () => {
  if (!submitted.value && quiz.value) startTimer()
})

onMounted(async () => {
  await loadQuiz()
  if (quiz.value && !submitted.value) startTimer()
})

onBeforeUnmount(clearTimer)
</script>

<style scoped>
.quiz-take { display: flex; flex-direction: column; gap: 20px; max-width: 760px; margin: 0 auto; }
.qt-header { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.qt-header h2 { margin-bottom: 4px; }
.qt-header p { color: var(--text3); font-size: 13px; margin: 0; }
.qt-side { display: flex; align-items: center; gap: 14px; }
.qt-progress { display: flex; align-items: center; gap: 10px; min-width: 180px; font-size: 13px; color: var(--text3); }
.qt-progress .progress-bar { flex: 1; }
.timer-box { min-width: 110px; padding: 10px 12px; border-radius: var(--r); background: var(--bg3); border: 1px solid var(--border); text-align: center; }
.timer-box.danger { border-color: var(--rose); color: var(--rose); background: rgba(255, 107, 138, 0.08); }
.timer-label { font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--text3); }
.timer-value { font-size: 22px; font-weight: 800; margin-top: 2px; }
.q-top { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 12px; }
.q-num { font-size: 12px; color: var(--text3); font-weight: 600; }
.q-text { font-size: 18px; font-weight: 700; margin-bottom: 24px; line-height: 1.5; }
.options { display: flex; flex-direction: column; gap: 10px; }
.option-btn {
  display: flex; align-items: center; gap: 14px;
  padding: 14px 16px; border-radius: var(--r2);
  border: 1.5px solid var(--border); background: var(--bg3);
  cursor: pointer; text-align: left; font-size: 15px; color: var(--text2);
  transition: all var(--t);
}
.option-btn:hover { border-color: var(--p); background: var(--p-soft); color: var(--p); }
.option-btn.selected { border-color: var(--p); background: var(--p-soft); color: var(--p); font-weight: 600; }
.opt-letter {
  width: 28px; height: 28px; border-radius: 50%; background: var(--border);
  font-size: 12px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.option-btn.selected .opt-letter { background: var(--p); color: #fff; }
.qt-nav { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.dots { display: flex; gap: 6px; flex-wrap: wrap; justify-content: center; }
.dot {
  width: 12px; height: 12px; border-radius: 50%; background: var(--border);
  cursor: pointer; transition: all var(--t); border: 0;
}
.dot.answered { background: var(--p); }
.dot.current { background: var(--amber); transform: scale(1.2); }
.answered-count { text-align: center; font-size: 13px; color: var(--text3); }
.quiz-result { text-align: center; padding: 48px; max-width: 760px; margin: 0 auto; }
.result-icon { font-size: 48px; font-weight: 900; margin-bottom: 16px; color: var(--p); }
.result-score { font-size: 72px; font-weight: 900; margin: 16px 0 8px; }
.result-score.exc { color: var(--green); }
.result-score.good { color: var(--amber); }
.result-score.low { color: var(--rose); }
.feedback-list { text-align: left; }
.feedback-item { padding: 16px; border-radius: var(--r); margin-bottom: 10px; }
.feedback-item.correct { background: rgba(34, 197, 94, 0.08); border: 1px solid rgba(34, 197, 94, 0.2); }
.feedback-item.wrong { background: rgba(255, 107, 138, 0.08); border: 1px solid rgba(255, 107, 138, 0.2); }
.fb-q { font-size: 14px; font-weight: 600; color: var(--text); margin-bottom: 6px; }
.fb-ans { font-size: 13px; color: var(--text2); }
.fb-correct { color: var(--green); font-weight: 600; }
.fb-exp { font-size: 12px; color: var(--text3); margin-top: 6px; }
.fb-label { font-weight: 600; }
.result-actions { display: flex; gap: 12px; justify-content: center; }
.loading-state { display: flex; justify-content: center; padding: 80px; }
@media (max-width: 768px) {
  .qt-header { flex-direction: column; align-items: flex-start; }
  .qt-side { width: 100%; justify-content: space-between; }
  .qt-nav { flex-direction: column; }
  .result-actions { flex-direction: column; }
}
</style>
