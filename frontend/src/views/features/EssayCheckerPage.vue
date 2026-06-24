<template>
  <AppLayout>
    <div class="feature-page">
      <div class="feature-header">
        <h1>📝 Essay Checker</h1>
        <p class="text-muted">AI checks your grammar, vocabulary, and coherence — get instant feedback</p>
      </div>

      <div class="ec-layout">
        <!-- Input -->
        <div class="card">
          <h3 class="mb-3">Your Text</h3>
          <textarea v-model="text" class="form-input essay-input"
            placeholder="Write or paste your paragraph/essay here... (minimum 20 characters)" rows="8"></textarea>
          <div class="ec-actions mt-3">
            <span class="text-xs text-muted">{{ text.length }} characters</span>
            <div class="flex gap-2">
              <select v-model="language" class="form-input" style="width:auto">
                <option value="en">English feedback</option>
                <option value="bn">বাংলা feedback</option>
              </select>
              <button class="btn btn-primary" @click="checkEssay" :disabled="loading || text.length < 20">
                <span class="spinner" v-if="loading"></span>
                <span v-else>Check Essay 🤖</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Results -->
        <div v-if="result">
          <!-- Score overview -->
          <div class="scores-row">
            <div class="score-card card" v-for="s in scores" :key="s.label">
              <div class="score-ring" :style="{background:`conic-gradient(${s.color} ${s.value*3.6}deg, var(--bg3) 0deg)`}">
                <div class="score-inner">{{ s.value }}</div>
              </div>
              <div class="score-label">{{ s.label }}</div>
            </div>
          </div>

          <!-- Grammar errors -->
          <div class="card" v-if="result.grammar_errors?.length">
            <h3 class="mb-3">❌ Grammar Errors ({{ result.grammar_errors.length }})</h3>
            <div v-for="e in result.grammar_errors" :key="e.original" class="error-item">
              <div class="error-original">❌ "{{ e.original }}"</div>
              <div class="error-arrow">→</div>
              <div class="error-correct">✅ "{{ e.correction }}"</div>
              <div class="error-exp text-xs text-muted mt-1">💡 {{ e.explanation }}</div>
            </div>
          </div>

          <!-- Corrected text -->
          <div class="card" v-if="result.corrected_text">
            <h3 class="mb-3">✅ Corrected Version</h3>
            <div class="corrected-text">{{ result.corrected_text }}</div>
          </div>

          <!-- Strengths / Improvements -->
          <div class="grid-2">
            <div class="card" v-if="result.strengths?.length">
              <h3 class="mb-3">💪 Strengths</h3>
              <div v-for="s in result.strengths" :key="s" class="strength-item">{{ s }}</div>
            </div>
            <div class="card" v-if="result.improvements?.length">
              <h3 class="mb-3">📈 Improvements</h3>
              <div v-for="i in result.improvements" :key="i" class="improvement-item">{{ i }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
<script setup>
import { ref, computed } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { toast } from 'vue3-toastify'
import api from '@/api'
const text=ref(''); const result=ref(null); const loading=ref(false); const language=ref('en')
const scores = computed(() => result.value ? [
  { label:'Overall',    value:result.value.overall_score||0,    color:'var(--p)' },
  { label:'Grammar',    value:result.value.grammar_score||0,    color:'var(--green)' },
  { label:'Vocabulary', value:result.value.vocabulary_score||0, color:'var(--teal)' },
  { label:'Coherence',  value:result.value.coherence_score||0,  color:'var(--amber)' },
] : [])
async function checkEssay(){
  if(text.value.length<20){toast.error('Write at least 20 characters');return}
  loading.value=true; result.value=null
  try{const r=await api.post('/essay/check',{text:text.value,language:language.value});result.value=r.data;toast.success('+5 XP earned!')}
  catch{toast.error('Check failed. Try again.')}finally{loading.value=false}
}
</script>
<style scoped>
.ec-layout{display:flex;flex-direction:column;gap:16px}
.essay-input{resize:vertical;min-height:200px;font-size:14px;line-height:1.7}
.ec-actions{display:flex;justify-content:space-between;align-items:center}
.scores-row{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
@media(max-width:640px){.scores-row{grid-template-columns:repeat(2,1fr)}}
.score-card{text-align:center;padding:20px 12px}
.score-ring{width:70px;height:70px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 10px}
.score-inner{width:54px;height:54px;border-radius:50%;background:var(--card);display:flex;align-items:center;justify-content:center;font-family:'Outfit',sans-serif;font-size:1.1rem;font-weight:800;color:var(--text)}
.score-label{font-size:12px;color:var(--text3);font-weight:600}
.error-item{padding:12px;background:rgba(244,63,94,.05);border:1px solid rgba(244,63,94,.15);border-radius:var(--r);margin-bottom:10px}
.error-original{font-size:13.5px;color:var(--rose);font-style:italic}
.error-arrow{color:var(--text3);margin:4px 0}
.error-correct{font-size:13.5px;color:var(--green);font-weight:600}
.corrected-text{background:var(--bg3);border-radius:var(--r);padding:16px;font-size:14px;line-height:1.8;white-space:pre-wrap;color:var(--text2)}
.strength-item{padding:8px 10px;background:rgba(16,185,129,.08);color:var(--green);border-radius:6px;font-size:13px;margin-bottom:6px}
.improvement-item{padding:8px 10px;background:rgba(245,158,11,.08);color:var(--amber);border-radius:6px;font-size:13px;margin-bottom:6px}
</style>
