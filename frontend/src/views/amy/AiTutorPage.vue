<template>
  <AppLayout>
    <div class="amy-page">

      <!-- Voice overlay (separate component) -->
      <AmyVoiceOverlay
        :open="voiceOverlayOpen"
        :phase="voicePhase"
        :lang="voiceLang"
        :transcript="voiceTranscript"
        :last-reply="voiceLastReply"
        v-bind="voiceAnimProps"
        @close="closeVoiceOverlay"
        @lang="v => voiceLang = v"
      />

      <!-- ── HEADER ─────────────────────────────────────────────── -->
      <div class="amy-header">
        <div class="amy-identity">
          <AmyRobot
            :size="82"
            :mood="currentMood"
            :is-speaking="isSpeaking"
            :is-loading="isLoading"
            v-bind="headerAnimProps"
          />
          <div class="amy-info">
            <div class="amy-name">Amy <span class="amy-badge">AI Tutor</span></div>
            <div class="amy-status">
              <span class="status-dot" :class="isLoading ? 'thinking' : 'online'"></span>
              {{ statusText }}
            </div>
            <div class="emotion-pill" v-if="detectedEmotion">{{ detectedEmotion }}</div>
          </div>
        </div>

        <div class="amy-right">
          <!-- Language -->
          <div class="lang-toggle">
            <button :class="['lang-btn', voiceLang === 'en-US' ? 'active' : '']" @click="voiceLang = 'en-US'">🇬🇧 EN</button>
            <button :class="['lang-btn', voiceLang === 'bn-BD' ? 'active' : '']" @click="voiceLang = 'bn-BD'">🇧🇩 বাং</button>
          </div>
          <!-- Mode tabs -->
          <div class="mode-tabs">
            <button v-for="m in MODES" :key="m.id"
              :class="['mode-tab', currentMode === m.id ? 'active' : '']"
              @click="switchMode(m.id)">
              {{ m.icon }} {{ m.label }}
            </button>
          </div>
          <!-- XP stats -->
          <div class="stats-row">
            <div class="stat-chip">🔥 {{ auth.user?.streak_days || 0 }}d</div>
            <div class="stat-chip">⭐ {{ auth.user?.xp_points || 0 }} XP</div>
            <div class="stat-chip level">Lv.{{ auth.user?.level || 1 }}</div>
          </div>
        </div>
      </div>

      <!-- ── DIFFICULTY ─────────────────────────────────────────── -->
      <div class="difficulty-bar">
        <span class="bar-label">Difficulty:</span>
        <div class="diff-options">
          <button v-for="d in DIFFS" :key="d.id"
            :class="['diff-btn', difficulty === d.id ? 'active' : '']"
            @click="difficulty = d.id">
            {{ d.icon }} {{ d.label }}
          </button>
        </div>
      </div>

      <!-- ── SCENARIO / TOPIC STRIP ─────────────────────────────── -->
      <div class="scenario-bar" v-if="currentMode === 'roleplay'">
        <span class="bar-label">📍 Scenario:</span>
        <div class="strip-scroll">
          <button v-for="s in scenarios" :key="s.id"
            :class="['strip-btn', selectedScenario?.id === s.id ? 'active' : '']"
            @click="selectScenario(s)">
            {{ s.icon }} {{ s.name }}
          </button>
        </div>
      </div>

      <div class="topics-bar" v-if="currentMode === 'english'">
        <span class="bar-label">🎯 Topic:</span>
        <div class="strip-scroll">
          <button v-for="t in topics" :key="t.label" class="strip-btn" @click="sendMessage(t.prompt)">
            {{ t.icon }} {{ t.label }}
          </button>
        </div>
      </div>

      <!-- ── CHAT AREA ───────────────────────────────────────────── -->
      <div class="chat-area" ref="chatArea">
        <!-- Welcome screen -->
        <div class="welcome" v-if="messages.length === 0">
          <div class="wb-name">{{ voiceLang === 'bn-BD' ? 'হ্যালো! আমি Amy 👋' : "Hi! I'm Amy 👋" }}</div>
          <div class="wb-text">{{ welcomeText }}</div>
          <div class="wb-qs">
            <button v-for="s in quickStarters" :key="s" class="qs" @click="sendMessage(s)">{{ s }}</button>
          </div>
        </div>

        <!-- Messages -->
        <div v-for="msg in messages" :key="msg.id"
          :class="['msg-row', msg.role === 'assistant' ? 'ai' : 'user']">

          <template v-if="msg.role === 'assistant'">
            <div class="msg-avatar">🤖</div>
            <div class="msg-right">
              <div class="msg-bubble ai-bubble" v-html="fmt(msg.content)"></div>
              <div class="grammar-card" v-if="msg.grammarNote">
                <span>📝</span><span class="gc-label">Grammar:</span><span>{{ msg.grammarNote }}</span>
              </div>
              <div class="vocab-card" v-if="msg.newVocab">
                <span>📚</span><span class="vc-text">{{ msg.newVocab }}</span>
                <button class="vc-save" @click="saveVocab(msg.newVocab)">+ Save</button>
              </div>
              <div class="fluency-card" v-if="msg.fluencyScore">
                <span class="fc-label">Fluency</span>
                <div class="fc-track">
                  <div class="fc-fill"
                    :style="`width:${msg.fluencyScore}%`"
                    :class="msg.fluencyScore > 80 ? 'exc' : msg.fluencyScore > 60 ? 'good' : 'imp'">
                  </div>
                </div>
                <span>{{ msg.fluencyScore }}%</span>
              </div>
              <div class="xp-pop" v-if="msg.xpEarned">+{{ msg.xpEarned }} XP</div>
              <div class="msg-actions">
                <button class="ma" @click="speak(msg.content)" title="Read aloud">🔊</button>
                <button class="ma" @click="copy(msg.content)"  title="Copy">📋</button>
              </div>
            </div>
          </template>

          <template v-else>
            <div class="msg-bubble user-bubble">{{ msg.content }}</div>
          </template>
        </div>

        <!-- Typing indicator -->
        <div class="typing-row" v-if="isLoading">
          <div class="msg-avatar">🤖</div>
          <div class="typing-bubble"><span></span><span></span><span></span></div>
        </div>
      </div>

      <!-- ── INPUT ──────────────────────────────────────────────── -->
      <div class="input-area">
        <div class="input-row">
          <textarea v-model="inputText" ref="inputRef" class="chat-input"
            :placeholder="voiceLang === 'bn-BD' ? 'বাংলা বা ইংরেজিতে লিখুন... অথবা 🎤 চাপুন' : 'Type or press 🎤 to speak'"
            rows="1"
            @keydown.enter.exact.prevent="send"
            @input="autoResize">
          </textarea>
          <div class="input-btns">
            <button class="btn-voice" :class="{ active: voiceOverlayOpen }" @click="openVoiceOverlay" title="Voice conversation">🎤</button>
            <button class="btn-stop"  v-if="isSpeaking"                     @click="stopSpeak"         title="Stop">⏹</button>
            <button class="btn-send"  @click="send" :disabled="!inputText.trim() || isLoading">{{ isLoading ? '...' : '↑' }}</button>
          </div>
        </div>
        <div class="input-meta">
          <span>Enter to send · 🎤 Voice conversation</span>
          <span v-if="amyUsage && !amyUsage.is_paid" class="usage-info">
            {{ amyUsage.messages_used }}/{{ amyUsage.messages_limit }} messages today
            <router-link to="/pricing" class="upgrade-link">Upgrade</router-link>
          </span>
        </div>
      </div>

      <!-- ── SAVED VOCAB PANEL ───────────────────────────────────── -->
      <div class="vocab-panel" v-if="savedVocabList.length > 0">
        <div class="vp-head">
          <span>📚 Saved Words ({{ savedVocabList.length }})</span>
          <button @click="savedVocabList = []" class="vp-clear">Clear</button>
        </div>
        <div class="vp-list">
          <span v-for="v in savedVocabList" :key="v" class="vtag">{{ v }}</span>
        </div>
      </div>

    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import AppLayout   from '@/components/layout/AppLayout.vue'
