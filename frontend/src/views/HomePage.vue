<template>
  <div class="home-page">
    <!-- Navbar -->
    <nav class="navbar">
      <div class="nav-container">
        <div class="nav-logo">🤖 Amy<span>Learn</span></div>
        <div class="nav-links">
          <router-link to="/courses">Courses</router-link>
          <router-link to="/pricing">Pricing</router-link>
          <router-link to="/login" class="btn btn-outline btn-sm">Login</router-link>
          <router-link to="/register" class="btn btn-primary btn-sm">Get Started Free</router-link>
        </div>
      </div>
    </nav>

    <!-- Hero -->
    <section class="hero">
      <div class="hero-bg">
        <div class="blob b1"></div>
        <div class="blob b2"></div>
      </div>
      <div class="hero-content">
        <div class="hero-badge chip chip-purple">🤖 AI-Powered English Learning</div>
        <h1>Learn English with<br /><span class="gradient-text">Amy AI Tutor</span></h1>
        <p class="hero-desc">Talk to Amy in real-time, take AI-generated quizzes, complete structured courses, and track your progress — all in one place.</p>
        <div class="hero-actions">
          <router-link to="/register" class="btn btn-primary btn-lg">Start Learning Free →</router-link>
          <router-link to="/courses" class="btn btn-outline btn-lg">Browse Courses</router-link>
        </div>
        <div class="hero-stats">
          <div class="hs-item"><div class="hs-val">10K+</div><div class="hs-label">Learners</div></div>
          <div class="hs-div"></div>
          <div class="hs-item"><div class="hs-val">500+</div><div class="hs-label">Lessons</div></div>
          <div class="hs-div"></div>
          <div class="hs-item"><div class="hs-val">98%</div><div class="hs-label">Satisfaction</div></div>
        </div>
      </div>
      <div class="hero-robot">
        <svg viewBox="0 0 420 480" xmlns="http://www.w3.org/2000/svg" class="hero-amy">
          <defs>
            <radialGradient id="hpSkinG" cx="50%" cy="40%" r="55%"><stop offset="0%" stop-color="#FFD6B8"/><stop offset="100%" stop-color="#FFBF96"/></radialGradient>
            <radialGradient id="hpShirtG" cx="50%" cy="0%" r="80%"><stop offset="0%" stop-color="#9FA8DA"/><stop offset="100%" stop-color="#7986CB"/></radialGradient>
          </defs>
          <ellipse cx="210" cy="474" rx="70" ry="8" fill="rgba(0,0,0,0.12)"/>
          <path d="M162,295 Q157,375 154,460 L266,460 Q263,375 258,295 Z" fill="url(#hpShirtG)" stroke="#7986CB" stroke-width="1"/>
          <path d="M186,298 Q210,314 234,298" fill="none" stroke="#C5CAE9" stroke-width="1.5" stroke-linecap="round"/>
          <rect x="193" y="328" width="34" height="22" rx="6" fill="#E8EAF6" stroke="#9FA8DA" stroke-width="1"/>
          <circle cx="210" cy="339" r="5" fill="#ff8fab"/>
          <path d="M154,434 Q182,425 210,427 Q238,425 266,434 L270,462 L150,462 Z" fill="#7986CB"/>
          <g style="transform-origin:175px 298px;transform:rotate(12deg)">
            <path d="M175,298 Q156,343 150,382" stroke="#9FA8DA" stroke-width="22" stroke-linecap="round" fill="none"/>
            <path d="M175,298 Q161,335 156,366" stroke="#FFBF96" stroke-width="16" stroke-linecap="round" fill="none"/>
            <circle cx="151" cy="385" r="12" fill="#FFD6B8" stroke="#F0A87A" stroke-width="1"/>
          </g>
          <g style="transform-origin:245px 298px;transform:rotate(-12deg)">
            <path d="M245,298 Q264,343 270,382" stroke="#9FA8DA" stroke-width="22" stroke-linecap="round" fill="none"/>
            <path d="M245,298 Q259,335 264,366" stroke="#FFBF96" stroke-width="16" stroke-linecap="round" fill="none"/>
            <circle cx="269" cy="385" r="12" fill="#FFD6B8" stroke="#F0A87A" stroke-width="1"/>
          </g>
          <rect x="199" y="276" width="22" height="24" rx="6" fill="#FFBF96"/>
          <ellipse cx="210" cy="178" rx="76" ry="80" fill="#4A3F9F"/>
          <path d="M136,175 Q121,248 126,318 Q141,270 144,254 Q146,234 151,210" fill="#4A3F9F"/>
          <path d="M284,175 Q299,248 294,318 Q279,270 276,254 Q274,234 269,210" fill="#4A3F9F"/>
          <ellipse cx="210" cy="196" rx="63" ry="70" fill="url(#hpSkinG)"/>
          <path d="M147,182 Q154,118 210,113 Q266,118 273,182 Q251,156 210,153 Q169,156 147,182 Z" fill="#5C4FBF"/>
          <ellipse cx="147" cy="200" rx="10" ry="14" fill="#FFBF96"/>
          <ellipse cx="273" cy="200" rx="10" ry="14" fill="#FFBF96"/>
          <circle cx="140" cy="213" r="4" fill="#7b6ef6"/>
          <circle cx="280" cy="213" r="4" fill="#7b6ef6"/>
          <path d="M168,165 Q180,160 192,163" stroke="#4A3F9F" stroke-width="2.5" fill="none" stroke-linecap="round"/>
          <path d="M228,163 Q240,160 252,165" stroke="#4A3F9F" stroke-width="2.5" fill="none" stroke-linecap="round"/>
          <ellipse cx="182" cy="191" rx="16" ry="14" fill="white" stroke="#E0C8B0" stroke-width="0.5"/>
          <ellipse cx="182" cy="191" rx="10" ry="10" fill="#7B6EF6"/>
          <circle cx="182" cy="191" r="5.5" fill="#1a1a2e"/>
          <circle cx="185" cy="186" r="3" fill="white" opacity="0.9"/>
          <path d="M167,179 Q168,174 170,171" stroke="#1a1a2e" stroke-width="1.4" fill="none" stroke-linecap="round"/>
          <path d="M180,174 Q182,169 183,167" stroke="#1a1a2e" stroke-width="1.4" fill="none" stroke-linecap="round"/>
          <path d="M193,179 Q196,175 198,173" stroke="#1a1a2e" stroke-width="1.4" fill="none" stroke-linecap="round"/>
          <ellipse cx="238" cy="191" rx="16" ry="14" fill="white" stroke="#E0C8B0" stroke-width="0.5"/>
          <ellipse cx="238" cy="191" rx="10" ry="10" fill="#7B6EF6"/>
          <circle cx="238" cy="191" r="5.5" fill="#1a1a2e"/>
          <circle cx="241" cy="186" r="3" fill="white" opacity="0.9"/>
          <path d="M223,179 Q222,174 220,171" stroke="#1a1a2e" stroke-width="1.4" fill="none" stroke-linecap="round"/>
          <path d="M236,174 Q235,169 234,167" stroke="#1a1a2e" stroke-width="1.4" fill="none" stroke-linecap="round"/>
          <path d="M249,179 Q252,175 254,173" stroke="#1a1a2e" stroke-width="1.4" fill="none" stroke-linecap="round"/>
          <path d="M206,212 Q210,220 214,212" stroke="#F0A87A" stroke-width="1.5" fill="none" stroke-linecap="round"/>
          <ellipse cx="165" cy="220" rx="17" ry="11" fill="#FFB3BA" opacity="0.5"/>
          <ellipse cx="255" cy="220" rx="17" ry="11" fill="#FFB3BA" opacity="0.5"/>
          <path d="M190,228 Q210,244 230,228" stroke="#C0726A" stroke-width="2.5" fill="none" stroke-linecap="round"/>
          <path d="M190,228 Q210,244 230,228 Q210,255 190,228 Z" fill="#E8907A" opacity="0.55"/>
        </svg>
      </div>
    </section>

    <!-- Features -->
    <section class="features">
      <div class="section-container">
        <h2 class="section-title">Why choose Amy?</h2>
        <div class="features-grid">
          <div class="feature-card">
            <div class="fc-icon">🤖</div>
            <h3>AI Tutor</h3>
            <p>Chat with Amy in English or Bangla. Voice conversation, grammar correction, and instant feedback.</p>
          </div>
          <div class="feature-card">
            <div class="fc-icon">📚</div>
            <h3>Structured Courses</h3>
            <p>Video lessons, PDFs, interactive content — learn at your own pace with professional courses.</p>
          </div>
          <div class="feature-card">
            <div class="fc-icon">🧠</div>
            <h3>AI Quiz Generator</h3>
            <p>Type any topic and get an instant quiz. Track your score and improve weak areas.</p>
          </div>
          <div class="feature-card">
            <div class="fc-icon">🏆</div>
            <h3>Gamification</h3>
            <p>Earn XP, maintain streaks, collect badges, and compete on the leaderboard.</p>
          </div>
          <div class="feature-card">
            <div class="fc-icon">🎓</div>
            <h3>Certificates</h3>
            <p>Complete courses and earn verified certificates you can share on LinkedIn.</p>
          </div>
          <div class="feature-card">
            <div class="fc-icon">🌍</div>
            <h3>Multilingual</h3>
            <p>Amy supports both English and Bangla. Learn in your preferred language.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="leaderboard-section" v-if="leaderboard.length">
      <div class="section-container">
        <div class="leaderboard-head">
          <div>
            <h2 class="section-title left">Top Learners</h2>
            <p class="leaderboard-sub">All users er moddhe jara sabcheye beshi XP earn koreche tader live ranking.</p>
          </div>
          <router-link :to="leaderboardCta" class="btn btn-outline btn-sm">View Leaderboard</router-link>
        </div>
        <div class="home-leaderboard-grid">
          <div v-for="user in leaderboard" :key="user.rank" class="home-lb-card">
            <div class="home-lb-rank">#{{ user.rank }}</div>
            <div class="home-lb-name">{{ user.name }}</div>
            <div class="home-lb-xp">{{ user.xp }} XP</div>
            <div class="home-lb-meta">Level {{ user.level }} - {{ user.streak }} day streak</div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="cta">
      <div class="cta-card">
        <h2>Start your English journey today</h2>
        <p>Join thousands of learners improving their English with Amy AI Tutor.</p>
        <router-link to="/register" class="btn btn-primary btn-lg">Get Started — It's Free! 🚀</router-link>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <div class="footer-container">
        <div class="footer-logo">🤖 Amy<span>Learn</span></div>
        <div class="footer-links">
          <router-link to="/courses">Courses</router-link>
          <router-link to="/pricing">Pricing</router-link>
          <router-link to="/login">Login</router-link>
          <router-link to="/register">Register</router-link>
        </div>
        <p class="footer-copy">© 2025 Amy Learning. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

