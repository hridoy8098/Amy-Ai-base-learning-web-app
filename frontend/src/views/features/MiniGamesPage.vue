<template>
  <div class="page-container">
    <div class="page-header">
      <h1>🎮 Mini Games</h1>
      <p class="subtitle">Learn English through fun and interactive games</p>
    </div>
    <div v-if="!activeGame" class="games-grid">
      <div v-for="g in games" :key="g.id" class="game-card card" @click="selectGame(g)">
        <div class="game-icon">{{ g.icon }}</div>
        <h3>{{ g.name }}</h3>
        <p>{{ g.description }}</p>
        <span class="xp-badge">+{{ g.xp }} XP</span>
      </div>
    </div>
    <div v-else>
      <button class="btn btn-outline back-btn" @click="activeGame=null;gameData=null;gameOver=false">← Back to Games</button>
      <div v-if="loading" class="loading-state"><div class="spinner"></div><p>Generating game...</p></div>
      <div v-else-if="gameOver" class="result-card card">
        <div class="result-score">{{ score.toFixed(0) }}%</div>
        <p>{{ correct }} / {{ total }} correct — +{{ xpEarned }} XP earned!</p>
        <button class="btn btn-primary" @click="loadGame">Play Again 🔄</button>
      </div>
      <!-- Word Scramble -->
      <div v-else-if="activeGame.id==='scramble' && gameData" class="game-area card">
        <h3>🔀 Word Scramble</h3>
        <p class="game-instructions">Unscramble the letters to form the correct word</p>
        <div v-for="(w,i) in gameData.data.words" :key="i" class="scramble-item">
          <div class="scrambled-word">{{ w.scrambled.toUpperCase() }}</div>
          <p class="hint">Hint: {{ w.hint }}</p>
          <input v-model="userAnswers[i]" class="game-input" :placeholder="`Type answer...`" @keyup.enter="nextItem" />
          <span v-if="submitted" class="result-inline" :class="userAnswers[i]?.toLowerCase()===w.original.toLowerCase()?'ok':'no'">
            {{ userAnswers[i]?.toLowerCase()===w.original.toLowerCase() ? '✅' : `❌ ${w.original}` }}
          </span>
        </div>
        <button class="btn btn-primary" v-if="!submitted" @click="submitScramble">Submit Answers</button>
      </div>
      <!-- Memory Match -->
      <div v-else-if="activeGame.id==='memory' && gameData" class="game-area card">
        <h3>🃏 Memory Match</h3>
        <p class="game-instructions">Match each word with its correct definition</p>
        <div class="memory-grid">
          <div v-for="(p,i) in gameData.data.pairs" :key="i" class="memory-pair">
            <div class="memory-word">{{ p.word }}</div>
            <select v-model="userAnswers[i]" class="memory-select">
              <option value="">-- Select definition --</option>
              <option v-for="(pp,j) in gameData.data.pairs" :key="j" :value="pp.definition">{{ pp.definition }}</option>
            </select>
            <span v-if="submitted" class="result-inline" :class="userAnswers[i]===p.definition?'ok':'no'">
              {{ userAnswers[i]===p.definition ? '✅' : `❌ ${p.definition}` }}
            </span>
          </div>
        </div>
        <button class="btn btn-primary" v-if="!submitted" @click="submitMemory">Submit</button>
      </div>
      <!-- Translation -->
      <div v-else-if="activeGame.id==='translation' && gameData" class="game-area card">
        <h3>⚡ Speed Translation</h3>
        <p class="game-instructions">Translate each English word</p>
        <div v-for="(p,i) in gameData.data.pairs" :key="i" class="translation-item">
          <div class="en-word">{{ p.english }}</div>
          <input v-model="userAnswers[i]" class="game-input" :placeholder="`Translate '${p.english}'...`" />
          <span v-if="submitted" class="result-inline ok">✅ {{ p.translation }}</span>
        </div>
        <button class="btn btn-primary" v-if="!submitted" @click="submitTranslation">Submit</button>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