import AmyRobot    from './components/AmyRobot.vue'
import AmyVoiceOverlay from './components/AmyVoiceOverlay.vue'
import { useAmyAnimation } from './composables/useAmyAnimation.js'
import { useVoiceChat }    from './composables/useVoiceChat.js'
import { useAuthStore }    from '@/store/auth'
import { toast }  from 'vue3-toastify'
import api        from '@/api'

const auth = useAuthStore()

// ── Core state ────────────────────────────────────────────────────
const messages         = ref([])
const inputText        = ref('')
const isLoading        = ref(false)
const isSpeaking       = ref(false)
const currentMood      = ref('happy')
const detectedEmotion  = ref('')
const currentMode      = ref('general')
const difficulty       = ref('intermediate')
const selectedScenario = ref(null)
const savedVocabList   = ref([])
const chatArea         = ref(null)
const inputRef         = ref(null)
const scenarios        = ref([])
const topics           = ref([])
const amyUsage         = ref(null)
const sessionId        = ref(null)
const voiceLang        = ref(localStorage.getItem('amy_lang') || 'en-US')
watch(voiceLang, v => localStorage.setItem('amy_lang', v))

let msgId = 0

// ── Animation composable ──────────────────────────────────────────
const anim = useAmyAnimation(currentMood, isSpeaking, isLoading)

