<template>
  <svg
    :width="size" :height="Math.round(size * 1.17)"
    viewBox="0 0 420 480"
    xmlns="http://www.w3.org/2000/svg"
    :class="['amy-svg', isSpeaking ? 'speaking-bob' : '', mood === 'excited' ? 'excited-bob' : '']"
  >
    <defs>
      <radialGradient id="hSG"  cx="50%" cy="40%" r="55%"><stop offset="0%" stop-color="#FFD6B8"/><stop offset="100%" stop-color="#FFBF96"/></radialGradient>
      <radialGradient id="hSG2" cx="50%" cy="30%" r="60%"><stop offset="0%" stop-color="#FFD6B8"/><stop offset="100%" stop-color="#FFBF96"/></radialGradient>
      <radialGradient id="hShG" cx="50%" cy="0%"  r="80%"><stop offset="0%" stop-color="#9FA8DA"/><stop offset="100%" stop-color="#7986CB"/></radialGradient>
    </defs>

    <!-- Shadow -->
    <ellipse cx="210" cy="474" rx="60" ry="6" fill="rgba(0,0,0,0.1)"/>

    <!-- Body -->
    <path d="M162,295 Q157,375 154,458 L266,458 Q263,375 258,295 Z" fill="url(#hShG)" stroke="#7986CB" stroke-width="1"/>
    <rect x="193" y="328" width="34" height="22" rx="6" fill="#E8EAF6" stroke="#9FA8DA" stroke-width="1"/>
    <circle cx="210" cy="339" r="5" :fill="chestColor"/>
    <path d="M154,432 Q182,423 210,425 Q238,423 266,432 L270,460 L150,460 Z" fill="#7986CB"/>

    <!-- Arms -->
    <g :style="`transform-origin:175px 298px;transform:${armLRot};transition:transform .5s ease`">
      <path d="M175,298 Q156,343 150,382" stroke="#9FA8DA" stroke-width="22" stroke-linecap="round" fill="none"/>
      <path d="M175,298 Q161,335 156,366" stroke="#FFBF96" stroke-width="16" stroke-linecap="round" fill="none"/>
      <circle cx="151" cy="385" r="12" fill="url(#hSG2)" stroke="#F0A87A" stroke-width="1"/>
    </g>
    <g :style="`transform-origin:245px 298px;transform:${armRRot};transition:transform .5s ease`">
      <path d="M245,298 Q264,343 270,382" stroke="#9FA8DA" stroke-width="22" stroke-linecap="round" fill="none"/>
      <path d="M245,298 Q259,335 264,366" stroke="#FFBF96" stroke-width="16" stroke-linecap="round" fill="none"/>
      <circle cx="269" cy="385" r="12" fill="url(#hSG2)" stroke="#F0A87A" stroke-width="1"/>
    </g>

    <!-- Neck -->
    <rect x="199" y="276" width="22" height="24" rx="6" fill="#FFBF96"/>

    <!-- Head group -->
    <g :style="`transform-origin:210px 185px;transform:rotate(${headTilt}deg);transition:transform .5s ease`">
      <ellipse cx="210" cy="178" rx="76" ry="80" fill="#4A3F9F"/>
      <path d="M136,175 Q121,248 126,318 Q141,270 144,254 Q146,234 151,210" fill="#4A3F9F"/>
      <path d="M284,175 Q299,248 294,318 Q279,270 276,254 Q274,234 269,210" fill="#4A3F9F"/>
      <ellipse cx="210" cy="196" rx="63" ry="70" fill="url(#hSG)"/>
      <path d="M147,182 Q154,118 210,113 Q266,118 273,182 Q251,156 210,153 Q169,156 147,182 Z" fill="#5C4FBF"/>
      <!-- Ears -->
      <ellipse cx="147" cy="200" rx="10" ry="14" fill="#FFBF96"/>
      <ellipse cx="273" cy="200" rx="10" ry="14" fill="#FFBF96"/>
      <circle cx="140" cy="213" r="4" fill="#7b6ef6"/>
      <circle cx="280" cy="213" r="4" fill="#7b6ef6"/>
      <!-- Eyebrows -->
      <path :d="browL" stroke="#4A3F9F" stroke-width="2.5" fill="none" stroke-linecap="round"/>
      <path :d="browR" stroke="#4A3F9F" stroke-width="2.5" fill="none" stroke-linecap="round"/>
      <!-- Left eye -->
      <ellipse cx="182" cy="191" rx="16" :ry="14 * eyeSc" fill="white" stroke="#E0C8B0" stroke-width="0.5"/>
      <ellipse cx="182" cy="191" rx="10" :ry="10 * eyeSc" fill="#7B6EF6"/>
      <circle :cx="182 + pX" :cy="191 + pY" r="5.5" fill="#1a1a2e"/>
      <circle cx="185" cy="186" r="3" fill="white" opacity="0.9"/>
      <!-- Right eye -->
      <ellipse cx="238" cy="191" rx="16" :ry="14 * eyeSc" fill="white" stroke="#E0C8B0" stroke-width="0.5"/>
      <ellipse cx="238" cy="191" rx="10" :ry="10 * eyeSc" fill="#7B6EF6"/>
      <circle :cx="238 + pX" :cy="191 + pY" r="5.5" fill="#1a1a2e"/>
      <circle cx="241" cy="186" r="3" fill="white" opacity="0.9"/>
      <!-- Nose dot -->
      <path d="M206,212 Q210,220 214,212" stroke="#F0A87A" stroke-width="1.5" fill="none" stroke-linecap="round"/>
      <!-- Cheeks -->
      <ellipse cx="165" cy="220" rx="17" ry="11" fill="#FFB3BA" :opacity="cheekOp"/>
      <ellipse cx="255" cy="220" rx="17" ry="11" fill="#FFB3BA" :opacity="cheekOp"/>
      <!-- Mouth -->
      <path :d="mouthPath" stroke="#C0726A" stroke-width="2.5" fill="none" stroke-linecap="round"/>
      <path :d="mouthFill" fill="#E8907A" :opacity="mouthFOp"/>
    </g>

    <!-- Speaking wave bars -->
    <g v-if="isSpeaking || isLoading">
      <rect v-for="(h, i) in waveH" :key="i"
        :x="293 + i * 10" :y="185 - h / 2"
        width="5" :height="h" rx="2.5"
        fill="#7b6ef6" opacity="0.8"/>
    </g>
  </svg>