import api from '@/api'
import { useAuthStore } from '@/store/auth'
import { useThemeStore } from '@/store/theme'

const auth = useAuthStore()
const theme = useThemeStore()
const leaderboard = ref([])
const leaderboardCta = computed(() => auth.isLoggedIn ? '/leaderboard' : '/login')

onMounted(async () => {
  theme.init()
  try {
    const response = await api.get('/users/leaderboard', { params: { limit: 4 } })
    leaderboard.value = response.data
  } catch {
    leaderboard.value = []
  }
})
</script>

<style scoped>
.home-page { min-height: 100vh; background: var(--bg); }

/* Navbar */
.navbar { position: sticky; top: 0; z-index: 100; background: var(--bg2); border-bottom: 1px solid var(--border); backdrop-filter: blur(12px); }
.nav-container { max-width: 1200px; margin: 0 auto; padding: 0 24px; height: 64px; display: flex; align-items: center; justify-content: space-between; }
.nav-logo { font-size: 20px; font-weight: 800; color: var(--text); }
.nav-logo span { color: var(--p); }
.nav-links { display: flex; align-items: center; gap: 20px; }
.nav-links a:not(.btn) { font-size: 14px; font-weight: 500; color: var(--text2); text-decoration: none; transition: color var(--t); }
.nav-links a:not(.btn):hover { color: var(--p); }

