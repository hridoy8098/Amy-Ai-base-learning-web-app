<template>
  <AppLayout>
    <div class="quiz-page">
      <div class="quiz-header">
        <h1>Quiz Generator</h1>
        <p>Topic dao, language choose koro, ar Amy tomar jonno instant quiz ready korbe.</p>
      </div>

      <div class="card quiz-form">
        <h3>Generate New Quiz</h3>
        <div class="form-grid mt-4">
          <div class="form-group form-full">
            <label class="form-label">Topic *</label>
            <input
              v-model="form.topic"
              type="text"
              class="form-input"
              placeholder="e.g. Present Perfect Tense, Travel Vocabulary, Job Interview"
              required
            />
          </div>
          <div class="form-group">
            <label class="form-label">Subject</label>
            <input v-model="form.subject" type="text" class="form-input" placeholder="e.g. English Grammar" />
          </div>
          <div class="form-group">
            <label class="form-label">Difficulty</label>
            <select v-model="form.difficulty" class="form-input">
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Questions</label>
            <select v-model="form.num_questions" class="form-input">
              <option :value="3">3 questions</option>
              <option :value="5">5 questions</option>
              <option :value="10">10 questions</option>
              <option :value="15">15 questions</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Language</label>
            <select v-model="form.language" class="form-input">
              <option v-for="language in languages" :key="language.code" :value="language.code">
                {{ language.label }}
              </option>
            </select>
          </div>
        </div>

        <div class="quiz-info-row mt-4">
          <span class="chip chip-amber">{{ selectedTimer }} sec per question</span>
          <span class="text-sm text-muted">
            Advanced quiz e 30 sec, baki level e 50 sec. Question, option, explanation sob selected language e ashbe.
          </span>
        </div>

        <div class="quiz-form-footer mt-4">
          <button class="btn btn-primary btn-lg" @click="generateQuiz" :disabled="generating || !form.topic.trim()">
            <span class="spinner" v-if="generating"></span>
            <span v-else>Generate Quiz</span>
          </button>
          <div class="usage-note" v-if="usage && !usage.is_paid">
            {{ usage.quiz_generated_today || 0 }}/{{ QUIZ_LIMIT }} free quizzes today
            <router-link to="/pricing">Upgrade for unlimited</router-link>
          </div>
        </div>
      </div>

      <div class="quiz-grid">
        <div class="card">
          <div class="section-head">
            <div>
              <h3>Recent Quizzes</h3>
              <p class="text-muted">Last generated and submitted quizzes, including unsolved ones.</p>
            </div>
            <button class="btn btn-outline btn-sm" @click="loadPageData" :disabled="pageRefreshing">
              {{ pageRefreshing ? 'Refreshing...' : 'Refresh' }}
            </button>
          </div>

          <div v-if="loadingHistory" class="loading-state compact">
            <div class="spinner"></div>
          </div>

          <div v-else-if="history.length" class="history-grid">
            <button v-for="quiz in history" :key="quiz.id" class="history-card card" @click="openRecentQuiz(quiz)">
              <div class="hc-header">
                <div>
                  <div class="hc-topic">{{ quiz.topic }}</div>
                  <div class="hc-meta">
                    {{ formatDifficulty(quiz.difficulty) }} - {{ quiz.total_q }} questions - {{ languageName(quiz.language) }}
                  </div>
                </div>
                <div class="hc-score" :class="scoreClass(quiz.score)">
                  {{ quiz.score > 0 ? `${quiz.score}%` : 'Pending' }}
                </div>
              </div>
              <div class="hc-tags">
                <span class="chip chip-amber">{{ quiz.time_per_question || getTimerForDifficulty(quiz.difficulty) }} sec</span>
                <span class="chip" v-if="quiz.xp_earned > 0">+{{ quiz.xp_earned }} XP</span>
              </div>
              <div class="hc-footer">
                <span class="text-xs text-muted">{{ formatDate(quiz.created_at) }}</span>
                <span class="open-link">{{ quiz.score > 0 ? 'View' : 'Continue' }}</span>
              </div>
            </button>
          </div>

          <div v-else class="empty-state compact">
            <div class="icon">Q</div>
            <h3>No recent quiz yet</h3>
            <p>Upore topic diye first quiz generate korle ekhane automatically show korbe.</p>
          </div>
        </div>

        <div class="card leaderboard-card">
          <div class="section-head">
            <div>
              <h3>Quiz Leaderboard</h3>
              <p class="text-muted">Quiz score ar quiz XP er upor all user er moddhe top performer.</p>
            </div>
          </div>

          <div class="loading-state compact" v-if="loadingLeaderboard">
            <div class="spinner"></div>
          </div>

          <template v-else-if="quizLeaders.length">
            <div class="my-quiz-rank card" v-if="myQuizRank">
              <div>
                <div class="my-rank-label">Your Quiz Rank</div>
                <div class="my-rank-name">{{ myQuizRank.name }}</div>
              </div>
              <div class="my-rank-stats">
                <span>#{{ myQuizRank.rank }}</span>
                <span>{{ myQuizRank.avg_score }}%</span>
                <span>{{ myQuizRank.quiz_xp }} XP</span>
              </div>
            </div>

            <div class="quiz-leader-list">
              <div v-for="leader in quizLeaders" :key="leader.user_id" class="quiz-leader-row" :class="{ me: isMyQuizRow(leader) }">
                <div class="ql-rank">#{{ leader.rank }}</div>
                <div class="ql-info">
                  <div class="ql-name">{{ leader.name }} <span v-if="isMyQuizRow(leader)">(You)</span></div>
                  <div class="ql-meta">{{ leader.attempts }} attempts - Best {{ leader.best_score }}%</div>
                </div>
                <div class="ql-stats">
                  <strong>{{ leader.avg_score }}%</strong>
                  <span>{{ leader.quiz_xp }} XP</span>
                </div>
              </div>
            </div>
          </template>

          <div v-else class="empty-state compact">
            <div class="icon">#</div>
            <h3>No quiz leaderboard data yet</h3>
            <p>Quiz submit korle ekhane rank automatically show hobe.</p>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue3-toastify'

