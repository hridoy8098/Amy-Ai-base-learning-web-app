<template>
  <AppLayout>
    <div class="feature-page">
      <div class="feature-header">
        <h1>📜 Micro Certificates</h1>
        <p class="text-muted">Earn skill badges and share on LinkedIn — showcase your English progress</p>
      </div>

      <div class="mc-tabs tabs mb-5">
        <button class="tab" :class="{active:tab==='my'}" @click="tab='my'">My Certificates</button>
        <button class="tab" :class="{active:tab==='eligible'}" @click="tab='eligible'">Eligible to Claim</button>
        <button class="tab" :class="{active:tab==='all'}" @click="tab='all'">All Skills</button>
      </div>

      <!-- My Certs -->
      <div v-if="tab==='my'">
        <div v-if="myCerts.length === 0" class="empty-state"><div class="icon">🏅</div><h3>No certificates yet</h3><p>Earn XP to claim your first micro-certificate</p></div>
        <div v-else class="certs-grid">
          <div v-for="c in myCerts" :key="c.id" class="cert-card card">
            <div class="cert-badge">🏅</div>
            <h3>{{ c.skill_name }}</h3>
            <div class="chip chip-purple cert-code">{{ c.cert_code }}</div>
            <div class="text-xs text-muted mt-2">Issued: {{ new Date(c.issued_at).toLocaleDateString() }}</div>
            <button class="btn btn-outline btn-sm w-full mt-3" @click="shareLinkedIn(c)">🔗 Share on LinkedIn</button>
          </div>
        </div>
      </div>

      <!-- Eligible -->
      <div v-if="tab==='eligible'">
        <div v-if="eligible.length === 0" class="empty-state"><div class="icon">⭐</div><h3>No eligible certificates</h3><p>Earn more XP to unlock certificates</p></div>
        <div v-else class="certs-grid">
          <div v-for="s in eligible" :key="s.id" class="cert-card card eligible">
            <div class="cert-badge">{{ s.icon }}</div>
            <h3>{{ s.name }}</h3>
            <p class="text-sm text-muted">{{ s.requirement }}</p>
            <div class="cert-xp chip chip-amber mt-2">{{ s.xp_needed }} XP needed</div>
            <button class="btn btn-primary btn-sm w-full mt-3" @click="claimCert(s)" :disabled="claiming===s.id">
              <span class="spinner" v-if="claiming===s.id"></span>
              <span v-else>🏅 Claim Certificate</span>
            </button>
          </div>
        </div>
      </div>

      <!-- All Skills -->
      <div v-if="tab==='all'" class="skills-grid">
        <div v-for="s in allSkills" :key="s.id" class="skill-card card" :class="{earned: earnedIds.has(s.id)}">
          <div class="skill-icon">{{ s.icon }}</div>
          <div class="skill-info">
            <div class="skill-name">{{ s.name }}</div>
            <div class="skill-req text-xs text-muted">{{ s.requirement }}</div>
            <div class="skill-xp chip chip-purple mt-1">{{ s.xp_needed }} XP</div>
          </div>
          <div class="skill-status">
            <span v-if="earnedIds.has(s.id)" class="chip chip-green">✅ Earned</span>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { toast } from 'vue3-toastify'
import api from '@/api'
const tab=ref('my'); const myCerts=ref([]); const eligible=ref([]); const allSkills=ref([])
const claiming=ref(null)
const earnedIds=computed(()=>new Set(myCerts.value.map(c=>c.skill_id)))
async function load(){
  try{
    const[m,e,a]=await Promise.allSettled([api.get('/micro-cert/my-certs'),api.get('/micro-cert/eligible'),api.get('/micro-cert/skills')])
    if(m.status==='fulfilled')myCerts.value=m.value.data
    if(e.status==='fulfilled')eligible.value=e.value.data
    if(a.status==='fulfilled')allSkills.value=a.value.data
  }catch{}
}
async function claimCert(s){
  claiming.value=s.id
  try{const r=await api.post(`/micro-cert/claim/${s.id}`);toast.success(r.data.message);load()}
  catch(e){toast.error(e.response?.data?.detail||'Failed to claim')}finally{claiming.value=null}
}
function shareLinkedIn(c){
  const text=encodeURIComponent(`I just earned the '${c.skill_name}' micro-certificate on Amy Learning Platform! #EnglishLearning #AmyLearn`)
  window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(window.location.origin+c.share_url)}&summary=${text}`,'_blank')
}
onMounted(load)
</script>
<style scoped>
.certs-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px}
.cert-card{text-align:center;padding:24px 16px;transition:all var(--t2)}
.cert-card.eligible{border-color:var(--border2);background:linear-gradient(135deg,rgba(124,92,191,.04),rgba(157,126,224,.02))}
.cert-badge{font-size:3rem;margin-bottom:10px}
.cert-code{font-family:'JetBrains Mono',monospace;font-size:10px;margin:8px auto 0;display:inline-block}
.cert-xp{display:inline-block}
.skills-grid{display:flex;flex-direction:column;gap:10px}
.skill-card{display:flex;align-items:center;gap:14px;padding:14px 18px}
.skill-card.earned{background:rgba(16,185,129,.04);border-color:rgba(16,185,129,.2)}
.skill-icon{font-size:1.8rem;flex-shrink:0}
.skill-info{flex:1}
.skill-name{font-size:14px;font-weight:600;color:var(--text)}
.skill-req{margin-top:2px}
</style>