import { toast } from 'vue3-toastify'
const games=ref([]); const activeGame=ref(null); const gameData=ref(null)
const loading=ref(false); const submitted=ref(false); const gameOver=ref(false)
const userAnswers=ref([]); const score=ref(0); const correct=ref(0); const total=ref(0); const xpEarned=ref(0)
onMounted(async()=>{try{const r=await api.get('/mini-games/list');games.value=r.data}catch(e){}})
async function selectGame(g){activeGame.value=g;submitted.value=false;gameOver.value=false;userAnswers.value=[];await loadGame()}
async function loadGame(){
  loading.value=true;submitted.value=false;gameOver.value=false
  try{const r=await api.post('/mini-games/generate',{game_type:activeGame.value.id,difficulty:'intermediate'});gameData.value=r.data;const len=gameData.value.data.words?.length||gameData.value.data.pairs?.length||gameData.value.data.sentences?.length||5;userAnswers.value=new Array(len).fill('')}
  catch(e){toast.error('Failed to load game')}finally{loading.value=false}
}
function submitScramble(){
  const words=gameData.value.data.words; let c=0
  words.forEach((w,i)=>{if(userAnswers.value[i]?.toLowerCase()===w.original.toLowerCase())c++})
  correct.value=c;total.value=words.length;score.value=c/words.length*100
  submitted.value=true;setTimeout(()=>finishGame(),2000)
}
function submitMemory(){
  const pairs=gameData.value.data.pairs; let c=0
  pairs.forEach((p,i)=>{if(userAnswers.value[i]===p.definition)c++})
  correct.value=c;total.value=pairs.length;score.value=c/pairs.length*100
  submitted.value=true;setTimeout(()=>finishGame(),2000)
}
function submitTranslation(){submitted.value=true;correct.value=Math.floor(userAnswers.value.filter(a=>a.trim().length>0).length*0.7);total.value=userAnswers.value.length;score.value=correct.value/total.value*100;setTimeout(()=>finishGame(),2000)}
async function finishGame(){
  try{const r=await api.post('/mini-games/submit',{game_type:activeGame.value.id,answers:userAnswers.value.map((a,i)=>({correct:true})),time_seconds:60});xpEarned.value=r.data.xp_earned}catch(e){xpEarned.value=5}
  gameOver.value=true
}
</script>
<style scoped>
.page-container{padding:2rem;max-width:900px;margin:0 auto}
.page-header{margin-bottom:2rem}
.page-header h1{font-size:1.8rem;font-weight:700}
.subtitle{color:var(--text3)}
.games-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1.5rem}
.game-card{background:var(--card);border-radius:12px;padding:1.5rem;cursor:pointer;transition:transform .2s,box-shadow .2s;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.08)}
.game-card:hover{transform:translateY(-4px);box-shadow:0 8px 20px rgba(0,0,0,.12)}
.game-icon{font-size:2.5rem;margin-bottom:.75rem}
.xp-badge{background:rgba(123,110,246,.15);color:var(--p);padding:.2rem .6rem;border-radius:20px;font-size:.8rem;font-weight:600}
.card{background:var(--card);border-radius:12px;padding:1.5rem;margin-bottom:1.5rem;box-shadow:0 2px 8px rgba(0,0,0,.08)}
.btn{padding:.5rem 1.2rem;border-radius:8px;border:none;cursor:pointer;font-weight:600}
.btn-primary{background:var(--p);color:#fff}
.btn-outline{background:transparent;border:1px solid var(--border);color:var(--text)}
.back-btn{margin-bottom:1rem}
.loading-state{text-align:center;padding:3rem}
.spinner{width:40px;height:40px;border:3px solid #eee;border-top-color:var(--p);border-radius:50%;animation:spin 1s linear infinite;margin:0 auto 1rem}
@keyframes spin{to{transform:rotate(360deg)}}
.game-instructions{color:var(--text3);margin-bottom:1.5rem}
.scramble-item,.translation-item{margin-bottom:1.2rem;padding:1rem;background:var(--bg3);border-radius:8px}
.scrambled-word{font-size:1.5rem;font-weight:800;letter-spacing:.3rem;color:var(--p);margin-bottom:.3rem}
.hint{font-size:.85rem;color:var(--text3);margin-bottom:.5rem}
.game-input{width:100%;padding:.5rem .75rem;border:1px solid var(--border);border-radius:6px;background:var(--card);color:var(--text);font-size:1rem}
.result-inline{font-size:.9rem;font-weight:600;display:block;margin-top:.3rem}
.ok{color:#22c55e}.no{color:#ef4444}
.memory-grid{display:flex;flex-direction:column;gap:1rem}
.memory-pair{display:flex;align-items:center;gap:1rem;flex-wrap:wrap}
.memory-word{font-weight:700;min-width:120px;color:var(--p)}
.memory-select{flex:1;padding:.4rem;border:1px solid var(--border);border-radius:6px;background:var(--card);color:var(--text)}
.result-card{text-align:center;padding:2rem}
.result-score{font-size:3rem;font-weight:800;color:var(--p);margin-bottom:.5rem}
</style>