</template>

<script setup>
defineProps({
  size:      { type: Number, default: 82 },
  mood:      { type: String, default: 'happy' },
  isSpeaking:{ type: Boolean, default: false },
  isLoading: { type: Boolean, default: false },
  // animation values from useAmyAnimation
  waveH:     { type: Array,   default: () => [8,14,20,14,8] },
  eyeSc:     { type: Number,  default: 1 },
  pX:        { type: Number,  default: 0 },
  pY:        { type: Number,  default: 0 },
  mouthPath: { type: String,  default: 'M190,228 Q210,244 230,228' },
  mouthFill: { type: String,  default: '' },
  mouthFOp:  { type: Number,  default: 0 },
  cheekOp:   { type: Number,  default: 0.5 },
  headTilt:  { type: Number,  default: 0 },
  armLRot:   { type: String,  default: 'rotate(12deg)' },
  armRRot:   { type: String,  default: 'rotate(-12deg)' },
  chestColor:{ type: String,  default: '#ff8fab' },
  browL:     { type: String,  default: 'M168,165 Q180,160 192,163' },
  browR:     { type: String,  default: 'M228,163 Q240,160 252,165' },
})
</script>

<style scoped>
.amy-svg { display: block; overflow: visible; }
@keyframes speaking-bob { 0%,100% { transform:translateY(0) } 50% { transform:translateY(-3px) } }
@keyframes excited-bob  { 0%,100% { transform:translateY(0) } 50% { transform:translateY(-5px) } }
.amy-svg.speaking-bob { animation: speaking-bob .5s ease infinite; }
.amy-svg.excited-bob  { animation: excited-bob  .3s ease infinite; }
</style>