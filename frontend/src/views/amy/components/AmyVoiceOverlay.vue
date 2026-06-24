<template>
  <Teleport to="body">
    <Transition name="vo-fade">
      <div v-if="open" class="voice-overlay" @keydown.esc="$emit('close')">

        <!-- Animated rings -->
        <div class="vo-rings">
          <div class="vo-ring r1" :class="phase"></div>
          <div class="vo-ring r2" :class="phase"></div>
          <div class="vo-ring r3" :class="phase"></div>
        </div>

        <!-- Big Amy robot -->
        <div class="vo-robot-wrap">
          <svg class="vo-amy-svg" viewBox="0 0 420 520" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <radialGradient id="voSG"  cx="50%" cy="40%" r="55%"><stop offset="0%" stop-color="#FFD6B8"/><stop offset="100%" stop-color="#FFBF96"/></radialGradient>
              <radialGradient id="voSG2" cx="50%" cy="30%" r="60%"><stop offset="0%" stop-color="#FFD6B8"/><stop offset="100%" stop-color="#FFBF96"/></radialGradient>
              <radialGradient id="voShG" cx="50%" cy="0%"  r="80%"><stop offset="0%" stop-color="#9FA8DA"/><stop offset="100%" stop-color="#7986CB"/></radialGradient>
            </defs>
            <ellipse cx="210" cy="514" rx="72" ry="8" fill="rgba(0,0,0,0.15)"/>
            <!-- Body -->
            <path d="M158,295 Q153,385 150,500 L270,500 Q267,385 262,295 Z" fill="url(#voShG)" stroke="#7986CB" stroke-width="1.5"/>
            <rect x="191" y="330" width="38" height="26" rx="8" fill="#E8EAF6" stroke="#9FA8DA" stroke-width="1.5"/>
            <circle cx="210" cy="343" r="6" :fill="chestColor"/>
            <path d="M150,468 Q182,458 210,460 Q238,458 270,468 L275,502 L145,502 Z" fill="#7986CB"/>
            <!-- Legs -->
            <g :style="`transform-origin:185px 500px;transform:${voLegL};transition:transform .35s ease`">
              <path d="M178,498 Q172,510 170,516" stroke="#7986CB" stroke-width="26" stroke-linecap="round" fill="none"/>
              <ellipse cx="168" cy="517" rx="17" ry="9" fill="#4A3F9F"/>
            </g>
            <g :style="`transform-origin:235px 500px;transform:${voLegR};transition:transform .35s ease`">
              <path d="M242,498 Q248,510 250,516" stroke="#7986CB" stroke-width="26" stroke-linecap="round" fill="none"/>
              <ellipse cx="252" cy="517" rx="17" ry="9" fill="#4A3F9F"/>
            </g>
            <!-- Arms -->
            <g :style="`transform-origin:172px 300px;transform:${voArmL};transition:transform .4s ease`">
              <path d="M172,300 Q148,355 138,400" stroke="#9FA8DA" stroke-width="26" stroke-linecap="round" fill="none"/>
              <path d="M172,300 Q152,348 144,388" stroke="#FFBF96" stroke-width="18" stroke-linecap="round" fill="none"/>
              <circle cx="140" cy="394" r="14" fill="url(#voSG2)" stroke="#F0A87A" stroke-width="1"/>
            </g>
            <g :style="`transform-origin:248px 300px;transform:${voArmR};transition:transform .4s ease`">
              <path d="M248,300 Q272,355 282,400" stroke="#9FA8DA" stroke-width="26" stroke-linecap="round" fill="none"/>
              <path d="M248,300 Q268,348 276,388" stroke="#FFBF96" stroke-width="18" stroke-linecap="round" fill="none"/>
              <circle cx="280" cy="394" r="14" fill="url(#voSG2)" stroke="#F0A87A" stroke-width="1"/>
            </g>
            <!-- Neck -->
            <rect x="198" y="275" width="24" height="26" rx="7" fill="#FFBF96"/>
            <!-- Head -->
            <g :style="`transform-origin:210px 185px;transform:rotate(${voHeadTilt}deg);transition:transform .5s ease`">
              <ellipse cx="210" cy="175" rx="78" ry="82" fill="#4A3F9F"/>
              <path d="M134,172 Q118,252 124,326 Q140,278 144,260 Q147,240 152,215" fill="#4A3F9F"/>
              <path d="M286,172 Q302,252 296,326 Q280,278 276,260 Q273,240 268,215" fill="#4A3F9F"/>
              <ellipse cx="210" cy="193" rx="65" ry="72" fill="url(#voSG)"/>
              <path d="M145,178 Q153,112 210,107 Q267,112 275,178 Q253,150 210,147 Q167,150 145,178 Z" fill="#5C4FBF"/>
              <path d="M145,178 Q154,152 163,154 Q157,171 155,181 Z" fill="#4A3F9F"/>
              <path d="M275,178 Q266,152 257,154 Q263,171 265,181 Z" fill="#4A3F9F"/>
              <ellipse cx="145" cy="197" rx="11" ry="15" fill="#FFBF96" stroke="#F0A87A" stroke-width="0.5"/>
              <ellipse cx="275" cy="197" rx="11" ry="15" fill="#FFBF96" stroke="#F0A87A" stroke-width="0.5"/>
              <!-- Eyebrows -->
              <path :d="voBrowL" stroke="#4A3F9F" stroke-width="3" fill="none" stroke-linecap="round"/>
              <path :d="voBrowR" stroke="#4A3F9F" stroke-width="3" fill="none" stroke-linecap="round"/>
              <!-- Left eye -->
              <ellipse cx="181" cy="188" rx="18" :ry="voEyeSc * 15" fill="white" stroke="#E0C8B0" stroke-width="0.5"/>
              <ellipse cx="181" cy="188" rx="11" :ry="voEyeSc * 11" fill="#7B6EF6"/>
              <circle :cx="181 + voPX" :cy="188 + voPY" r="6.5" fill="#1a1a2e"/>
              <circle cx="184" cy="182" r="3.5" fill="white" opacity="0.9"/>
              <!-- Lashes left -->
              <path d="M163,175 Q165,168 167,165" stroke="#1a1a2e" stroke-width="1.6" fill="none" stroke-linecap="round"/>
              <path d="M178,168 Q180,161 181,159" stroke="#1a1a2e" stroke-width="1.6" fill="none" stroke-linecap="round"/>
              <path d="M193,173 Q197,167 200,165" stroke="#1a1a2e" stroke-width="1.6" fill="none" stroke-linecap="round"/>
              <!-- Right eye -->
              <ellipse cx="239" cy="188" rx="18" :ry="voEyeSc * 15" fill="white" stroke="#E0C8B0" stroke-width="0.5"/>
              <ellipse cx="239" cy="188" rx="11" :ry="voEyeSc * 11" fill="#7B6EF6"/>
              <circle :cx="239 + voPX" :cy="188 + voPY" r="6.5" fill="#1a1a2e"/>
              <circle cx="242" cy="182" r="3.5" fill="white" opacity="0.9"/>
              <!-- Lashes right -->
              <path d="M220,173 Q218,167 216,165" stroke="#1a1a2e" stroke-width="1.6" fill="none" stroke-linecap="round"/>
              <path d="M236,168 Q235,161 234,159" stroke="#1a1a2e" stroke-width="1.6" fill="none" stroke-linecap="round"/>
              <path d="M251,173 Q254,167 257,165" stroke="#1a1a2e" stroke-width="1.6" fill="none" stroke-linecap="round"/>
              <!-- Nose -->
              <path d="M205,210 Q210,219 215,210" stroke="#F0A87A" stroke-width="1.8" fill="none" stroke-linecap="round"/>
              <!-- Cheeks -->
              <ellipse cx="163" cy="218" rx="18" ry="12" fill="#FFB3BA" :opacity="voCheek"/>
              <ellipse cx="257" cy="218" rx="18" ry="12" fill="#FFB3BA" :opacity="voCheek"/>
              <!-- Mouth -->
              <path :d="voMouth" stroke="#C0726A" stroke-width="3" fill="none" stroke-linecap="round"/>
              <path :d="voMouthF" fill="#E8907A" :opacity="voMouthFOp"/>
            </g>

            <!-- Speaking bars (right side) -->
            <g v-if="phase === 'speaking'">
              <rect v-for="(h, i) in voWaveH" :key="'s'+i"
                :x="300 + i*12" :y="188 - h/2"
                width="7" :height="h" rx="3.5"
                fill="#7b6ef6" opacity="0.85"/>
            </g>
            <!-- Listening bars (left side) -->
            <g v-if="phase === 'listening'">
              <rect v-for="(h, i) in voWaveH" :key="'l'+i"
                :x="60 + i*12" :y="188 - h/2"
                width="7" :height="h" rx="3.5"
                fill="#ff8fab" opacity="0.85"/>
            </g>
          </svg>
        </div>

        <!-- Lang toggle -->
        <div class="vo-lang-toggle">
          <button :class="['vo-lang-btn', lang === 'en-US' ? 'active' : '']" @click="$emit('lang', 'en-US')">🇬🇧 English</button>
          <button :class="['vo-lang-btn', lang === 'bn-BD' ? 'active' : '']" @click="$emit('lang', 'bn-BD')">🇧🇩 বাংলা</button>
        </div>

        <!-- Status -->
        <div class="vo-status">
          <div class="vo-status-dot" :class="phase"></div>
          <span v-if="phase === 'listening'">{{ lang === 'bn-BD' ? 'শুনছি... বলুন' : 'Listening… speak now' }}</span>
          <span v-else-if="phase === 'thinking'">{{ lang === 'bn-BD' ? 'Amy ভাবছে...' : 'Amy is thinking…' }}</span>
          <span v-else-if="phase === 'speaking'">{{ lang === 'bn-BD' ? 'Amy বলছে...' : 'Amy is speaking…' }}</span>
        </div>

        <!-- Transcript & reply bubbles -->
        <div class="vo-transcript" v-if="transcript">"{{ transcript }}"</div>
        <div class="vo-reply" v-if="lastReply && phase === 'speaking'">{{ lastReply }}</div>

        <!-- Close -->
        <button class="vo-close-btn" @click="$emit('close')">
          ✕ {{ lang === 'bn-BD' ? 'শেষ করুন' : 'End conversation' }}
        </button>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  open:       Boolean,
  phase:      String,
  lang:       String,
  transcript: String,
  lastReply:  String,
  // animation
  voWaveH:    Array,
  voEyeSc:    Number,
  voPX:       Number,
  voPY:       Number,
  voArmL:     String,
  voArmR:     String,
  voLegL:     String,
  voLegR:     String,
  voHeadTilt: Number,
  voBrowL:    String,
  voBrowR:    String,
  voMouth:    String,
  voMouthF:   String,
  voMouthFOp: Number,
  voCheek:    Number,
  chestColor: String,
})
defineEmits(['close', 'lang'])
</script>

