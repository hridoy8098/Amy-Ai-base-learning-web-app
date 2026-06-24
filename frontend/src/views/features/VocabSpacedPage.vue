<template>
  <AppLayout>
    <div class="feature-page">
      <div class="feature-header">
        <h1>📖 Vocabulary Review</h1>
        <p class="text-muted">Spaced repetition to master your saved vocabulary words</p>
      </div>
      <div class="vocab-stats" v-if="stats">
        <div class="stat-card card"><div class="stat-icon">📖</div><div class="stat-value">{{ stats.total_words }}</div><div class="stat-label">Total Words</div></div>
        <div class="stat-card card"><div class="stat-icon">📅</div><div class="stat-value">{{ stats.due_today }}</div><div class="stat-label">Due Today</div></div>
        <div class="stat-card card"><div class="stat-icon">✅</div><div class="stat-value">{{ stats.mastered }}</div><div class="stat-label">Mastered</div></div>
      </div>

      <!-- Review mode -->
      <div v-if="reviewMode && dueWords.length" class="card review-card">
        <div class="review-progress">
          <div class="rp-text">{{ currentIdx + 1 }} / {{ dueWords.length }}</div>
          <div class="progress-bar"><div class="progress-fill" :style="{width:((currentIdx)/dueWords.length*100)+'%'}"></div></div>
        </div>
        <div class="word-display">
          <div class="big-word">{{ currentWord.word }}</div>
          <div v-if="revealed">
            <div class="word-def">{{ currentWord.definition }}</div>
            <div class="word-ex text-sm text-muted" v-if="currentWord.example">"{{ currentWord.example }}"</div>
            <div class="review-btns">
              <button class="btn btn-danger" @click="rate(0)">😕 Forgot</button>
              <button class="btn btn-secondary" @click="rate(3)">🤔 Hard</button>
              <button class="btn btn-success" @click="rate(5)">✅ Got it!</button>
            </div>
          </div>
          <div v-else class="text-center mt-4">
            <button class="btn btn-primary" @click="revealed=true">Reveal Definition 👁️</button>
          </div>
        </div>
      </div>

      <div class="flex gap-3 mb-4">
        <button class="btn btn-primary" v-if="!reviewMode" @click="startReview" :disabled="!dueWords.length">Start Review Session ({{ dueWords.length }})</button>
        <button class="btn btn-outline" v-if="reviewMode" @click="reviewMode=false;currentIdx=0">End Session</button>
        <router-link to="/amy" class="btn btn-secondary">+ Save New Words via Amy</router-link>
      </div>

      <!-- Word list -->
      <div class="card" v-if="!reviewMode">
        <div class="flex justify-between items-center mb-4">
          <h3>All Saved Words ({{ words.length }})</h3>
          <input v-model="search" class="form-input" style="max-width:200px" placeholder="Search..." />
        </div>
        <div v-if="!filteredWords.length" class="empty-state"><div class="icon">📖</div><h3>No words saved</h3><p>Chat with Amy — she'll suggest words to save</p></div>
        <div v-else class="words-list">
          <div v-for="w in filteredWords" :key="w.id" class="word-row">
            <div class="wr-word">{{ w.word }}</div>
            <div class="wr-def">{{ w.definition }}</div>
            <div class="wr-ex text-xs text-muted" v-if="w.example">"{{ w.example }}"</div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { toast } from 'vue3-toastify'
import api from '@/api'
const words=ref([]); const dueWords=ref([]); const stats=ref(null)
const search=ref(''); const reviewMode=ref(false); const currentIdx=ref(0); const revealed=ref(false)
const currentWord=computed(()=>dueWords.value[currentIdx.value]||{})
const filteredWords=computed(()=>words.value.filter(w=>w.word.toLowerCase().includes(search.value.toLowerCase())||w.definition?.toLowerCase().includes(search.value.toLowerCase())))
function startReview(){reviewMode.value=true;currentIdx.value=0;revealed.value=false}
function rate(quality){
  toast.success(quality>=4?'Great!':quality>=2?'Keep practicing!':'Review again soon')
  if(currentIdx.value<dueWords.value.length-1){currentIdx.value++;revealed.value=false}
  else{reviewMode.value=false;toast.success('🎉 Review session complete!')}
}
async function load(){
  try{
    const[w,d,s]=await Promise.allSettled([api.get('/vocab-spaced/all'),api.get('/vocab-spaced/due'),api.get('/vocab-spaced/stats')])
    if(w.status==='fulfilled')words.value=w.value.data
    if(d.status==='fulfilled')dueWords.value=d.value.data.words||[]
    if(s.status==='fulfilled')stats.value=s.value.data
  }catch{}
}
onMounted(load)
</script>
<style scoped>
.vocab-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:20px}
.review-card{padding:28px;text-align:center}
.review-progress{margin-bottom:20px}
.rp-text{font-size:13px;color:var(--text3);margin-bottom:6px}
.big-word{font-family:'Outfit',sans-serif;font-size:2.5rem;font-weight:800;color:var(--p);margin-bottom:16px}
.word-def{font-size:16px;color:var(--text);margin-bottom:8px;padding:12px;background:var(--bg3);border-radius:var(--r)}
.word-ex{font-style:italic;margin-bottom:16px}
.review-btns{display:flex;gap:10px;justify-content:center;margin-top:16px}
.words-list{display:flex;flex-direction:column;gap:0}
.word-row{padding:12px 0;border-bottom:1px solid var(--border)}
.word-row:last-child{border-bottom:none}
.wr-word{font-size:15px;font-weight:700;color:var(--p);margin-bottom:3px}
.wr-def{font-size:13.5px;color:var(--text2);margin-bottom:2px}
</style>