// Props passed to header robot
const headerAnimProps = computed(() => ({
  waveH:     anim.waveH.value,
  eyeSc:     anim.eyeSc.value,
  pX:        anim.pX.value,
  pY:        anim.pY.value,
  mouthPath: anim.mouthPath.value,
  mouthFill: anim.mouthFill.value,
  mouthFOp:  anim.mouthFOp.value,
  cheekOp:   anim.cheekOp.value,
  headTilt:  anim.headTilt.value,
  armLRot:   anim.armLRot.value,
  armRRot:   anim.armRRot.value,
  chestColor:anim.chestColor.value,
  browL:     anim.browL.value,
  browR:     anim.browR.value,
}))

// Props passed to voice overlay robot
const voiceAnimProps = computed(() => ({
  voWaveH:    anim.voWaveH.value,
  voEyeSc:    anim.voEyeSc.value,
  voPX:       anim.voPX.value,
  voPY:       anim.voPY.value,
  voArmL:     anim.voArmL.value,
  voArmR:     anim.voArmR.value,
  voLegL:     anim.voLegL.value,
  voLegR:     anim.voLegR.value,
  voHeadTilt: anim.voHeadTilt.value,
  voBrowL:    anim.voBrowL.value,
  voBrowR:    anim.voBrowR.value,
  voMouth:    anim.voMouth.value,
  voMouthF:   anim.voMouthF.value,
  voMouthFOp: anim.voMouthFOp.value,
  voCheek:    anim.voCheek.value,
  chestColor: anim.chestColor.value,
}))

// ── Voice composable ──────────────────────────────────────────────
const {
  voiceOverlayOpen, voicePhase, voiceTranscript, voiceLastReply,
  openVoiceOverlay, closeVoiceOverlay,
  stopSpeak,
} = useVoiceChat({
  currentMode, selectedScenario, difficulty,
  messages, sessionId, currentMood, detectedEmotion,
  isSpeaking, voiceLang,
  scrollToBottom: () => nextTick(() => { if (chatArea.value) chatArea.value.scrollTop = chatArea.value.scrollHeight }),
  startBodyAnim: anim.startBodyAnim,
  stopBodyAnim:  anim.stopBodyAnim,
})

// ── Chat functions ────────────────────────────────────────────────
function detectTypedLang(text) { return /[\u0980-\u09FF]/.test(text) ? 'Bangla' : 'auto' }

async function send() {
  const text = inputText.value.trim()
  if (!text || isLoading.value) return
  sendMessage(text)
  inputText.value = ''
  nextTick(() => { if (inputRef.value) inputRef.value.style.height = 'auto' })
}

