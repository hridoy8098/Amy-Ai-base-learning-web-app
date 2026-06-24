<!-- AdminDashboard.vue -->
<template>
  <AppLayout>
    <div class="admin-dash">
      <div class="page-header">
        <h1>⚡ Admin Dashboard</h1>
        <p>Overview of your learning platform</p>
      </div>
      <div class="stats-grid" v-if="stats">
        <div class="stat-card card">
          <div class="stat-icon">👥</div>
          <div class="stat-val">{{ stats.users?.total || 0 }}</div>
          <div class="stat-label">Total Users</div>
          <div class="stat-sub">{{ stats.users?.paid || 0 }} paid</div>
        </div>
        <div class="stat-card card">
          <div class="stat-icon">📚</div>
          <div class="stat-val">{{ stats.courses?.published || 0 }}</div>
          <div class="stat-label">Published Courses</div>
          <div class="stat-sub">{{ stats.courses?.total || 0 }} total</div>
        </div>
        <div class="stat-card card">
          <div class="stat-icon">🎯</div>
          <div class="stat-val">{{ stats.enrollments?.total || 0 }}</div>
          <div class="stat-label">Enrollments</div>
          <div class="stat-sub">{{ stats.enrollments?.completed || 0 }} completed</div>
        </div>
        <div class="stat-card card revenue">
          <div class="stat-icon">💰</div>
          <div class="stat-val">৳{{ stats.payments?.revenue?.toFixed(0) || 0 }}</div>
          <div class="stat-label">Total Revenue</div>
          <div class="stat-sub">{{ stats.payments?.count || 0 }} payments</div>
        </div>
        <div class="stat-card card">
          <div class="stat-icon">🤖</div>
          <div class="stat-val">{{ stats.amy_messages || 0 }}</div>
          <div class="stat-label">Amy Messages</div>
        </div>
        <div class="stat-card card">
          <div class="stat-icon">🧠</div>
          <div class="stat-val">{{ stats.quizzes || 0 }}</div>
          <div class="stat-label">Quizzes Taken</div>
        </div>
      </div>
      <div class="quick-links card mt-6">
        <h3 class="mb-4">Quick Actions</h3>
        <div class="ql-grid">
          <router-link to="/admin/courses/create" class="ql-btn btn btn-primary">+ New Course</router-link>
          <router-link to="/admin/users" class="ql-btn btn btn-secondary">Manage Users</router-link>
          <router-link to="/admin/payments" class="ql-btn btn btn-outline">View Payments</router-link>
          <router-link to="/admin/coupons" class="ql-btn btn btn-outline">Manage Coupons</router-link>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import api from '@/api'
const stats = ref(null)
onMounted(async () => { try { const r = await api.get('/admin/stats'); stats.value = r.data } catch {} })
</script>
<style scoped>
.admin-dash { display: flex; flex-direction: column; gap: 24px; }
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.stat-card { text-align: center; padding: 24px 16px; }
.stat-icon { font-size: 32px; margin-bottom: 8px; }
.stat-val  { font-size: 32px; font-weight: 900; color: var(--p); }
.stat-label { font-size: 13px; color: var(--text2); font-weight: 600; }
.stat-sub   { font-size: 11px; color: var(--text3); margin-top: 2px; }
.revenue .stat-val { color: var(--green); }
.ql-grid { display: flex; gap: 12px; flex-wrap: wrap; }
@media (max-width: 768px) { .stats-grid { grid-template-columns: repeat(2,1fr); } }
</style>
