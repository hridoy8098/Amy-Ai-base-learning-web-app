<template>
  <AppLayout>
    <div>
      <div class="flex justify-between items-center mb-6">
        <h1>🔔 Notifications</h1>
        <button class="btn btn-outline btn-sm" @click="markAll" v-if="notifs.some(n=>!n.is_read)">Mark all read</button>
      </div>
      <div class="notif-list card" v-if="notifs.length>0">
        <div v-for="n in notifs" :key="n.id" class="notif-item" :class="{unread:!n.is_read}" @click="markRead(n)">
          <div class="notif-dot" :class="n.type"></div>
          <div class="notif-body">
            <div class="notif-title">{{ n.title }}</div>
            <div class="notif-msg">{{ n.message }}</div>
            <div class="notif-time">{{ new Date(n.created_at).toLocaleString() }}</div>
          </div>
        </div>
      </div>
      <div class="empty-state" v-else><div class="icon">🔔</div><h3>No notifications</h3></div>
    </div>
  </AppLayout>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import api from '@/api'
const notifs=ref([])
async function load(){try{const r=await api.get('/users/notifications');notifs.value=r.data}catch{}}
async function markRead(n){if(n.is_read)return;n.is_read=true;try{await api.put(`/users/notifications/${n.id}/read`)}catch{}}
async function markAll(){try{await api.post('/users/notifications/read-all');notifs.value.forEach(n=>n.is_read=true)}catch{}}
onMounted(load)
</script>
<style scoped>
.notif-list{padding:0;overflow:hidden}
.notif-item{display:flex;align-items:flex-start;gap:12px;padding:16px 20px;border-bottom:1px solid var(--border);cursor:pointer;transition:background .15s}
.notif-item:last-child{border-bottom:none}
.notif-item:hover{background:var(--bg3)}
.notif-item.unread{background:var(--p-soft)}
.notif-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0;margin-top:5px}
.notif-dot.info{background:var(--blue)}.notif-dot.success{background:var(--green)}.notif-dot.warning{background:var(--amber)}
.notif-body{flex:1}
.notif-title{font-size:14px;font-weight:600;color:var(--text)}
.notif-msg{font-size:13px;color:var(--text2);margin-top:2px}
.notif-time{font-size:11px;color:var(--text3);margin-top:4px}
</style>