async function sendMessage(text) {
  messages.value.push({ id: ++msgId, role: 'user', content: text })
  scrollToBottom(); isLoading.value = true
  try {
    const history = messages.value
      .slice(-12)
      .filter(m => m.role === 'user' || m.role === 'assistant')
      .map(m => ({ role: m.role, content: m.content }))

    const res = await api.post('/amy/chat', {
      message:    text,
      history:    history.slice(0, -1),
      mode:       currentMode.value,
      scenario:   selectedScenario.value?.name || null,
      difficulty: difficulty.value,
      language:   detectTypedLang(text),
      session_id: sessionId.value,
    })
    const d = res.data
    if (d.detected_emotion) detectedEmotion.value = d.detected_emotion
    if (d.mood)             currentMood.value     = d.mood
    if (d.session_id)       sessionId.value       = d.session_id

    messages.value.push({
      id: ++msgId, role: 'assistant', content: d.reply, mood: d.mood,
      grammarNote: d.grammar_note, newVocab: d.new_vocab,
      fluencyScore: d.fluency_score, xpEarned: d.xp_earned,
    })
    if (currentMode.value !== 'general') setTimeout(() => speak(d.reply), 300)
    await loadUsage()
  } catch (e) {
    if (e.response?.status !== 402) {
      messages.value.push({ id: ++msgId, role: 'assistant', content: 'Oops! Something went wrong 😅', mood: 'thinking' })
    }
  } finally {
    isLoading.value = false; scrollToBottom()
  }
}