/* Hero */
.hero { min-height: calc(100vh - 64px); display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; padding: 60px 24px; }
.hero-bg { position: absolute; inset: 0; pointer-events: none; }
.blob { position: absolute; border-radius: 50%; filter: blur(100px); opacity: 0.12; }
.b1 { width: 600px; height: 600px; background: var(--p); top: -200px; left: -100px; }
.b2 { width: 500px; height: 500px; background: #a78bfa; bottom: -200px; right: -100px; }
.hero-content { max-width: 560px; position: relative; z-index: 1; }
.hero-badge { margin-bottom: 20px; display: inline-flex; }
.hero-content h1 { font-size: clamp(2rem, 5vw, 3.5rem); font-weight: 900; line-height: 1.1; margin-bottom: 20px; }
.gradient-text { background: linear-gradient(135deg, var(--p), #a78bfa, var(--rose)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.hero-desc { font-size: 17px; color: var(--text2); line-height: 1.7; margin-bottom: 32px; }
.hero-actions { display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 40px; }
.hero-stats { display: flex; align-items: center; gap: 20px; }
.hs-item { text-align: center; }
.hs-val { font-size: 24px; font-weight: 900; color: var(--p); }
.hs-label { font-size: 12px; color: var(--text3); }
.hs-div { width: 1px; height: 36px; background: var(--border); }
.hero-robot { flex-shrink: 0; position: relative; z-index: 1; }
.hero-amy { width: clamp(200px, 30vw, 340px); height: auto; animation: hero-float 3s ease-in-out infinite; filter: drop-shadow(0 20px 40px rgba(123,110,246,0.25)); }
@keyframes hero-float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-16px)} }

