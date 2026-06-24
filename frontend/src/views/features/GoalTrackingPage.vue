<template>
  <AppLayout>
    <div class="feature-page">
      <div class="feature-header flex justify-between items-center">
        <div><h1>🎯 Goal Tracking</h1><p class="text-muted">Set IELTS/TOEFL goals and get AI-personalized study plans</p></div>
        <button class="btn btn-primary" @click="showCreate=true">+ New Goal</button>
      </div>

      <div v-if="loading" class="loading-state"><div class="spinner spinner-lg"></div></div>

      <!-- Active Goals -->
      <div v-else-if="goals.length" class="goals-grid">
        <div v-for="g in goals" :key="g.id" class="card goal-card">
          <div class="goal-top">
            <div class="goal-icon">{{ goalIcon(g.goal_type) }}</div>
            <div class="goal-info">
              <h3>{{ goalName(g.goal_type) }}</h3>
              <div class="goal-meta">
                <span v-if="g.target_score" class="chip chip-purple">Target: {{ g.target_score }}</span>
                <span v-if="g.deadline" class="chip chip-amber">📅 {{ g.deadline?.slice(0,10) }}</span>
              </div>
            </div>
          </div>
          <div class="goal-progress mt-4">
            <div class="flex justify-between text-xs text-muted mb-1"><span>Progress</span><span>{{ g.progress_pct?.toFixed(0) }}%</span></div>
            <div class="progress-bar"><div class="progress-fill" :style="{width:g.progress_pct+'%'}"></div></div>
          </div>
          <div class="goal-plan" v-if="g.study_plan?.daily_tasks?.length">
            <h4 class="mt-3 mb-2">📋 Daily Tasks</h4>
            <div v-for="task in g.study_plan.daily_tasks?.slice(0,3)" :key="task" class="plan-task">✓ {{ task }}</div>
          </div>
          <div class="goal-actions mt-3">
            <input type="range" v-model.number="g.progress_pct" min="0" max="100" class="progress-slider" @change="updateProgress(g)" />
          </div>
        </div>
      </div>

      <!-- Empty -->
      <div v-else class="empty-state">
        <div class="icon">🏁</div>
        <h3>No goals set yet</h3>
        <p>Set a learning goal and get a personalized AI study plan</p>
        <button class="btn btn-primary mt-4" @click="showCreate=true">Create Your First Goal</button>
      </div>

      <!-- Goal types -->
      <div class="card mt-4">
        <h3 class="mb-4">Available Goal Types</h3>
        <div class="gtype-grid">
          <div v-for="t in goalTypes" :key="t.id" class="gtype-card" @click="quickCreate(t)">
            <div class="gtype-icon">{{ t.icon }}</div>
            <div class="gtype-name">{{ t.name }}</div>
            <div class="gtype-desc text-xs text-muted">{{ t.description }}</div>
          </div>
        </div>
      </div>

      <!-- Create Modal -->
      <div class="modal-overlay" v-if="showCreate" @click.self="showCreate=false">
        <div class="modal">
          <h3 class="mb-4">🎯 Create New Goal</h3>
          <div class="form-group mb-3">
            <label class="form-label">Goal Type</label>
            <select v-model="form.goal_type" class="form-input">
              <option v-for="t in goalTypes" :key="t.id" :value="t.id">{{ t.icon }} {{ t.name }}</option>
            </select>
          </div>
          <div class="form-group mb-3"><label class="form-label">Target Score (optional)</label><input v-model.number="form.target_score" type="number" class="form-input" placeholder="e.g. 7.0 for IELTS" /></div>
          <div class="form-group mb-3"><label class="form-label">Deadline (optional)</label><input v-model="form.deadline" type="date" class="form-input" /></div>
          <div class="form-group mb-4">
            <label class="form-label">Current Level</label>
            <select v-model="form.current_level" class="form-input">
              <option value="beginner">Beginner</option>
              <option value="elementary">Elementary</option>
              <option value="intermediate">Intermediate</option>
              <option value="upper-intermediate">Upper-Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
          <div class="flex gap-3">
            <button class="btn btn-primary flex-1" @click="createGoal" :disabled="creating">
              <span class="spinner" v-if="creating"></span>
              <span v-else>Create & Get Study Plan 🤖</span>
            </button>
            <button class="btn btn-outline" @click="showCreate=false">Cancel</button>
          </div>
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
const goals=ref([]); const loading=ref(true); const showCreate=ref(false); const creating=ref(false)
const goalTypes=ref([
  {id:'ielts',icon:'🎓',name:'IELTS Prep',description:'Band 6.0–8.0'},
  {id:'toefl',icon:'📝',name:'TOEFL Prep',description:'Score 80–120'},
  {id:'business',icon:'💼',name:'Business English',description:'Professional communication'},
  {id:'travel',icon:'✈️',name:'Travel English',description:'Confident traveling'},
  {id:'general',icon:'📚',name:'General Fluency',description:'Everyday English'},
  {id:'interview',icon:'🤝',name:'Job Interview',description:'Get your dream job'},
])
const form=reactive({goal_type:'ielts',target_score:null,deadline:'',current_level:'intermediate'})
function goalIcon(t){return goalTypes.value.find(g=>g.id===t)?.icon||'🎯'}
function goalName(t){return goalTypes.value.find(g=>g.id===t)?.name||t}
function quickCreate(t){form.goal_type=t.id;showCreate.value=true}
async function load(){try{const r=await api.get('/goals/');goals.value=r.data}catch{}finally{loading.value=false}}
async function createGoal(){
  creating.value=true
  try{const r=await api.post('/goals/create',{...form});goals.value.push(r.data);showCreate.value=false;toast.success('Goal created with AI study plan! 🎉')}
  catch(e){toast.error('Failed to create goal')}finally{creating.value=false}
}
async function updateProgress(g){try{await api.put(`/goals/${g.id}/progress?progress=${g.progress_pct}`);toast.success('Progress updated!')}catch{}}
onMounted(load)
</script>
<style scoped>
.goals-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:20px;margin-bottom:20px}
.goal-card{padding:20px}
.goal-top{display:flex;gap:14px;align-items:flex-start}
.goal-icon{font-size:2rem;flex-shrink:0}
.goal-info{flex:1}
.goal-info h3{margin-bottom:6px}
.goal-meta{display:flex;gap:6px;flex-wrap:wrap}
.goal-plan{background:var(--bg3);border-radius:var(--r);padding:10px 12px}
.plan-task{font-size:12.5px;color:var(--text2);padding:3px 0}
.progress-slider{width:100%;accent-color:var(--p);cursor:pointer}
.gtype-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}
.gtype-card{padding:16px;background:var(--bg3);border-radius:var(--r2);cursor:pointer;text-align:center;transition:all var(--t);border:1px solid transparent}
.gtype-card:hover{border-color:var(--p);background:var(--p-soft);transform:translateY(-2px)}
.gtype-icon{font-size:1.8rem;margin-bottom:6px}
.gtype-name{font-size:13px;font-weight:600;color:var(--text);margin-bottom:3px}
</style>