<style scoped>
.voice-overlay {
  position: fixed; inset: 0; z-index: 9999;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  background: rgba(8,6,24,.97); backdrop-filter: blur(16px);
}
.vo-fade-enter-active { animation: vo-in .38s cubic-bezier(.34,1.56,.64,1); }
.vo-fade-leave-active { animation: vo-in .22s ease reverse; }
@keyframes vo-in { from { opacity:0; transform:scale(.92) } to { opacity:1; transform:scale(1) } }

.vo-rings { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; pointer-events:none; }
.vo-ring  { position:absolute; border-radius:50%; border:1.5px solid rgba(123,110,246,.22); animation:vo-ring-pulse 2.6s ease-out infinite; }
.vo-ring.listening { border-color:rgba(255,143,171,.3); }
.vo-ring.speaking  { border-color:rgba(123,110,246,.35); }
.vo-ring.thinking  { border-color:rgba(255,214,0,.25); }
.r1 { width:300px; height:300px; animation-delay:0s; }
.r2 { width:480px; height:480px; animation-delay:.7s; }
.r3 { width:660px; height:660px; animation-delay:1.4s; }
@keyframes vo-ring-pulse { 0%{transform:scale(.82);opacity:.55} 60%{opacity:.18} 100%{transform:scale(1.18);opacity:0} }

