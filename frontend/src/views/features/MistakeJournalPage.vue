<template>
  <AppLayout>
    <div class="feature-page">
      <div class="feature-header flex justify-between items-center">
        <div><h1>🔁 Mistake Journal</h1><p class="text-muted">Track grammar mistakes and improve from your errors</p></div>
        <button class="btn btn-primary" @click="loadReport">📊 Weekly Report</button>
      </div>

      <div class="mj-layout">
        <!-- Stats -->
        <div class="stats-grid" style="grid-template-columns:repeat(3,1fr)">
          <div class="stat-card card"><div class="stat-icon">📋</div><div class="stat-value">{{ stats.total_mistakes }}</div><div class="stat-label">Total Mistakes</div></div>
          <div class="stat-card card"><div class="stat-icon">🔢</div><div class="stat-value">{{ stats.total_occurrences }}</div><div class="stat-label">Occurrences</div></div>
          <div class="stat-card card"><div class="stat-icon">🏆</div><div class="stat-value">{{ stats.by_type?.[0]?.type || '—' }}</div><div class="stat-label">Top Error Type</div></div>
        </div>

        <!-- Error type breakdown -->
        <div class="card" v-if="stats.by_type?.length">
          <h3 class="mb-4">Error Type Breakdown</h3>
          <div v-for="t in stats.by_type" :key="t.type" class="error-type-row">
            <span class="et-name">{{ t.type }}</span>
            <div class="et-bar-wrap"><div class="et-bar" :style="{width: (t.count/stats.total_occurrences*100)+'%'}"></div></div>
            <span class="et-count">{{ t.count }}x</span>
          </div>
        </div>

        <!-- Mistakes list -->
        <div class="card">
          <div class="flex justify-between items-center mb-4">
            <h3>All Mistakes</h3>
            <button class="btn btn-outline btn-sm" @click="showAddModal = true">+ Add Mistake</button>
          </div>
          <div v-if="mistakes.length === 0" class="empty-state"><div class="icon">✅</div><h3>No mistakes logged!</h3><p>Keep practicing — mistakes help you improve</p></div>
          <div v-else>
            <div v-for="m in mistakes" :key="m.id" class="mistake-row">
              <div class="mistake-header">
                <span class="mistake-type chip chip-rose">{{ m.error_type }}</span>
                <span class="mistake-count">{{ m.count }}x</span>
              </div>
              <div class="mistake-compare">
                <div class="wrong-ver">❌ {{ m.original }}</div>
                <div class="arrow">→</div>
                <div class="right-ver">✅ {{ m.correction }}</div>
              </div>
              <div class="mistake-exp text-xs text-muted" v-if="m.explanation">💡 {{ m.explanation }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Weekly Report Modal -->
      <div class="modal-overlay" v-if="showReport" @click.self="showReport=false">
        <div class="modal modal-lg">
          <div class="flex justify-between items-center mb-4">
            <h2>📊 Weekly Report</h2>
            <button class="btn btn-ghost btn-icon" @click="showReport=false">✕</button>
          </div>
          <div v-if="reportLoading" class="loading-state"><div class="spinner spinner-lg"></div></div>
          <div v-else-if="report">
            <div class="report-score card mb-4">
              <div class="rs-num">{{ report.weekly_score }}</div>
              <div class="rs-lbl">Weekly Score</div>
            </div>
            <p class="mb-4">{{ report.summary }}</p>
            <div class="grid-2 mb-4">
              <div><h4 class="mb-2">🔧 Improvement Areas</h4>
                <div v-for="a in report.improvement_areas" :key="a" class="report-item">{{ a }}</div></div>
              <div><h4 class="mb-2">🏆 Achievements</h4>
                <div v-for="a in report.achievements" :key="a" class="report-item success">{{ a }}</div></div>
            </div>
            <div class="card" style="background:var(--bg3)">
              <h4 class="mb-2">💬 {{ report.encouragement }}</h4>
              <p class="text-xs text-muted">Recommended: {{ report.recommended_practice?.join(', ') }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Add Mistake Modal -->
      <div class="modal-overlay" v-if="showAddModal" @click.self="showAddModal=false">
        <div class="modal modal-sm">
          <h3 class="mb-4">Add Mistake</h3>
          <div class="form-group mb-3">
            <label class="form-label">Error Type</label>
            <select v-model="newMistake.error_type" class="form-input">
              <option v-for="t in errorTypes" :key="t" :value="t">{{ t }}</option>
            </select>
          </div>
          <div class="form-group mb-3"><label class="form-label">Wrong Version</label><input v-model="newMistake.original" class="form-input" placeholder="e.g. She go to school" /></div>
          <div class="form-group mb-3"><label class="form-label">Correct Version</label><input v-model="newMistake.correction" class="form-input" placeholder="e.g. She goes to school" /></div>
          <div class="form-group mb-4"><label class="form-label">Explanation (optional)</label><input v-model="newMistake.explanation" class="form-input" placeholder="Why is this wrong?" /></div>
          <div class="flex gap-3"><button class="btn btn-primary flex-1" @click="addMistake">Save</button><button class="btn btn-outline flex-1" @click="showAddModal=false">Cancel</button></div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
<script setup>
import { ref, reactive, onMounted } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { toast } from 'vue3-toastify'
import api from '@/api'
const mistakes=ref([]); const stats=ref({total_mistakes:0,total_occurrences:0,by_type:[]})
const showReport=ref(false); const showAddModal=ref(false); const report=ref(null); const reportLoading=ref(false)
const errorTypes=['tense','article','preposition','subject-verb agreement','spelling','punctuation','word order','vocabulary','other']
const newMistake=reactive({error_type:'tense',original:'',correction:'',explanation:''})
async function load() {
  try {
    const [m,s]=await Promise.allSettled([api.get('/mistakes/'),api.get('/mistakes/stats')])
    if(m.status==='fulfilled') mistakes.value=m.value.data
    if(s.status==='fulfilled') stats.value=s.value.data
  } catch {}
}
async function loadReport() {
  showReport.value=true; reportLoading.value=true
  try { const r=await api.get('/mistakes/weekly-report'); report.value=r.data.report } catch {}
  finally { reportLoading.value=false }
}
async function addMistake() {
  if(!newMistake.original||!newMistake.correction){toast.error('Fill required fields');return}
  try { await api.post('/mistakes/add',{...newMistake}); toast.success('Mistake logged!'); showAddModal.value=false; newMistake.original=''; newMistake.correction=''; newMistake.explanation=''; load() } catch {}
}
onMounted(load)
</script>
<style scoped>
.mj-layout{display:flex;flex-direction:column;gap:20px}
.error-type-row{display:flex;align-items:center;gap:12px;padding:8px 0;border-bottom:1px solid var(--border)}
.error-type-row:last-child{border-bottom:none}
.et-name{width:180px;font-size:13px;font-weight:600;color:var(--text);flex-shrink:0}
.et-bar-wrap{flex:1;height:8px;background:var(--bg3);border-radius:99px;overflow:hidden}
.et-bar{height:100%;background:linear-gradient(90deg,var(--rose),#fb7185);border-radius:99px;transition:width .6s ease}
.et-count{font-size:12px;font-weight:700;color:var(--text3);width:32px;text-align:right;flex-shrink:0}
.mistake-row{padding:14px 0;border-bottom:1px solid var(--border)}
.mistake-row:last-child{border-bottom:none}
.mistake-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.mistake-count{font-size:12px;font-weight:700;color:var(--rose);background:rgba(244,63,94,.1);padding:2px 8px;border-radius:99px}
.mistake-compare{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.wrong-ver,.right-ver{font-size:14px;font-weight:600;padding:6px 12px;border-radius:var(--r)}
.wrong-ver{background:rgba(244,63,94,.1);color:var(--rose)}
.right-ver{background:rgba(16,185,129,.1);color:var(--green)}
.arrow{color:var(--text3);font-size:18px}
.mistake-exp{margin-top:6px}
.report-score{text-align:center;padding:20px;background:linear-gradient(135deg,rgba(124,92,191,.1),rgba(157,126,224,.05))}
.rs-num{font-family:'Outfit',sans-serif;font-size:3rem;font-weight:900;color:var(--p)}
.rs-lbl{font-size:13px;color:var(--text3)}
.report-item{padding:6px 10px;background:rgba(244,63,94,.08);color:var(--rose);border-radius:6px;font-size:13px;margin-bottom:6px}
.report-item.success{background:rgba(16,185,129,.08);color:var(--green)}
</style>
