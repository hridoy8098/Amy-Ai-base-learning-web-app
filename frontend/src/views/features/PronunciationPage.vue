<template>
  <AppLayout>
    <div class="feature-page">
      <div class="feature-header">
        <h1>🎙️ Pronunciation Checker</h1>
        <p class="text-muted">Learn correct pronunciation for any English word or phrase</p>
      </div>
      <div class="pron-layout">
        <div class="card">
          <div class="pron-tabs tabs mb-4">
            <button class="tab" :class="{active:tab==='word'}" @click="tab='word'">Single Word</button>
            <button class="tab" :class="{active:tab==='phrase'}" @click="tab='phrase'">Phrase</button>
            <button class="tab" :class="{active:tab==='mistakes'}" @click="tab='mistakes'; loadMistakes()">Common Mistakes</button>
          </div>
          <div v-if="tab==='word'">
            <div class="flex gap-3">
              <input v-model="word" class="form-input flex-1" placeholder="Enter any English word (e.g. schedule, comfortable)..." @keyup.enter="checkWord" />
              <select v-model="language" class="form-input" style="width:auto">
                <option value="en">English</option>
                <option value="bn">বাংলা explanation</option>
              </select>
              <button class="btn btn-primary" @click="checkWord" :disabled="loading">
                <span class="spinner" v-if="loading"></span>
                <span v-else>Check →</span>
              </button>
            </div>
          </div>
          <div v-if="tab==='phrase'">
            <div class="flex gap-3">
              <input v-model="phrase" class="form-input flex-1" placeholder='Enter a phrase (e.g. "How are you doing?")...' @keyup.enter="checkPhrase" />
              <select v-model="accent" class="form-input" style="width:auto">
                <option value="american">🇺🇸 American</option>
                <option value="british">🇬🇧 British</option>
                <option value="australian">🇦🇺 Australian</option>
              </select>
              <button class="btn btn-primary" @click="checkPhrase" :disabled="loading">
                <span class="spinner" v-if="loading"></span><span v-else>Check →</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Word result -->
        <div class="card" v-if="tab==='word' && wordResult">
          <div class="pron-word-header">
            <h2>{{ wordResult.word }}</h2>
            <div class="pron-ipa">/{{ wordResult.ipa }}/</div>
          </div>
          <div class="pron-info-grid mt-4">
            <div class="pron-info-item"><span class="pi-label">Syllables</span><span class="pi-val">{{ wordResult.syllables }}</span></div>
            <div class="pron-info-item"><span class="pi-label">Stress</span><span class="pi-val">{{ wordResult.stress }}</span></div>
          </div>
          <div class="pron-audio mt-3 text-sm text-muted">🔊 {{ wordResult.audio_description }}</div>
          <div class="pron-section mt-4" v-if="wordResult.tips?.length">
            <h4 class="mb-2">💡 Tips</h4>
            <div v-for="t in wordResult.tips" :key="t" class="pron-tip">{{ t }}</div>
          </div>
          <div class="pron-section mt-4" v-if="wordResult.common_mistakes?.length">
            <h4 class="mb-2">⚠️ Common Mistakes</h4>
            <div v-for="m in wordResult.common_mistakes" :key="m" class="pron-mistake">{{ m }}</div>
          </div>
          <div class="pron-examples mt-4" v-if="wordResult.example_sentences?.length">
            <h4 class="mb-2">📝 Examples</h4>
            <div v-for="e in wordResult.example_sentences" :key="e" class="pron-example">"{{ e }}"</div>
          </div>
        </div>

        <!-- Phrase result -->
        <div class="card" v-if="tab==='phrase' && phraseResult">
          <h3 class="mb-4">"{{ phraseResult.phrase }}"</h3>
          <div class="wbw-grid" v-if="phraseResult.word_by_word?.length">
            <div v-for="w in phraseResult.word_by_word" :key="w.word" class="wbw-item">
              <div class="wbw-word">{{ w.word }}</div>
              <div class="wbw-ipa">/{{ w.ipa }}/</div>
              <div class="wbw-tip text-xs text-muted" v-if="w.tip">{{ w.tip }}</div>
            </div>
          </div>
          <div class="mt-4" v-if="phraseResult.connected_speech_tips?.length">
            <h4 class="mb-2">🔗 Connected Speech Tips</h4>
            <div v-for="t in phraseResult.connected_speech_tips" :key="t" class="pron-tip">{{ t }}</div>
          </div>
        </div>

        <!-- Common mistakes -->
        <div class="card" v-if="tab==='mistakes'">
          <h3 class="mb-4">⚠️ Common Bangladeshi Pronunciation Mistakes</h3>
          <div v-if="mistakesLoading" class="loading-state"><div class="spinner"></div></div>
          <div v-else v-for="m in commonMistakes" :key="m.bangladeshi_mistake" class="common-mistake-row">
            <div class="cm-issue">{{ m.bangladeshi_mistake }}</div>
            <div class="cm-example">Example: {{ m.example }}</div>
            <div class="cm-fix">✅ Fix: {{ m.fix }}</div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