import api from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import { getTimerForDifficulty, mergeRecentQuizzes, upsertRecentQuiz } from '@/utils/quizHistory'

const router = useRouter()
const generating = ref(false)
const loadingHistory = ref(false)
const loadingLeaderboard = ref(false)
const history = ref([])
const quizLeaders = ref([])
const myQuizRank = ref(null)
const usage = ref(null)
const QUIZ_LIMIT = 3

const languages = [
  { code: 'en', label: 'English' },
  { code: 'bn', label: 'Bangla' },
  { code: 'hi', label: 'Hindi' },
  { code: 'ur', label: 'Urdu' },
  { code: 'ar', label: 'Arabic' },
  { code: 'zh', label: 'Chinese' },
  { code: 'ja', label: 'Japanese' },
  { code: 'ko', label: 'Korean' },
  { code: 'ta', label: 'Tamil' },
  { code: 'th', label: 'Thai' },
  { code: 'id', label: 'Indonesian' },
  { code: 'ms', label: 'Malay' },
  { code: 'vi', label: 'Vietnamese' },
]

const form = ref({
  topic: '',
  subject: '',
  difficulty: 'intermediate',
  num_questions: 5,
  language: 'en',
})

const selectedTimer = computed(() => getTimerForDifficulty(form.value.difficulty))
const pageRefreshing = computed(() => loadingHistory.value || loadingLeaderboard.value)

function languageName(code) {
  return languages.find(language => language.code === code)?.label || code?.toUpperCase() || 'English'
}

function formatDate(value) {
  return new Date(value).toLocaleString()
}

function formatDifficulty(value) {
  return value ? value[0].toUpperCase() + value.slice(1) : 'Intermediate'
}

function scoreClass(score) {
  if (score >= 80) return 'exc'
  if (score >= 60) return 'good'
  return 'low'
}

function isMyQuizRow(leader) {
  return leader.user_id === myQuizRank.value?.user_id
}

function buildRouteQuiz(data) {
  return {
    result_id: data.result_id ?? data.id,
    topic: data.topic,
    difficulty: data.difficulty,
    language: data.language || form.value.language,
    total: data.total ?? data.total_q,
    questions: data.questions || [],
    time_per_question: data.time_per_question || getTimerForDifficulty(data.difficulty),
  }
}

async function loadPageData() {
  loadingHistory.value = true
  loadingLeaderboard.value = true
  try {
    const [historyResult, usageResult, leaderboardResult] = await Promise.allSettled([
      api.get('/quiz/history'),
      api.get('/amy/usage'),
      api.get('/quiz/leaderboard', { params: { limit: 5 } }),
    ])

    if (historyResult.status === 'fulfilled') {
      history.value = mergeRecentQuizzes(historyResult.value.data)
    } else {
      history.value = mergeRecentQuizzes([])
    }

    if (usageResult.status === 'fulfilled') {
      usage.value = usageResult.value.data
    }

    if (leaderboardResult.status === 'fulfilled') {
      quizLeaders.value = leaderboardResult.value.data.leaders || []
      myQuizRank.value = leaderboardResult.value.data.me || null
    } else {
      quizLeaders.value = []
      myQuizRank.value = null
    }
  } finally {
    loadingHistory.value = false
    loadingLeaderboard.value = false
  }
}

