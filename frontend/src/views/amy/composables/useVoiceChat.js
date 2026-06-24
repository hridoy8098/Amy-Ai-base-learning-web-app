import { ref, watch } from 'vue'
import { toast } from 'vue3-toastify'
import api from '@/api'

/**
 * Picks the most natural-sounding female voice available in the browser.
 * Priority order tested across Chrome, Edge, Firefox, Safari.
 */
function pickFemaleVoice(lang = 'en-US') {
  const voices = speechSynthesis.getVoices()

  if (lang.startsWith('bn')) {
    return voices.find(v => v.lang.startsWith('bn')) || null
  }

  // Ranked list — most human-sounding first
  const preferred = [
    'Samantha',    // macOS/iOS — very natural
    'Karen',       // macOS Australian
    'Moira',       // macOS Irish
    'Tessa',       // macOS South African
    'Veena',       // macOS Indian
    'Zira',        // Windows — decent
    'Google UK English Female',
    'Google US English',
    'Microsoft Zira',
    'Microsoft Jenny',
    'Microsoft Aria',
  ]

  for (const name of preferred) {
    const v = voices.find(v => v.name.includes(name))
    if (v) return v
  }

  // Fallback: any en-US female-labelled voice
  return (
    voices.find(v => v.lang === 'en-US' && /female/i.test(v.name)) ||
    voices.find(v => v.lang === 'en-US') ||
    null
  )
}

export function useVoiceChat({
  currentMode,
  selectedScenario,
  difficulty,
  messages,
  sessionId,
  currentMood,
  detectedEmotion,
  isSpeaking,
  voiceLang,
  scrollToBottom,
  startBodyAnim,
  stopBodyAnim,
}) {
  const voiceOverlayOpen = ref(false)
  const voicePhase       = ref('idle')
  const voiceTranscript  = ref('')
  const voiceLastReply   = ref('')
  const voiceHistory     = ref([])

  let voiceActive = false
  let voiceRec    = null
  let msgId       = 1000 // offset so IDs don't clash with chat msgIds

  const langLabel = () => voiceLang.value === 'bn-BD' ? 'Bangla' : 'English'

  // ── TTS ──────────────────────────────────────────────────────────
  function speakAndWait(text) {
    return new Promise(resolve => {
      if (!('speechSynthesis' in window)) { resolve(); return }
      speechSynthesis.cancel()

      const clean = text.replace(/<[^>]*>/g, '').replace(/[*_`#]/g, '').trim()
      const utter = new SpeechSynthesisUtterance(clean)

      utter.lang  = voiceLang.value === 'bn-BD' ? 'bn-BD' : 'en-US'
      utter.rate  = difficulty.value === 'beginner' ? 0.82 : difficulty.value === 'advanced' ? 1.05 : 0.92
      utter.pitch = 1.15  // slightly higher = more feminine/warm

      const applyVoice = () => {
        const v = pickFemaleVoice(utter.lang)
        if (v) utter.voice = v
      }

      if (speechSynthesis.getVoices().length) {
        applyVoice()
      } else {
        speechSynthesis.addEventListener('voiceschanged', applyVoice, { once: true })
      }

      isSpeaking.value = true
      utter.onend  = () => { isSpeaking.value = false; resolve() }
      utter.onerror = () => { isSpeaking.value = false; resolve() }
      speechSynthesis.speak(utter)
    })
  }

  function stopSpeak() {
    speechSynthesis.cancel()
    isSpeaking.value = false
  }

  // ── STT ──────────────────────────────────────────────────────────
  function startVoiceListen() {
    if (!voiceActive) return
    voicePhase.value = 'listening'; voiceTranscript.value = ''

    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    voiceRec = new SR()
    voiceRec.lang = voiceLang.value
    voiceRec.continuous = false
    voiceRec.interimResults = true

    voiceRec.onresult = e => {
      voiceTranscript.value = Array.from(e.results).map(r => r[0].transcript).join('')
    }
    voiceRec.onend = async () => {
      if (!voiceActive) return
      const t = voiceTranscript.value.trim()
      if (!t) { setTimeout(() => { if (voiceActive) startVoiceListen() }, 400); return }
      await handleVoiceTurn(t)
    }
    voiceRec.onerror = () => {
      if (!voiceActive) return
      setTimeout(() => { if (voiceActive) startVoiceListen() }, 600)
    }
    voiceRec.start()
  }

  async function handleVoiceTurn(transcript) {
    if (!voiceActive) return
    voicePhase.value = 'thinking'; currentMood.value = 'thinking'
    voiceHistory.value.push({ role: 'user', content: transcript })
    messages.value.push({ id: ++msgId, role: 'user', content: transcript })
    scrollToBottom()

    try {
      const res = await api.post('/amy/voice', {
        transcript,
        history:    voiceHistory.value.slice(-6, -1),
        mode:       currentMode.value,
        scenario:   selectedScenario.value?.name || null,
        difficulty: difficulty.value,
        language:   langLabel(),
        session_id: sessionId.value,
      })
      const d = res.data
      if (d.mood)             currentMood.value     = d.mood
      if (d.detected_emotion) detectedEmotion.value = d.detected_emotion
      if (d.session_id)       sessionId.value       = d.session_id

      voiceHistory.value.push({ role: 'assistant', content: d.reply })
      messages.value.push({ id: ++msgId, role: 'assistant', content: d.reply, mood: d.mood })
      scrollToBottom()

      voiceLastReply.value = d.reply
      voicePhase.value = 'speaking'
      await speakAndWait(d.reply)
      if (voiceActive) startVoiceListen()

    } catch {
      const errMsg = voiceLang.value === 'bn-BD' ? 'একটু সমস্যা হলো!' : 'Sorry, small issue!'
      voicePhase.value = 'speaking'
      await speakAndWait(errMsg)
      if (voiceActive) startVoiceListen()
    }
  }

  // ── Overlay open / close ─────────────────────────────────────────
  function openVoiceOverlay() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      toast.warning('Voice needs Chrome or Edge!')
      return
    }
    voiceOverlayOpen.value = true; voiceActive = true
    voiceHistory.value = []; voiceTranscript.value = ''; voiceLastReply.value = ''
    voicePhase.value = 'speaking'

    const greeting = voiceLang.value === 'bn-BD'
      ? 'হ্যালো! আমি Amy। চলুন কথা বলি!'
      : "Hi! I'm Amy, your English tutor. Let's talk — go ahead and speak!"

    voiceLastReply.value = greeting
    speakAndWait(greeting).then(() => { if (voiceActive) startVoiceListen() })
  }

  function closeVoiceOverlay() {
    voiceActive = false; voicePhase.value = 'idle'; voiceOverlayOpen.value = false
    voiceTranscript.value = ''; voiceLastReply.value = ''
    stopSpeak()
    if (voiceRec) { try { voiceRec.stop() } catch {} voiceRec = null }
    stopBodyAnim()
  }

  watch(voicePhase, p => { if (p === 'idle') stopBodyAnim(); else startBodyAnim(p) })

  return {
    voiceOverlayOpen,
    voicePhase,
    voiceTranscript,
    voiceLastReply,
    openVoiceOverlay,
    closeVoiceOverlay,
    speakAndWait,
    stopSpeak,
  }
}