<script setup>
import { ref } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { toast } from 'vue3-toastify'
import api from '@/api'
const tab=ref('word'); const word=ref(''); const phrase=ref(''); const accent=ref('american'); const language=ref('en')
const loading=ref(false); const wordResult=ref(null); const phraseResult=ref(null)
const commonMistakes=ref([]); const mistakesLoading=ref(false)
async function checkWord(){
  if(!word.value.trim())return
  loading.value=true;wordResult.value=null
  try{const r=await api.post('/pronunciation/word',{word:word.value,language:language.value});wordResult.value=r.data}
  catch{toast.error('Failed')}finally{loading.value=false}
}
async function checkPhrase(){
  if(!phrase.value.trim())return
  loading.value=true;phraseResult.value=null
  try{const r=await api.post('/pronunciation/phrase',{phrase:phrase.value,accent:accent.value,language:language.value});phraseResult.value=r.data}
  catch{toast.error('Failed')}finally{loading.value=false}
}
async function loadMistakes(){
  if(commonMistakes.value.length)return
  mistakesLoading.value=true
  try{const r=await api.get('/pronunciation/common-mistakes');commonMistakes.value=r.data.common_mistakes}
  catch{}finally{mistakesLoading.value=false}
}
</script>
<style scoped>
.pron-layout{display:flex;flex-direction:column;gap:16px}
.pron-word-header{display:flex;align-items:baseline;gap:14px}
.pron-word-header h2{font-size:2rem}
.pron-ipa{font-family:'JetBrains Mono',monospace;font-size:1.1rem;color:var(--p);background:var(--p-soft);padding:4px 12px;border-radius:var(--r)}
.pron-info-grid{display:flex;gap:16px;flex-wrap:wrap}
.pron-info-item{display:flex;flex-direction:column;gap:2px}
.pi-label{font-size:11px;text-transform:uppercase;color:var(--text3);font-family:'Outfit',sans-serif;letter-spacing:.06em}
.pi-val{font-size:15px;font-weight:700;color:var(--text)}
.pron-tip,.pron-mistake,.pron-example{font-size:13.5px;padding:6px 10px;border-radius:6px;margin-bottom:5px}
.pron-tip{background:rgba(0,201,167,.08);color:var(--teal)}
.pron-mistake{background:rgba(245,158,11,.08);color:var(--amber)}
.pron-example{background:var(--bg3);color:var(--text2);font-style:italic}
.wbw-grid{display:flex;flex-wrap:wrap;gap:10px}
.wbw-item{background:var(--bg3);border-radius:var(--r);padding:10px 14px;text-align:center;min-width:80px}
.wbw-word{font-weight:700;color:var(--text)}
.wbw-ipa{font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--p);margin-top:3px}
.wbw-tip{margin-top:3px}
.common-mistake-row{padding:14px;background:var(--bg3);border-radius:var(--r);margin-bottom:10px;border-left:3px solid var(--amber)}
.cm-issue{font-weight:600;color:var(--text);margin-bottom:4px}
.cm-example{font-size:13px;color:var(--text2);font-style:italic;margin-bottom:4px}
.cm-fix{font-size:13px;color:var(--green);font-weight:600}
</style>