async function generateQuiz() {
  if (!form.value.topic.trim()) return

  generating.value = true
  try {
    const response = await api.post('/quiz/generate', form.value)
    const routeQuiz = buildRouteQuiz(response.data)

    upsertRecentQuiz({
      id: response.data.result_id,
      topic: response.data.topic,
      subject: form.value.subject,
      difficulty: response.data.difficulty,
      language: response.data.language,
      total_q: response.data.total,
      questions: response.data.questions,
      created_at: new Date().toISOString(),
      time_per_question: response.data.time_per_question,
      score: 0,
      xp_earned: 0,
    })

    toast.success('Quiz generated successfully')
    await router.push({
      path: `/quiz/${response.data.result_id}`,
      state: { quiz: routeQuiz },
    })
  } catch (error) {
    toast.error(error.response?.data?.detail || 'Failed to generate quiz')
  } finally {
    generating.value = false
  }
}

async function openRecentQuiz(quiz) {
  await router.push({
    path: `/quiz/${quiz.id}`,
    state: {
      quiz: buildRouteQuiz(quiz),
      submittedResult: quiz.score > 0
        ? (quiz.submitted_result || {
            score: quiz.score,
            correct: quiz.correct,
            total: quiz.total_q,
            xp_earned: quiz.xp_earned,
            passed: quiz.score >= 60,
            feedback: [],
          })
        : null,
    },
  })
}

onMounted(loadPageData)
</script>

<style scoped>
.quiz-page { display: flex; flex-direction: column; gap: 28px; }
.quiz-header h1 { margin-bottom: 4px; }
.quiz-header p { color: var(--text3); }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.form-full { grid-column: 1 / -1; }
.quiz-info-row { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.quiz-form-footer { display: flex; align-items: center; gap: 20px; flex-wrap: wrap; }
.usage-note { font-size: 13px; color: var(--text3); }
.usage-note a { color: var(--p); font-weight: 600; text-decoration: none; }
.quiz-grid { display: grid; grid-template-columns: minmax(0, 1.3fr) minmax(320px, 0.9fr); gap: 20px; align-items: start; }
.section-head { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 18px; }
.history-grid { display: grid; grid-template-columns: 1fr; gap: 16px; }
.history-card { padding: 16px; text-align: left; cursor: pointer; border: 1px solid var(--border); background: var(--bg2); }
.history-card:hover { border-color: var(--p); background: var(--p-soft); }
.hc-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 12px; }
.hc-topic { font-size: 15px; font-weight: 700; color: var(--text); }
.hc-meta { font-size: 12px; color: var(--text3); margin-top: 4px; }
.hc-score { font-size: 20px; font-weight: 800; flex-shrink: 0; }
.hc-score.exc { color: var(--green); }
.hc-score.good { color: var(--amber); }
.hc-score.low { color: var(--rose); }
.hc-tags { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }
.hc-footer { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.open-link { font-size: 12px; font-weight: 700; color: var(--p); }
.leaderboard-card { position: sticky; top: 12px; }
.my-quiz-rank { padding: 16px; margin-bottom: 14px; background: linear-gradient(180deg, rgba(123, 110, 246, 0.1), var(--bg2)); border: 1px solid var(--border); }
.my-rank-label { font-size: 11px; font-weight: 800; color: var(--text3); text-transform: uppercase; letter-spacing: .08em; }
.my-rank-name { font-size: 18px; font-weight: 800; color: var(--text); margin-top: 4px; }
.my-rank-stats { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 10px; font-size: 13px; font-weight: 700; color: var(--p); }
.quiz-leader-list { display: flex; flex-direction: column; gap: 10px; }
.quiz-leader-row { display: flex; align-items: center; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--border); }
.quiz-leader-row:last-child { border-bottom: 0; }
.quiz-leader-row.me { background: var(--p-soft); margin: 0 -12px; padding: 12px; border-radius: var(--r); border-bottom: 0; }
.ql-rank { width: 42px; font-size: 18px; font-weight: 900; color: var(--p); flex-shrink: 0; }
.ql-info { flex: 1; min-width: 0; }
.ql-name { font-size: 14px; font-weight: 700; color: var(--text); }
.ql-name span { color: var(--p); }
.ql-meta { font-size: 12px; color: var(--text3); margin-top: 3px; }
.ql-stats { display: flex; flex-direction: column; align-items: flex-end; gap: 4px; font-size: 12px; color: var(--text3); text-align: right; }
.ql-stats strong { font-size: 16px; color: var(--amber); }
.compact { min-height: 180px; }
@media (max-width: 1024px) {
  .quiz-grid { grid-template-columns: 1fr; }
  .leaderboard-card { position: static; }
}
@media (max-width: 768px) {
  .form-grid { grid-template-columns: 1fr; }
  .form-full { grid-column: auto; }
  .section-head { flex-direction: column; align-items: flex-start; }
}
</style>
