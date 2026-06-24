<template>
  <AppLayout>
    <div class="feature-page">
      <div class="feature-header">
        <h1>{{ meta.icon }} {{ meta.title }}</h1>
        <p class="text-muted">{{ meta.desc }}</p>
      </div>
      <div v-if="loading" class="loading-state"><div class="spinner spinner-lg"></div><p>Loading...</p></div>
      <div v-else>
        <!-- Quick action -->
        <div class="card mb-4">
          <div class="flex items-center gap-4">
            <div class="qa-icon">{{ meta.icon }}</div>
            <div class="flex-1">
              <h3>{{ meta.title }}</h3>
              <p class="text-sm text-muted">{{ meta.desc }}</p>
            </div>
            <button class="btn btn-primary" @click="loadData" :disabled="fetching">
              <span class="spinner" v-if="fetching"></span>
              <span v-else>{{ meta.action }}</span>
            </button>
          </div>
        </div>
        <!-- Data display -->
        <div v-if="data" class="card">
          <h3 class="mb-3">Response</h3>
          <div class="data-grid">
            <template v-if="Array.isArray(data)">
              <div v-for="(item, i) in data" :key="i" class="data-item">
                <span class="data-icon" v-if="item.icon">{{ item.icon }}</span>
                <div>
                  <div class="data-name">{{ item.name || item.word || item.title || item.skill_name || JSON.stringify(item).slice(0,60) }}</div>
                  <div class="data-desc text-xs text-muted">{{ item.description || item.definition || item.desc || '' }}</div>
                </div>
              </div>
            </template>
            <template v-else>
              <div v-for="(val, key) in data" :key="key" class="data-kv">
                <span class="kv-key">{{ key }}</span>
                <span class="kv-val">{{ typeof val === 'object' ? JSON.stringify(val).slice(0,80)+'...' : val }}</span>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
<script setup>
import { ref, onMounted, computed } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import api from '@/api'
const loading = ref(false); const fetching = ref(false); const data = ref(null)
const metaMap = {
  AmyMemoryPage:     { icon:'💭', title:'Amy Memory System', desc:'Amy remembers your conversations for a personal touch', action:'View My Memories', endpoint:'/amy-memory/', method:'get' },
  FluencyPage:       { icon:'📊', title:'Fluency Score',     desc:'Track your English fluency progress over time',        action:'View History',     endpoint:'/fluency/history', method:'get' },
  NewsLearningPage:  { icon:'📰', title:'News Learning',     desc:'Learn English from BBC/CNN style headlines',            action:'Browse Topics',    endpoint:'/news-learning/topics', method:'get' },
  SongLearningPage:  { icon:'🎵', title:'Song Learning',     desc:'Learn English through popular song themes',            action:'Browse Songs',     endpoint:'/song-learning/songs', method:'get' },
  SleepLearningPage: { icon:'🌙', title:'Sleep Learning',    desc:'Bedtime recap to reinforce your daily learning',       action:'Get Tonight\'s Recap', endpoint:'/sleep-learning/recap', method:'get' },
  PronunciationPage: { icon:'🎙️', title:'Pronunciation',     desc:'Learn correct pronunciation for any English word',     action:'Common Mistakes',  endpoint:'/pronunciation/common-mistakes', method:'get' },
  EssayCheckerPage:  { icon:'📝', title:'Essay Checker',     desc:'AI checks grammar, vocabulary and coherence',          action:'Check Essay',      endpoint:null, method:'post' },
  MicroCertPage:     { icon:'📜', title:'Micro Certificates',desc:'Earn skill badges and share on LinkedIn',             action:'View All Skills',  endpoint:'/micro-cert/skills', method:'get' },
  CodingInterviewPage:{ icon:'👨‍💻', title:'Coding Interview', desc:'Practice English for technical job interviews',      action:'Browse Topics',    endpoint:'/coding-interview/topics', method:'get' },
  AccentTrainingPage:{ icon:'🌍', title:'Accent Training',   desc:'Practice British, American, Australian accents',       action:'Choose Accent',    endpoint:'/accent/accents', method:'get' },
  LearningStylePage: { icon:'🧬', title:'Learning Style',    desc:'Detect if you are visual, auditory or reading learner',action:'Detect My Style',  endpoint:'/learning-style/detect', method:'get' },
  CulturalContextPage:{ icon:'🌐', title:'Cultural Context', desc:'Learn English-speaking culture alongside grammar',     action:'Browse Topics',    endpoint:'/cultural/topics', method:'get' },
  VocabSpacedPage:   { icon:'📖', title:'Vocabulary Review', desc:'Spaced repetition to master your saved words',        action:'Review Words',     endpoint:'/vocab-spaced/all', method:'get' },
  RemindersPage:     { icon:'📅', title:'Smart Reminders',   desc:'Set personalized study schedule reminders',           action:'My Reminders',     endpoint:'/reminders/', method:'get' },
  LearningPathPage:  { icon:'🗺️', title:'Learning Path',     desc:'AI-powered personalized course recommendations',      action:'Get My Path',      endpoint:'/learning-path/', method:'get' },
}
const meta = computed(() => metaMap['CulturalContextPage'] || { icon:'✨', title:'CulturalContextPage', desc:'', action:'Load', endpoint:null })
async function loadData() {
  if (!meta.value.endpoint) return
  fetching.value = true
  try { const r = await api.get(meta.value.endpoint); data.value = r.data }
  catch(e) { data.value = { error: 'Failed to load data. Please try again.' } }
  finally { fetching.value = false }
}
onMounted(loadData)
</script>
<style scoped>
.qa-icon { font-size: 2.5rem; flex-shrink: 0; }
.data-grid { display: flex; flex-direction: column; gap: 10px; }
.data-item { display: flex; align-items: center; gap: 12px; padding: 10px 12px; background: var(--bg3); border-radius: var(--r); }
.data-icon { font-size: 1.4rem; flex-shrink: 0; }
.data-name { font-size: 14px; font-weight: 600; color: var(--text); }
.data-desc { margin-top: 2px; }
.data-kv { display: flex; gap: 12px; padding: 8px 0; border-bottom: 1px solid var(--border); font-size: 13.5px; }
.data-kv:last-child { border-bottom: none; }
.kv-key { font-weight: 600; color: var(--p); min-width: 140px; flex-shrink: 0; font-family: 'JetBrains Mono', monospace; font-size: 12px; }
.kv-val { color: var(--text2); word-break: break-all; }
</style>