/* Features */
.features { padding: 80px 24px; }
.section-container { max-width: 1200px; margin: 0 auto; }
.section-title { text-align: center; margin-bottom: 48px; }
.features-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.feature-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--r2); padding: 28px; transition: all var(--t); }
.feature-card:hover { transform: translateY(-4px); box-shadow: var(--shadow2); border-color: var(--border2); }
.fc-icon { font-size: 36px; margin-bottom: 14px; }
.feature-card h3 { margin-bottom: 8px; }
.feature-card p { font-size: 14px; color: var(--text3); line-height: 1.65; margin: 0; }

.leaderboard-section { padding: 20px 24px 80px; }
.leaderboard-head { display: flex; align-items: end; justify-content: space-between; gap: 16px; margin-bottom: 24px; }
.section-title.left { text-align: left; margin-bottom: 8px; }
.leaderboard-sub { color: var(--text3); margin: 0; }
.home-leaderboard-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; }
.home-lb-card {
  background: linear-gradient(180deg, rgba(123, 110, 246, 0.08), var(--card));
  border: 1px solid var(--border);
  border-radius: var(--r2);
  padding: 24px 20px;
  text-align: center;
}
.home-lb-rank { font-size: 28px; font-weight: 900; color: var(--p); }
.home-lb-name { font-size: 16px; font-weight: 800; color: var(--text); margin-top: 10px; }
.home-lb-xp { font-size: 22px; font-weight: 900; color: var(--amber); margin-top: 8px; }
.home-lb-meta { font-size: 12px; color: var(--text3); margin-top: 6px; }

/* CTA */
.cta { padding: 60px 24px; }
.cta-card { max-width: 700px; margin: 0 auto; text-align: center; background: linear-gradient(135deg, var(--p), #a78bfa); border-radius: var(--r3); padding: 60px 40px; color: #fff; }
.cta-card h2 { color: #fff; margin-bottom: 12px; }
.cta-card p  { color: rgba(255,255,255,0.85); margin-bottom: 28px; font-size: 16px; }
.cta-card .btn-primary { background: #fff; color: var(--p); box-shadow: none; }

/* Footer */
.footer { padding: 40px 24px; border-top: 1px solid var(--border); }
.footer-container { max-width: 1200px; margin: 0 auto; text-align: center; display: flex; flex-direction: column; align-items: center; gap: 16px; }
.footer-logo { font-size: 18px; font-weight: 800; color: var(--text); }
.footer-logo span { color: var(--p); }
.footer-links { display: flex; gap: 20px; flex-wrap: wrap; justify-content: center; }
.footer-links a { font-size: 14px; color: var(--text3); text-decoration: none; transition: color var(--t); }
.footer-links a:hover { color: var(--p); }
.footer-copy { font-size: 13px; color: var(--text3); }

@media (max-width: 900px) {
  .hero { flex-direction: column; text-align: center; gap: 40px; }
  .hero-actions { justify-content: center; }
  .hero-stats { justify-content: center; }
  .features-grid { grid-template-columns: 1fr 1fr; }
  .home-leaderboard-grid { grid-template-columns: 1fr 1fr; }
  .leaderboard-head { align-items: flex-start; flex-direction: column; }
  .hero-robot { order: -1; }
}
@media (max-width: 600px) {
  .features-grid { grid-template-columns: 1fr; }
  .home-leaderboard-grid { grid-template-columns: 1fr; }
  .nav-links .btn-outline { display: none; }
}
</style>
