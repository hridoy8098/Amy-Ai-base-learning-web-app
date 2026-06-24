<template>
  <AppLayout>
    <div class="admin-badges">
      <div class="page-header flex justify-between items-center">
        <h1>🏅 Badge Management</h1>
        <button class="btn btn-primary" @click="showForm=true">+ New Badge</button>
      </div>
      <div class="badges-grid">
        <div v-for="b in badges" :key="b.id" class="badge-card card">
          <div class="badge-icon">{{ b.icon || '🏅' }}</div>
          <div class="badge-name">{{ b.name }}</div>
          <div class="badge-cond text-xs text-muted">{{ b.condition }}</div>
          <div class="chip chip-amber mt-2" v-if="b.xp_reward > 0">+{{ b.xp_reward }} XP</div>
        </div>
      </div>
      <div class="modal-overlay" v-if="showForm" @click.self="showForm=false">
        <div class="modal">
          <h3 class="mb-4">Create Badge</h3>
          <div class="flex flex-col gap-4">
            <div class="form-group"><label class="form-label">Name *</label><input v-model="form.name" type="text" class="form-input" /></div>
            <div class="form-group"><label class="form-label">Icon (emoji)</label><input v-model="form.icon" type="text" class="form-input" placeholder="🏅" /></div>
            <div class="form-group"><label class="form-label">Description</label><textarea v-model="form.description" class="form-input" rows="2"></textarea></div>
            <div class="form-group"><label class="form-label">Condition key</label><input v-model="form.condition" type="text" class="form-input" placeholder="streak_7" /></div>
            <div class="form-group"><label class="form-label">XP Reward</label><input v-model.number="form.xp_reward" type="number" min="0" class="form-input" /></div>
            <div class="flex gap-2"><button class="btn btn-primary" @click="save">Create</button><button class="btn btn-outline" @click="showForm=false">Cancel</button></div>
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
const badges=ref([]),showForm=ref(false)
const form=reactive({name:'',icon:'',description:'',condition:'',xp_reward:0})
async function load(){try{const r=await api.get('/admin/badges');badges.value=r.data}catch{}}
async function save(){try{await api.post('/admin/badges',form);toast.success('Badge created!');showForm.value=false;Object.assign(form,{name:'',icon:'',description:'',condition:'',xp_reward:0});load()}catch{toast.error('Failed')}}
onMounted(load)
</script>
<style scoped>
.admin-badges{display:flex;flex-direction:column;gap:20px}
.badges-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:16px}
.badge-card{text-align:center;padding:20px}
.badge-icon{font-size:36px;margin-bottom:8px}
.badge-name{font-size:14px;font-weight:700;color:var(--text)}
.badge-cond{margin-top:4px}
</style>
