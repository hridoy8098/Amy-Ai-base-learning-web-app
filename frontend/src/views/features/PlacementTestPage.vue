<template>
  <div class="page-container">
    <div class="page-header">
      <h1>🧪 Placement Test</h1>
      <p class="subtitle">Find your English level and get the perfect course recommendations</p>
    </div>
    <div v-if="!started && !result" class="intro-card card">
      <div class="intro-icon">🎯</div>
      <h2>Discover Your Level</h2>
      <p>Answer {{ questions.length || 10 }} questions to find your exact English level and unlock the right learning path.</p>
      <div class="levels-grid">
        <div v-for="l in levels" :key="l.name" class="level-item">
          <span class="level-icon">{{ l.icon }}</span>
          <span>{{ l.name }}</span>
        </div>
      </div>
      <button class="btn btn-primary" :disabled="loadingQuestions" @click="start">
        {{ loadingQuestions ? 'Loading...' : 'Start Placement Test →' }}
      </button>
      <button class="btn btn-outline" @click="goToGame" style="margin-top: 1rem;">
        Skip to Skill Path
      </button>
    </div>
    <div v-else-if="started && !result" class="test-area">
      <div class="loading-message" v-if="loadingQuestions">
        <p>Preparing your placement questions...</p>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" :style="{width: ((currentQ+1)/questions.length*100)+'%'}"></div>
      </div>
      <p class="progress-text">Question {{ currentQ+1 }} of {{ questions.length }} — <span class="level-tag">{{ questions[currentQ]?.level }}</span></p>
      <div class="card question-card">
        <h3>{{ questions[currentQ]?.question }}</h3>
        <div class="options">
          <button v-for="(opt,i) in questions[currentQ]?.options" :key="i"
            class="option-btn" :class="{selected: answers[currentQ]===i}"
            @click="answers[currentQ]=i">
            <span class="opt-letter">{{ String.fromCharCode(65+i) }}</span> {{ opt }}
          </button>
        </div>
        <div class="nav-btns">
          <button class="btn btn-outline" v-if="currentQ>0" @click="currentQ--">← Back</button>
          <button class="btn btn-primary" v-if="currentQ<questions.length-1" :disabled="answers[currentQ]===undefined" @click="currentQ++">Next →</button>
          <button class="btn btn-success" v-if="currentQ===questions.length-1" :disabled="answers[currentQ]===undefined || submitting" @click="submit">{{ submitting ? 'Evaluating...' : 'Submit Test ✓' }}</button>
        </div>
      </div>
    </div>
    <div v-else-if="result" class="result-area">
      <div class="result-card card">
        <div class="result-score">{{ result.score }}%</div>
        <h2 class="result-level">{{ result.level_assigned.toUpperCase() }}</h2>
        <p>{{ result.message }}</p>
        <div class="result-stats">
          <div class="stat"><span class="stat-val">{{ result.correct }}</span><span class="stat-lbl">Correct</span></div>
          <div class="stat"><span class="stat-val">{{ result.total }}</span><span class="stat-lbl">Total</span></div>
          <div class="stat"><span class="stat-val">+{{ result.xp_earned }}</span><span class="stat-lbl">XP Earned</span></div>
        </div>
        <div class="result-actions">
        <button @click="goToCourses" class="btn btn-primary">View Recommended Courses →</button>
        <button @click="goToGame" class="btn btn-outline" style="margin-left:1rem;">Go to Game Path</button>
      </div>
      </div>
      <div class="card">
        <h3>Question Review</h3>
        <div v-for="r in result.results" :key="r.question_id" class="review-item" :class="r.is_correct ? 'correct' : 'wrong'">
          <div class="review-header">
            <span>{{ r.is_correct ? '✅' : '❌' }} Q{{ r.question_id }} ({{ r.level }})</span>
          </div>
          <p class="your-ans">Your answer: <strong>{{ r.your_answer }}</strong></p>
          <p v-if="!r.is_correct" class="correct-ans">Correct: <strong>{{ r.correct_answer }}</strong></p>
          <p class="explanation">💡 {{ r.explanation }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'
import { toast } from 'vue3-toastify'

const router = useRouter()
const started = ref(false)
const result = ref(null)
const submitting = ref(false)
const loadingQuestions = ref(false)
const currentQ = ref(0)
const questions = ref([])
const answers = ref([])
const levels = [
  { icon: '🌱', name: 'Beginner' },
  { icon: '📗', name: 'Elementary' },
  { icon: '📘', name: 'Intermediate' },
  { icon: '📙', name: 'Upper-Int' },
  { icon: '🏆', name: 'Advanced' }
]

async function start() {
  loadingQuestions.value = true
  try {
    const r = await api.get('/placement/questions-public')
    questions.value = r.data.questions || []
    if (!questions.value.length) {
      throw new Error('No placement questions available')
    }
    answers.value = new Array(questions.value.length).fill(undefined)
    currentQ.value = 0
    started.value = true
  } catch (e) {
    console.error(e)
    toast.error('Failed to load placement questions: ' + (e.response?.data?.detail || e.message))
  } finally {
    loadingQuestions.value = false
  }
}

async function submit() {
  if (!questions.value.length) return
  submitting.value = true
  try {
    const r = await api.post('/placement/submit-simple', {
      answers: answers.value.map(a => a ?? 0)
    })
    result.value = r.data
    toast.success('Placement test completed!')
  } catch (e) {
    console.error(e)
    toast.error('Submission failed: ' + (e.response?.data?.detail || e.message))
  } finally {
    submitting.value = false
  }
}

function restart() {
  started.value = false
  result.value = null
  currentQ.value = 0
  questions.value = []
  answers.value = []
}

function goToCourses() {
  const level = result.value?.recommended_course_level || 'beginner'
  router.push(`/courses?level=${encodeURIComponent(level)}`)
}

function goToGame() {
  router.push('/game')
}
</script>
<style scoped>
.page-container{padding:2rem;max-width:800px;margin:0 auto}
.page-header{margin-bottom:2rem}
.page-header h1{font-size:1.8rem;font-weight:700}
.subtitle{color:var(--text3)}
.card{background:var(--card);border-radius:12px;padding:1.5rem;margin-bottom:1.5rem;box-shadow:0 2px 8px rgba(0,0,0,.08)}
.intro-card{text-align:center}
.intro-icon{font-size:3rem;margin-bottom:1rem}
.levels-grid{display:flex;justify-content:center;gap:1rem;flex-wrap:wrap;margin:1.5rem 0}
.level-item{display:flex;flex-direction:column;align-items:center;gap:.3rem;font-size:.85rem}
.level-icon{font-size:1.5rem}
.btn{padding:.5rem 1.2rem;border-radius:8px;border:none;cursor:pointer;font-weight:600;transition:opacity .2s}
.btn-primary{background:var(--p);color:#fff}
.btn-outline{background:transparent;border:1px solid var(--border);color:var(--text)}
.btn-success{background:#22c55e;color:#fff}
.btn:disabled{opacity:.5;cursor:not-allowed}
.progress-bar{height:6px;background:var(--border);border-radius:3px;margin-bottom:.75rem}
.progress-fill{height:100%;background:var(--p);border-radius:3px;transition:width .3s}
.progress-text{font-size:.9rem;color:var(--text3);margin-bottom:1rem}
.level-tag{background:var(--p);color:#fff;padding:.1rem .5rem;border-radius:10px;font-size:.8rem}
.question-card h3{font-size:1.1rem;margin-bottom:1.2rem}
.options{display:flex;flex-direction:column;gap:.6rem;margin-bottom:1.5rem}
.option-btn{display:flex;align-items:center;gap:.75rem;padding:.75rem 1rem;border:2px solid var(--border);border-radius:8px;background:var(--card);cursor:pointer;text-align:left;transition:all .2s}
.option-btn.selected{border-color:var(--p);background:rgba(123,110,246,.08)}
.opt-letter{width:24px;height:24px;border-radius:50%;background:var(--bg3);display:flex;align-items:center;justify-content:center;font-size:.8rem;font-weight:700;flex-shrink:0}
.nav-btns{display:flex;gap:1rem;justify-content:flex-end}
.result-card{text-align:center}
.result-score{font-size:3rem;font-weight:800;color:var(--p)}
.result-level{font-size:1.5rem;margin:.5rem 0}
.result-stats{display:flex;justify-content:center;gap:2rem;margin:1.5rem 0}
.stat{display:flex;flex-direction:column;align-items:center}
.stat-val{font-size:1.5rem;font-weight:700;color:var(--p)}
.stat-lbl{font-size:.8rem;color:var(--text3)}
.review-item{padding:1rem;border-radius:8px;margin-bottom:.75rem}
.correct{background:rgba(34,197,94,.08);border-left:3px solid #22c55e}
.wrong{background:rgba(239,68,68,.08);border-left:3px solid #ef4444}
.your-ans,.correct-ans,.explanation{font-size:.9rem;margin:.2rem 0}
.explanation{color:var(--text3);font-style:italic}
</style>
