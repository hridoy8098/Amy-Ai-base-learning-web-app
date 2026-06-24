import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

export function useAmyAnimation(currentMood, isSpeaking, isLoading) {
  // ── Wave bars ────────────────────────────────────────────────────
  const waveH   = ref([8, 14, 20, 14, 8])
  const voWaveH = ref([10, 18, 28, 18, 10])

  // ── Eye & pupil ──────────────────────────────────────────────────
  const eyeSc  = ref(1)
  const pX     = ref(0), pY = ref(0)
  const voEyeSc = ref(1)
  const voPX   = ref(0), voPY = ref(0)

  // ── Voice body parts ─────────────────────────────────────────────
  const voArmLA    = ref(20),  voArmRA = ref(-20)
  const voLegLA    = ref(0),   voLegRA = ref(0), voHeadA = ref(0)
  const voArmL     = computed(() => `rotate(${voArmLA.value}deg)`)
  const voArmR     = computed(() => `rotate(${voArmRA.value}deg)`)
  const voLegL     = computed(() => `rotate(${voLegLA.value}deg)`)
  const voLegR     = computed(() => `rotate(${voLegRA.value}deg)`)
  const voHeadTilt = computed(() => voHeadA.value)

  let waveT = null, blinkT = null, pupilT = null, voBodyT = null

  // ── Mood config ──────────────────────────────────────────────────
  const moodCfg = {
    happy:    { mouth:'M190,228 Q210,244 230,228', mf:'M190,228 Q210,244 230,228 Q210,255 190,228 Z', mfOp:.55, brow:'normal', cheek:.50, tilt:0,  armL:'rotate(12deg)',  armR:'rotate(-12deg)', chest:'#ff8fab', eyeSc:1.00 },
    excited:  { mouth:'M186,226 Q210,248 234,226', mf:'M186,226 Q210,248 234,226 Q210,260 186,226 Z', mfOp:.75, brow:'up',    cheek:.70, tilt:0,  armL:'rotate(-22deg)', armR:'rotate(22deg)',  chest:'#ffd600', eyeSc:1.08 },
    thinking: { mouth:'M193,230 Q210,236 227,228', mf:'',                                             mfOp:0,   brow:'down',  cheek:.12, tilt:-7, armL:'rotate(0deg)',   armR:'rotate(-38deg)', chest:'#82b1ff', eyeSc:.88  },
    caring:   { mouth:'M190,228 Q210,242 230,228', mf:'M190,228 Q210,242 230,228 Q210,248 190,228 Z', mfOp:.40, brow:'normal',cheek:.65, tilt:4,  armL:'rotate(8deg)',   armR:'rotate(-8deg)',  chest:'#ff8fab', eyeSc:.92  },
    playful:  { mouth:'M188,226 Q210,246 232,226', mf:'M188,226 Q210,246 232,226 Q210,256 188,226 Z', mfOp:.60, brow:'up',    cheek:.55, tilt:-4, armL:'rotate(-15deg)', armR:'rotate(18deg)',  chest:'#7b6ef6', eyeSc:1.00 },
    gentle:   { mouth:'M192,228 Q210,240 228,228', mf:'M192,228 Q210,240 228,228 Q210,244 192,228 Z', mfOp:.35, brow:'normal',cheek:.80, tilt:8,  armL:'rotate(28deg)',  armR:'rotate(-5deg)',  chest:'#ff8fab', eyeSc:.52  },
    neutral:  { mouth:'M193,230 Q210,236 227,230', mf:'',                                             mfOp:0,   brow:'normal',cheek:.20, tilt:0,  armL:'rotate(12deg)',  armR:'rotate(-12deg)', chest:'#9FA8DA', eyeSc:1.00 },
  }

  const cfg        = computed(() => moodCfg[currentMood.value] || moodCfg.neutral)
  const mouthPath  = computed(() => cfg.value.mouth)
  const mouthFill  = computed(() => cfg.value.mf)
  const mouthFOp   = computed(() => cfg.value.mfOp)
  const cheekOp    = computed(() => cfg.value.cheek)
  const headTilt   = computed(() => cfg.value.tilt)
  const armLRot    = computed(() => cfg.value.armL)
  const armRRot    = computed(() => cfg.value.armR)
  const chestColor = computed(() => cfg.value.chest)

  const browL = computed(() => {
    const b = cfg.value.brow
    return b === 'up' ? 'M168,162 Q180,155 192,158' : b === 'down' ? 'M168,162 Q180,168 192,165' : 'M168,165 Q180,160 192,163'
  })
  const browR = computed(() => {
    const b = cfg.value.brow
    return b === 'up' ? 'M228,158 Q240,155 252,162' : b === 'down' ? 'M228,165 Q240,168 252,162' : 'M228,163 Q240,160 252,165'
  })
  const voBrowL = computed(() => {
    const b = cfg.value.brow
    return b === 'up' ? 'M163,158 Q181,150 199,154' : b === 'down' ? 'M163,158 Q181,165 199,161' : 'M163,161 Q181,155 199,158'
  })
  const voBrowR = computed(() => {
    const b = cfg.value.brow
    return b === 'up' ? 'M221,154 Q239,150 257,158' : b === 'down' ? 'M221,161 Q239,165 257,158' : 'M221,158 Q239,155 257,161'
  })
  const voMouth    = computed(() => cfg.value.mouth)
  const voMouthF   = computed(() => cfg.value.mf)
  const voMouthFOp = computed(() => cfg.value.mfOp)
  const voCheek    = computed(() => cfg.value.cheek)

  // ── Voice body animation ─────────────────────────────────────────
  function startBodyAnim(state) {
    clearInterval(voBodyT); let t = 0
    voBodyT = setInterval(() => {
      t++
      const s = Math.sin
      if (state === 'listening') {
        voArmLA.value = -30 + s(t * .45) * 22; voArmRA.value = 14 + s(t * .20) * 8
        voLegLA.value = 5 * s(t * .10);         voLegRA.value = -5 * s(t * .10); voHeadA.value = 6 * s(t * .13)
      } else if (state === 'speaking') {
        voArmLA.value = 10 + s(t * .22) * 32;  voArmRA.value = -10 + s(t * .22 + Math.PI) * 32
        voLegLA.value = 8 * s(t * .15);         voLegRA.value = -8 * s(t * .15); voHeadA.value = 9 * s(t * .18)
      } else {
        voArmLA.value = 18 + s(t * .08) * 5;   voArmRA.value = -35 + s(t * .12) * 8
        voLegLA.value = 2 * s(t * .06);         voLegRA.value = -2 * s(t * .06); voHeadA.value = 7 * s(t * .10)
      }
      voWaveH.value = Array.from({ length: 5 }, () => Math.round(8 + Math.random() * 30))
    }, 75)
  }

  function stopBodyAnim() {
    clearInterval(voBodyT)
    voArmLA.value = 20; voArmRA.value = -20; voLegLA.value = 0; voLegRA.value = 0; voHeadA.value = 0
    voWaveH.value = [10, 18, 28, 18, 10]
  }

  // ── Watchers ─────────────────────────────────────────────────────
  watch([isSpeaking, isLoading], ([sp, ld]) => {
    clearInterval(waveT)
    if (sp || ld) {
      waveT = setInterval(() => {
        waveH.value = Array.from({ length: 5 }, () => Math.round(6 + Math.random() * 22))
      }, 160)
    } else {
      waveH.value = [8, 14, 20, 14, 8]
    }
  })

  watch(currentMood, mood => {
    clearInterval(pupilT); pX.value = 0; pY.value = 0; voPX.value = 0; voPY.value = 0
    if (mood === 'thinking') {
      let t = 0
      pupilT = setInterval(() => {
        t++
        const x = t % 3 === 0 ? 5 : t % 3 === 1 ? -5 : 0
        const y = t % 3 === 0 ? -2 : 0
        pX.value = x; pY.value = y; voPX.value = x; voPY.value = y
      }, 650)
    }
  })

  onMounted(() => {
    blinkT = setInterval(() => {
      if (currentMood.value === 'thinking') return
      eyeSc.value = .05; voEyeSc.value = .05
      setTimeout(() => { eyeSc.value = cfg.value.eyeSc; voEyeSc.value = cfg.value.eyeSc }, 130)
    }, 3400)
  })

  onUnmounted(() => {
    clearInterval(blinkT); clearInterval(waveT)
    clearInterval(pupilT); clearInterval(voBodyT)
  })

  return {
    // wave
    waveH, voWaveH,
    // eyes
    eyeSc, pX, pY, voEyeSc, voPX, voPY,
    // voice body
    voArmL, voArmR, voLegL, voLegR, voHeadTilt,
    startBodyAnim, stopBodyAnim,
    // mouth / face
    mouthPath, mouthFill, mouthFOp,
    cheekOp, headTilt, armLRot, armRRot, chestColor,
    browL, browR, voBrowL, voBrowR,
    voMouth, voMouthF, voMouthFOp, voCheek,
  }
}