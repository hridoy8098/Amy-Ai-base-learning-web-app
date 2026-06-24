<template>
  <AppLayout>
    <div class="feature-page">
      <div class="feature-header">
        <h1>💼 Industry-Specific English</h1>
        <p class="text-muted">Medical, Legal, IT, Business — master specialized English for your career</p>
      </div>

      <div v-if="!selected">
        <div class="industry-grid">
          <div v-for="ind in industries" :key="ind.id" class="industry-card card card-hover" @click="selectIndustry(ind)">
            <div class="ind-icon">{{ ind.icon }}</div>
            <h3>{{ ind.name }}</h3>
            <p class="text-sm text-muted">{{ ind.description }}</p>
            <div class="ind-arrow">→</div>
          </div>
        </div>
      </div>

      <div v-else>
        <div class="flex items-center gap-3 mb-6">
          <button class="btn btn-outline btn-sm" @click="selected=null;lesson=null">← Back</button>
          <h2>{{ selected.icon }} {{ selected.name }}</h2>
        </div>

        <!-- Topics -->
        <div class="card mb-4" v-if="!lesson">
          <h3 class="mb-4">Choose a Topic</h3>
          <div class="topics-grid">
            <button v-for="t in topics" :key="t" class="topic-btn" :class="{active:activeTopic===t}" @click="activeTopic=t">{{ t }}</button>
          </div>
          <div class="flex gap-3 mt-4">
            <select v-model="difficulty" class="form-input" style="max-width:160px">
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
            <select v-model="lang" class="form-input" style="max-width:160px">
              <option value="en">English only</option>
              <option value="bn">বাংলা সহ</option>
            </select>
            <button class="btn btn-primary" @click="loadLesson" :disabled="loading">
              <span class="spinner" v-if="loading"></span>
              <span v-else>Generate Lesson 🤖</span>
            </button>
          </div>
        </div>

        <!-- Lesson Content -->
        <div v-if="lesson">
          <button class="btn btn-outline btn-sm mb-4" @click="lesson=null">← Choose Another Topic</button>
          <div class="lesson-layout">
            <div class="card lesson-main">
              <h2 class="mb-2">{{ lesson.title }}</h2>
              <p class="mb-5">{{ lesson.introduction }}</p>

              <div v-if="lesson.key_terms?.length" class="mb-5">
                <h3 class="mb-3">📚 Key Terms</h3>
                <div v-for="t in lesson.key_terms" :key="t.term" class="term-card">
                  <div class="term-word">{{ t.term }}</div>
                  <div class="term-def">{{ t.definition }}</div>
                  <div class="term-ex text-xs text-muted" v-if="t.example_sentence">💬 "{{ t.example_sentence }}"</div>
                </div>
              </div>

              <div v-if="lesson.common_phrases?.length" class="mb-5">
                <h3 class="mb-3">💬 Common Phrases</h3>
                <div v-for="p in lesson.common_phrases" :key="p.phrase" class="phrase-card">
                  <div class="phrase-text">"{{ p.phrase }}"</div>
                  <div class="phrase-usage text-xs text-muted">{{ p.context }}</div>
                </div>
              </div>

              <div v-if="lesson.sample_dialogue?.length" class="mb-5">
                <h3 class="mb-3">🗣️ Sample Dialogue</h3>
                <div class="dialogue-box">
                  <div v-for="line in lesson.sample_dialogue" :key="line.line" class="dialogue-line" :class="line.speaker==='A'?'speaker-a':'speaker-b'">
                    <span class="speaker-label">{{ line.speaker }}</span>
                    <span class="speaker-line">{{ line.line }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="lesson-side">
              <div class="card" v-if="lesson.pro_tips?.length">
                <h4 class="mb-3">⭐ Pro Tips</h4>
                <div v-for="tip in lesson.pro_tips" :key="tip" class="tip-item">{{ tip }}</div>
              </div>
              <div class="card mt-4" v-if="lesson.practice_exercise?.scenario">
                <h4 class="mb-2">✍️ Practice Exercise</h4>
                <p class="text-sm">{{ lesson.practice_exercise.instructions }}</p>
                <div class="exercise-scenario">{{ lesson.practice_exercise.scenario }}</div>
                <div class="mt-2" v-if="lesson.practice_exercise.hints?.length">
                  <div v-for="h in lesson.practice_exercise.hints" :key="h" class="hint-item">💡 {{ h }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { toast } from 'vue3-toastify'
import api from '@/api'
const industries=ref([]); const selected=ref(null); const topics=ref([]); const lesson=ref(null)
const loading=ref(false); const activeTopic=ref(''); const difficulty=ref('intermediate'); const lang=ref('en')
async function selectIndustry(ind){
  selected.value=ind; lesson.value=null
  try{const r=await api.get(`/industry/${ind.id}/topics`);topics.value=r.data.topics;activeTopic.value=topics.value[0]}catch{}
}
async function loadLesson(){
  loading.value=true
  try{const r=await api.post('/industry/lesson',{industry_id:selected.value.id,topic:activeTopic.value,difficulty:difficulty.value,language:lang.value});lesson.value=r.data.lesson;toast.success('+15 XP earned!')}
  catch{toast.error('Failed to load lesson')}finally{loading.value=false}
}
onMounted(async()=>{try{const r=await api.get('/industry/industries');industries.value=r.data}catch{}})
</script>
<style scoped>
.industry-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px}
.industry-card{text-align:center;padding:28px 16px;cursor:pointer;position:relative}
.ind-icon{font-size:2.5rem;margin-bottom:10px}
.ind-arrow{position:absolute;bottom:14px;right:16px;font-size:18px;color:var(--p);opacity:0;transition:opacity var(--t)}
.industry-card:hover .ind-arrow{opacity:1}
.topics-grid{display:flex;flex-wrap:wrap;gap:8px}
.topic-btn{padding:6px 14px;border-radius:99px;border:1.5px solid var(--border);background:transparent;color:var(--text2);font-size:13px;cursor:pointer;transition:all var(--t);font-family:'DM Sans',sans-serif}
.topic-btn:hover,.topic-btn.active{border-color:var(--p);background:var(--p-soft);color:var(--p)}
.lesson-layout{display:grid;grid-template-columns:1fr 280px;gap:16px}
@media(max-width:768px){.lesson-layout{grid-template-columns:1fr}}
.term-card{padding:12px;background:var(--bg3);border-radius:var(--r);margin-bottom:8px;border-left:3px solid var(--p)}
.term-word{font-weight:700;color:var(--p);margin-bottom:3px}
.term-def{font-size:13.5px;color:var(--text2)}
.term-ex{margin-top:4px;font-style:italic}
.phrase-card{padding:10px 14px;background:var(--p-soft);border-radius:var(--r);margin-bottom:8px}
.phrase-text{font-style:italic;font-weight:600;color:var(--text);margin-bottom:3px}
.dialogue-box{background:var(--bg3);border-radius:var(--r2);padding:14px;display:flex;flex-direction:column;gap:10px}
.dialogue-line{display:flex;gap:10px;align-items:flex-start}
.speaker-label{font-weight:800;font-family:'Outfit',sans-serif;min-width:20px;color:var(--p)}
.speaker-b .speaker-label{color:var(--teal)}
.speaker-line{font-size:14px}
.tip-item{padding:8px 10px;background:var(--bg3);border-radius:var(--r);font-size:13px;margin-bottom:6px;color:var(--text2)}
.exercise-scenario{margin-top:8px;padding:10px;background:var(--p-soft);border-radius:var(--r);font-size:13px;font-style:italic;color:var(--text)}
.hint-item{font-size:12px;color:var(--text3);margin-top:4px}
</style>