.vo-robot-wrap  { position:relative; z-index:2; }
.vo-amy-svg     { width:min(300px,65vw); height:auto; display:block; filter:drop-shadow(0 0 40px rgba(123,110,246,.4)); animation:vo-float 2.4s ease-in-out infinite; }
@keyframes vo-float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-12px)} }

.vo-lang-toggle { position:relative; z-index:2; display:flex; gap:8px; margin-top:14px; }
.vo-lang-btn    { background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.2); color:rgba(255,255,255,.7); border-radius:20px; padding:6px 16px; font-size:13px; font-weight:600; cursor:pointer; transition:all .2s; }
.vo-lang-btn.active { background:rgba(123,110,246,.3); border-color:#7b6ef6; color:#fff; }

.vo-status      { position:relative; z-index:2; display:flex; align-items:center; gap:10px; margin-top:14px; font-size:15px; font-weight:600; color:rgba(255,255,255,.9); }
.vo-status-dot  { width:10px; height:10px; border-radius:50%; animation:blink 1s infinite; flex-shrink:0; }
.vo-status-dot.listening { background:#ff8fab; box-shadow:0 0 10px #ff8fab; }
.vo-status-dot.speaking  { background:#7b6ef6; box-shadow:0 0 10px #7b6ef6; }
.vo-status-dot.thinking  { background:#ffd600; box-shadow:0 0 8px  #ffd600; }
.vo-status-dot.idle      { background:#555; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }

.vo-transcript { position:relative; z-index:2; margin-top:10px; max-width:420px; text-align:center; font-size:13px; font-style:italic; color:rgba(175,169,236,.85); padding:7px 20px; background:rgba(255,143,171,.1); border:1px solid rgba(255,143,171,.25); border-radius:20px; }
.vo-reply      { position:relative; z-index:2; margin-top:8px; max-width:440px; text-align:center; font-size:14px; color:rgba(200,195,255,.9); padding:8px 22px; background:rgba(123,110,246,.12); border:1px solid rgba(123,110,246,.28); border-radius:20px; line-height:1.5; }
.vo-close-btn  { position:absolute; bottom:28px; background:rgba(255,107,138,.15); border:1px solid rgba(255,107,138,.35); color:rgba(255,143,171,.8); font-size:13px; font-weight:500; padding:8px 22px; border-radius:20px; cursor:pointer; transition:all .2s; }
.vo-close-btn:hover { background:rgba(255,107,138,.28); color:#fff; }
</style>