function speak(text) {
  if (!('speechSynthesis' in window)) return
  stopSpeak()
  const utter = new SpeechSynthesisUtterance(text.replace(/<[^>]*>/g, '').replace(/[*_`]/g, ''))
  utter.lang = voiceLang.value === 'bn-BD' ? 'bn-BD' : 'en-US'
  utter.rate = 0.92; utter.pitch = 1.15
  const applyVoice = () => {
    const voices = speechSynthesis.getVoices()
    const preferred = ['Samantha','Karen','Moira','Tessa','Google UK English Female','Zira','Microsoft Jenny']
    for (const name of preferred) {
      const v = voices.find(v => v.name.includes(name))
      if (v) { utter.voice = v; break }
    }
  }
  if (speechSynthesis.getVoices().length) applyVoice()
  else speechSynthesis.addEventListener('voiceschanged', applyVoice, { once: true })
  utter.onstart = () => { isSpeaking.value = true }
  utter.onend   = () => { isSpeaking.value = false }
  utter.onerror = () => { isSpeaking.value = false }
  speechSynthesis.speak(utter)
}

// ── Helpers ───────────────────────────────────────────────────────
function saveVocab(word) {
  if (!savedVocabList.value.includes(word)) {
    savedVocabList.value.push(word)
    api.post('/amy/vocab/save', { word }).catch(() => {})
  }
  toast.success('Word saved!')
}
function copy(text)      { navigator.clipboard.writeText(text); toast.info('Copied!') }
function scrollToBottom(){ nextTick(() => { if (chatArea.value) chatArea.value.scrollTop = chatArea.value.scrollHeight }) }
function autoResize()    {
  nextTick(() => {
    if (inputRef.value) {
      inputRef.value.style.height = 'auto'
      inputRef.value.style.height = Math.min(inputRef.value.scrollHeight, 140) + 'px'
    }
  })
}
function fmt(t) {
  return t
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}
function switchMode(m)    { currentMode.value = m; messages.value = []; selectedScenario.value = null; detectedEmotion.value = '' }
function selectScenario(s){ selectedScenario.value = s; messages.value = []; sendMessage(`Let's practice a ${s.name} scenario.`) }
async function loadUsage() { try { const r = await api.get('/amy/usage'); amyUsage.value = r.data } catch {} }

// ── Constants ─────────────────────────────────────────────────────
const MODES = [
  { id:'general',  icon:'💬', label:'Chat'      },
  { id:'english',  icon:'📖', label:'Practice'  },
  { id:'roleplay', icon:'🎭', label:'Role-Play' },
]
const DIFFS = [
  { id:'beginner',     icon:'🌱', label:'Beginner'     },
  { id:'intermediate', icon:'⚡', label:'Intermediate' },
  { id:'advanced',     icon:'🔥', label:'Advanced'     },
]
const statusText   = computed(() => isLoading.value ? 'Thinking…' : isSpeaking.value ? 'Speaking…' : 'Ready to help')
const welcomeText  = computed(() => ({
  general:  "I'm your personal AI English tutor! Ask me anything.",
  english:  "Let's practice English together! Pick a topic or start talking.",
  roleplay: "Choose a scenario and I'll play the character!",
}[currentMode.value]))
const quickStarters = computed(() => ({
  general:  ['Help me improve my English', 'Teach me idioms', 'Correct my grammar'],
  english:  ["Let's talk about travel", 'Help me with past tense', 'Practice daily conversation'],
  roleplay: ['Job interview', 'Restaurant', 'Airport'],
}[currentMode.value]))

onMounted(async () => {
  const [sc, tp] = await Promise.allSettled([api.get('/amy/scenarios'), api.get('/amy/topics')])
  if (sc.status === 'fulfilled') scenarios.value = sc.value.data
  if (tp.status === 'fulfilled') topics.value    = tp.value.data
  loadUsage()
})
</script>

<style scoped>
.amy-page { display:flex; flex-direction:column; gap:14px; height:calc(100vh - 120px); overflow:hidden; }

/* Header */
.amy-header    { display:flex; align-items:center; justify-content:space-between; background:var(--bg2); border:1px solid var(--border); border-radius:18px; padding:12px 22px; flex-shrink:0; }
.amy-identity  { display:flex; align-items:center; gap:10px; }
.amy-name      { font-size:16px; font-weight:800; color:var(--text); margin-bottom:3px; }
.amy-badge     { background:linear-gradient(135deg,var(--p),#a78bfa); color:#fff; font-size:10px; font-weight:700; padding:2px 8px; border-radius:20px; margin-left:6px; }
.amy-status    { display:flex; align-items:center; gap:6px; font-size:12px; color:var(--text3); margin-bottom:3px; }
.status-dot    { width:7px; height:7px; border-radius:50%; background:var(--border2); flex-shrink:0; }
.status-dot.online   { background:var(--teal);  animation:blink 2s   infinite; }
.status-dot.thinking { background:var(--amber); animation:blink .6s  infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }
.emotion-pill  { background:rgba(123,110,246,.12); color:var(--p); font-size:11px; font-weight:500; padding:2px 10px; border-radius:20px; display:inline-block; }
.amy-right     { display:flex; flex-direction:column; align-items:flex-end; gap:8px; }

/* Lang / mode toggles */
.lang-toggle, .mode-tabs { display:flex; gap:4px; }
.lang-btn, .mode-tab { background:rgba(255,255,255,.05); border:1px solid var(--border); color:var(--text2); border-radius:20px; padding:6px 12px; font-size:12px; font-weight:600; cursor:pointer; transition:all .18s; }
.lang-btn.active, .mode-tab.active { background:rgba(123,110,246,.15); border-color:var(--p); color:var(--p); }

/* Stats */
.stats-row  { display:flex; gap:8px; }
.stat-chip  { background:rgba(255,255,255,.05); border:1px solid var(--border); color:var(--text2); border-radius:20px; padding:4px 11px; font-size:11px; font-weight:600; }
.stat-chip.level { background:rgba(245,166,35,.12); border-color:rgba(245,166,35,.3); color:var(--amber); }

/* Difficulty / scenario / topics bar */
.difficulty-bar, .scenario-bar, .topics-bar {
  display:flex; align-items:center; gap:12px;
  padding:10px 16px; background:var(--bg2); border:1px solid var(--border);
  border-radius:12px; flex-shrink:0; overflow:hidden;
}
.bar-label    { font-size:12px; color:var(--text3); font-weight:600; flex-shrink:0; }
.diff-options { display:flex; gap:6px; }
.diff-btn     { background:transparent; border:1px solid var(--border); color:var(--text2); border-radius:20px; padding:5px 12px; font-size:12px; cursor:pointer; transition:all .18s; }
.diff-btn.active { background:rgba(123,110,246,.15); border-color:var(--p); color:var(--p); }
.strip-scroll  { display:flex; gap:8px; overflow-x:auto; padding-bottom:2px; }
.strip-scroll::-webkit-scrollbar { display:none; }
.strip-btn    { background:rgba(255,255,255,.04); border:1px solid var(--border); color:var(--text2); border-radius:20px; padding:6px 13px; font-size:12px; font-weight:500; cursor:pointer; white-space:nowrap; transition:all .18s; flex-shrink:0; }
.strip-btn.active { background:rgba(123,110,246,.15); border-color:var(--p); color:var(--p); }

/* Chat */
.chat-area { flex:1; overflow-y:auto; padding:10px 0; display:flex; flex-direction:column; gap:16px; min-height:0; }
.welcome   { background:var(--bg2); border:1px solid var(--border); border-radius:18px; padding:20px; }
.wb-name   { font-size:16px; font-weight:700; color:var(--text); margin-bottom:8px; }
.wb-text   { font-size:14px; color:var(--text2); line-height:1.65; margin-bottom:16px; }
.wb-qs     { display:flex; flex-wrap:wrap; gap:8px; }
.qs        { background:rgba(123,110,246,.1); border:1px solid rgba(123,110,246,.25); color:var(--p); border-radius:20px; padding:7px 14px; font-size:12px; font-weight:500; cursor:pointer; transition:all .18s; }
.qs:hover  { background:rgba(123,110,246,.2); transform:translateY(-1px); }

.msg-row   { display:flex; align-items:flex-start; gap:12px; }
.msg-row.user { flex-direction:row-reverse; }
.msg-avatar { width:36px; height:36px; border-radius:50%; background:var(--p-soft); display:flex; align-items:center; justify-content:center; font-size:18px; flex-shrink:0; border:1px solid var(--border); }
.msg-right  { display:flex; flex-direction:column; gap:6px; max-width:75%; }
.msg-bubble { padding:13px 16px; border-radius:18px; font-size:14px; line-height:1.65; }
.ai-bubble  { background:var(--bg2); border:1px solid var(--border); border-radius:0 18px 18px 18px; color:var(--text); }
.user-bubble{ background:linear-gradient(135deg,var(--p),#a78bfa); color:#fff; border-radius:18px 0 18px 18px; max-width:480px; }

.grammar-card { display:flex; align-items:flex-start; gap:8px; background:rgba(0,212,170,.08); border:1px solid rgba(0,212,170,.2); border-radius:10px; padding:10px 13px; font-size:12px; color:var(--text2); }
.gc-label     { color:var(--teal); font-weight:700; flex-shrink:0; }
.vocab-card   { display:flex; align-items:center; gap:8px; background:rgba(123,110,246,.08); border:1px solid rgba(123,110,246,.2); border-radius:10px; padding:9px 13px; font-size:12px; }
.vc-text      { color:var(--text2); flex:1; }
.vc-save      { background:rgba(123,110,246,.2); border:none; color:var(--p); border-radius:6px; padding:3px 9px; font-size:11px; font-weight:600; cursor:pointer; }
.fluency-card { display:flex; align-items:center; gap:8px; font-size:11px; }
.fc-label     { color:var(--text3); }
.fc-track     { flex:1; height:5px; background:rgba(255,255,255,.06); border-radius:5px; overflow:hidden; }
.fc-fill      { height:100%; border-radius:5px; transition:width .8s ease; }
.fc-fill.exc  { background:var(--teal); }
.fc-fill.good { background:var(--amber); }
.fc-fill.imp  { background:var(--rose); }
.xp-pop       { font-size:11px; font-weight:700; color:var(--amber); animation:xp-float .8s ease forwards; }
@keyframes xp-float { 0%{opacity:1;transform:translateY(0)} 100%{opacity:0;transform:translateY(-16px)} }
.msg-actions  { display:flex; gap:6px; }
.ma           { background:rgba(255,255,255,.05); border:none; border-radius:8px; padding:5px 9px; font-size:12px; cursor:pointer; color:var(--text3); transition:all .18s; }
.ma:hover     { background:rgba(255,255,255,.1); color:var(--text); }

.typing-row   { display:flex; align-items:flex-start; gap:12px; }
.typing-bubble{ background:var(--bg2); border:1px solid var(--border); border-radius:0 18px 18px 18px; padding:14px 18px; display:flex; gap:5px; align-items:center; }
.typing-bubble span { width:8px; height:8px; background:var(--text3); border-radius:50%; animation:dot-bounce .8s infinite; }
.typing-bubble span:nth-child(2){ animation-delay:.15s; }
.typing-bubble span:nth-child(3){ animation-delay:.30s; }
@keyframes dot-bounce { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-6px)} }

/* Input */
.input-area  { background:var(--bg2); border:1px solid var(--border); border-radius:18px; padding:14px 16px; flex-shrink:0; }
.input-row   { display:flex; gap:10px; align-items:flex-end; }
.chat-input  { flex:1; background:rgba(255,255,255,.05); border:1px solid var(--border); border-radius:12px; padding:12px 16px; color:var(--text); font-size:14px; outline:none; resize:none; font-family:inherit; line-height:1.5; transition:border-color .18s; min-height:46px; max-height:140px; }
.chat-input:focus { border-color:var(--p); }
.chat-input::placeholder { color:var(--text3); }
.input-btns  { display:flex; gap:8px; flex-shrink:0; }
.btn-voice   { width:44px; height:44px; border-radius:50%; background:rgba(255,255,255,.07); border:1px solid var(--border); font-size:18px; cursor:pointer; transition:all .18s; display:flex; align-items:center; justify-content:center; }
.btn-voice:hover { background:rgba(123,110,246,.15); border-color:var(--p); }
.btn-voice.active{ background:rgba(255,107,138,.2); border-color:var(--rose); animation:pulse-btn .6s infinite; }
@keyframes pulse-btn { 0%,100%{transform:scale(1)} 50%{transform:scale(1.08)} }
.btn-stop    { width:44px; height:44px; border-radius:50%; background:rgba(255,107,138,.15); border:1px solid rgba(255,107,138,.3); color:var(--rose); font-size:16px; cursor:pointer; }
.btn-send    { width:44px; height:44px; border-radius:50%; background:linear-gradient(135deg,var(--p),#a78bfa); border:none; color:#fff; font-size:18px; font-weight:700; cursor:pointer; transition:all .18s; box-shadow:0 4px 14px var(--p-glow); }
.btn-send:hover:not(:disabled) { transform:scale(1.05); }
.btn-send:disabled { opacity:.4; cursor:not-allowed; box-shadow:none; }
.input-meta  { display:flex; justify-content:space-between; font-size:11px; color:var(--text3); margin-top:8px; }
.usage-info  { display:flex; align-items:center; gap:6px; }
.upgrade-link{ color:var(--p); font-weight:600; text-decoration:none; }

/* Vocab panel */
.vocab-panel { background:var(--bg2); border:1px solid var(--border); border-radius:14px; padding:14px 16px; flex-shrink:0; }
.vp-head     { display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; font-size:13px; font-weight:600; color:var(--text2); }
.vp-clear    { background:transparent; border:none; color:var(--text3); font-size:12px; cursor:pointer; }
.vp-clear:hover { color:var(--rose); }
.vp-list     { display:flex; flex-wrap:wrap; gap:7px; }
.vtag        { background:rgba(123,110,246,.12); border:1px solid rgba(123,110,246,.2); color:var(--p); padding:4px 12px; border-radius:20px; font-size:12px; }
</style>