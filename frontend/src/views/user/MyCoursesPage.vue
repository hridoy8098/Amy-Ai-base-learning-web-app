<!-- MyCoursesPage.vue -->
<template>
  <AppLayout>
    <div>
      <h1 class="mb-6">🎯 My Courses</h1>
      <div v-if="courses.length === 0" class="empty-state">
        <div class="icon">📚</div><h3>No courses yet</h3><p>Browse and enroll in courses to start learning</p>
        <router-link to="/courses" class="btn btn-primary mt-4">Browse Courses</router-link>
      </div>
      <div class="courses-grid" v-else>
        <router-link v-for="c in courses" :key="c.course_id" :to="`/courses/${c.slug}`" class="course-card card card-hover">
          <div class="cc-thumb"><img v-if="c.thumbnail" :src="c.thumbnail" /><div v-else class="cc-ph">📖</div></div>
          <div class="cc-body">
            <h3 class="cc-title">{{ c.title }}</h3>
            <div class="progress-bar mt-2"><div class="progress-fill" :style="`width:${c.progress}%`"></div></div>
            <div class="cc-meta mt-1">
              <span>{{ c.progress.toFixed(0) }}% complete</span>
              <span class="chip chip-green" v-if="c.completed">✅ Done</span>
            </div>
            <div v-if="c.completed" class="mt-3">
              <router-link :to="`/certificates`" class="btn btn-secondary btn-sm">🎓 Get Certificate</router-link>
            </div>
          </div>
        </router-link>
      </div>
    </div>
  </AppLayout>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import api from '@/api'
const courses=ref([])
onMounted(async()=>{try{const r=await api.get('/users/my-courses');courses.value=r.data}catch{}})
</script>
<style scoped>
.courses-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:20px}
.course-card{display:flex;flex-direction:column;text-decoration:none;padding:0;overflow:hidden}
.cc-thumb{aspect-ratio:16/9;background:var(--bg3);overflow:hidden}
.cc-thumb img{width:100%;height:100%;object-fit:cover}
.cc-ph{width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:40px}
.cc-body{padding:14px}
.cc-title{font-size:14px;font-weight:700;color:var(--text);margin-bottom:4px}
.cc-meta{display:flex;align-items:center;justify-content:space-between;font-size:12px;color:var(--text3)}
</style>
