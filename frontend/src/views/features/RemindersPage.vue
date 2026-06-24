<template>
  <AppLayout>
    <div class="feature-page">
      <div class="feature-header flex justify-between items-center">
        <div><h1>📅 Smart Reminders</h1><p class="text-muted">Set personalized study reminders — never miss a session</p></div>
        <button class="btn btn-primary" @click="showCreate=true">+ Add Reminder</button>
      </div>

      <div v-if="reminders.length===0" class="empty-state mt-6">
        <div class="icon">⏰</div><h3>No reminders set</h3>
        <p>Add reminders to stay consistent with your learning schedule</p>
        <button class="btn btn-primary mt-4" @click="showCreate=true">Add First Reminder</button>
      </div>

      <div v-else class="reminders-list">
        <div v-for="r in reminders" :key="r.id" class="reminder-card card" :class="{inactive:!r.is_active}">
          <div class="r-time">{{ r.reminder_time }}</div>
          <div class="r-info">
            <div class="r-type chip chip-purple">{{ r.message_type.replace(/_/g,' ') }}</div>
            <div class="r-days text-xs text-muted mt-1">{{ r.days?.join(', ') }}</div>
            <div class="r-preview text-sm mt-1">{{ r.preview_message }}</div>
          </div>
          <div class="r-actions">
            <button class="btn btn-icon" :class="r.is_active?'btn-success':'btn-outline'" @click="toggleReminder(r)" title="Toggle">{{ r.is_active?'✅':'⏸️' }}</button>
            <button class="btn btn-icon btn-danger" @click="deleteReminder(r)" title="Delete">🗑️</button>
          </div>
        </div>
      </div>

      <!-- Create Modal -->
      <div class="modal-overlay" v-if="showCreate" @click.self="showCreate=false">
        <div class="modal">
          <h3 class="mb-4">⏰ Add Reminder</h3>
          <div class="form-group mb-3">
            <label class="form-label">Time</label>
            <input type="time" v-model="form.reminder_time" class="form-input" />
          </div>
          <div class="form-group mb-3">
            <label class="form-label">Reminder Type</label>
            <select v-model="form.message_type" class="form-input">
              <option v-for="t in types" :key="t.id" :value="t.id">{{ t.message }}</option>
            </select>
          </div>
          <div class="form-group mb-4">
            <label class="form-label">Days</label>
            <div class="days-picker">
              <button v-for="d in allDays" :key="d" class="day-btn" :class="{active:selectedDays.includes(d)}" @click="toggleDay(d)">{{ d }}</button>
            </div>
          </div>
          <div class="flex gap-3">
            <button class="btn btn-primary flex-1" @click="createReminder">Save Reminder</button>
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
const reminders=ref([]); const showCreate=ref(false)
const allDays=['mon','tue','wed','thu','fri','sat','sun']
const selectedDays=ref([...allDays])
const form=reactive({reminder_time:'08:00',message_type:'daily_practice'})
const types=[
  {id:'daily_practice',message:'🎯 Daily Practice Reminder'},
  {id:'vocab_review',message:'📖 Vocabulary Review'},
  {id:'quiz_time',message:'🧠 Quiz Time'},
  {id:'streak_warning',message:'🔥 Streak Warning'},
  {id:'sleep_recap',message:'🌙 Bedtime Recap'},
  {id:'challenge',message:'⚡ Daily Challenge'},
]
function toggleDay(d){
  const i=selectedDays.value.indexOf(d)
  if(i>-1)selectedDays.value.splice(i,1)
  else selectedDays.value.push(d)
}
async function load(){try{const r=await api.get('/reminders/');reminders.value=r.data}catch{}}
async function createReminder(){
  if(!selectedDays.value.length){toast.error('Select at least one day');return}
  try{const r=await api.post('/reminders/',{...form,days:selectedDays.value.join(',')});reminders.value.push(r.data);showCreate.value=false;toast.success('Reminder created!')}
  catch{toast.error('Failed')}
}
async function toggleReminder(r){try{const res=await api.put(`/reminders/${r.id}/toggle`);r.is_active=res.data.is_active}catch{}}
async function deleteReminder(r){try{await api.delete(`/reminders/${r.id}`);reminders.value=reminders.value.filter(x=>x.id!==r.id);toast.success('Deleted')}catch{}}
onMounted(load)
</script>
<style scoped>
.reminders-list{display:flex;flex-direction:column;gap:12px}
.reminder-card{display:flex;align-items:center;gap:16px;padding:16px 20px;transition:all var(--t)}
.reminder-card.inactive{opacity:.6}
.r-time{font-family:'Outfit',sans-serif;font-size:1.6rem;font-weight:800;color:var(--p);min-width:80px;flex-shrink:0}
.r-info{flex:1}
.r-actions{display:flex;gap:6px;flex-shrink:0}
.days-picker{display:flex;gap:6px;flex-wrap:wrap;margin-top:4px}
.day-btn{padding:5px 10px;border-radius:6px;border:1.5px solid var(--border);background:transparent;color:var(--text2);font-size:12px;cursor:pointer;font-family:'Outfit',sans-serif;font-weight:600;text-transform:uppercase;transition:all var(--t)}
.day-btn.active{border-color:var(--p);background:var(--p-soft);color:var(--p)}
</style>
