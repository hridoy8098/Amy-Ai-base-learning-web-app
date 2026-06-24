<template>
  <AppLayout>
    <div>
      <h1 class="mb-6">🎓 My Certificates</h1>
      <div v-if="certs.length===0" class="empty-state">
        <div class="icon">🎓</div><h3>No certificates yet</h3><p>Complete a course to earn your certificate</p>
        <router-link to="/my-courses" class="btn btn-primary mt-4">My Courses</router-link>
      </div>
      <div class="certs-grid" v-else>
        <div v-for="c in certs" :key="c.id" class="cert-card card">
          <div class="cert-icon">🎓</div>
          <h3>{{ c.course_title }}</h3>
          <div class="cert-code chip chip-purple">{{ c.cert_code }}</div>
          <div class="text-xs text-muted mt-2">Issued: {{ new Date(c.issued_at).toLocaleDateString() }}</div>
          <a v-if="c.file_path" :href="c.file_path" target="_blank" class="btn btn-primary btn-sm mt-4 w-full">⬇ Download Certificate</a>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import api from '@/api'
const certs=ref([])
onMounted(async()=>{try{const r=await api.get('/users/certificates');certs.value=r.data}catch{}})
</script>
<style scoped>
.certs-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:20px}
.cert-card{text-align:center;padding:32px 20px}
.cert-icon{font-size:48px;margin-bottom:12px}
.cert-code{margin:8px auto;display:inline-block}
</style>
