<template>
  <AppLayout>
    <div class="courses-page">
      <!-- Header -->
      <div class="page-header">
        <h1>Explore Courses</h1>
        <p>Master English with structured, AI-powered courses</p>
      </div>

      <!-- Filters -->
      <div class="filters card">
        <div class="search-wrap">
          <span class="search-icon">🔍</span>
          <input v-model="filters.search" type="text" class="form-input search-input"
            placeholder="Search courses..." @input="debouncedFetch" />
        </div>
        <select v-model="filters.category" class="form-input filter-select" @change="fetchCourses">
          <option value="">All Categories</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.icon }} {{ c.name }}</option>
        </select>
        <select v-model="filters.level" class="form-input filter-select" @change="fetchCourses">
          <option value="">All Levels</option>
          <option value="beginner">🌱 Beginner</option>
          <option value="intermediate">⚡ Intermediate</option>
          <option value="advanced">🔥 Advanced</option>
        </select>
        <select v-model="filters.is_free" class="form-input filter-select" @change="fetchCourses">
          <option value="">All Courses</option>
          <option value="true">🆓 Free</option>
          <option value="false">💎 Paid</option>
        </select>
      </div>

      <!-- Loading -->
      <div class="loading-state" v-if="loading">
        <div class="spinner"></div>
        <p>Loading courses...</p>
      </div>

      <!-- Empty -->
      <div class="empty-state" v-else-if="courses.length === 0">
        <div class="icon">📚</div>
        <h3>No courses found</h3>
        <p>Try different filters</p>
      </div>

      <!-- Course grid -->
      <div class="course-grid" v-else>
        <router-link v-for="c in courses" :key="c.id"
          :to="`/courses/${c.slug}`" class="course-card card card-hover">
          <div class="cc-thumb">
            <img v-if="c.thumbnail" :src="c.thumbnail" :alt="c.title" />
            <div v-else class="cc-placeholder">📖</div>
            <div class="cc-price">
              <span v-if="c.is_free" class="chip chip-green">Free</span>
              <span v-else-if="c.discount_price" class="chip chip-amber">
                ৳{{ c.discount_price }}
                <s class="original-price">৳{{ c.price }}</s>
              </span>
              <span v-else class="chip chip-purple">৳{{ c.price }}</span>
            </div>
          </div>
          <div class="cc-body">
            <div class="cc-meta">
              <span class="chip chip-teal">{{ c.category_name || 'General' }}</span>
              <span class="chip chip-purple">{{ c.level }}</span>
            </div>
            <h3 class="cc-title">{{ c.title }}</h3>
            <p class="cc-desc">{{ c.short_desc }}</p>
            <div class="cc-stats">
              <span>📚 {{ c.total_lessons }} lessons</span>
              <span>👥 {{ c.enrolled_count }}</span>
              <span v-if="c.rating_avg > 0">⭐ {{ c.rating_avg }}</span>
            </div>
          </div>
          <div class="cc-enrolled" v-if="c.enrolled">
            <div class="progress-bar">
              <div class="progress-fill" :style="`width:${c.progress}%`"></div>
            </div>
            <span class="chip chip-green">{{ c.progress.toFixed(0) }}%</span>
          </div>
        </router-link>
      </div>

      <!-- Pagination -->
      <div class="pagination" v-if="totalPages > 1">
        <button class="btn btn-outline btn-sm" :disabled="page === 1" @click="page--;fetchCourses()">← Prev</button>
        <span class="page-info">{{ page }} / {{ totalPages }}</span>
        <button class="btn btn-outline btn-sm" :disabled="page === totalPages" @click="page++;fetchCourses()">Next →</button>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import api from '@/api'

const courses    = ref([])
const categories = ref([])
const loading    = ref(false)
const page       = ref(1)
const totalPages = ref(1)
const filters    = reactive({ search: '', category: '', level: '', is_free: '' })

let searchTimer = null
function debouncedFetch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(fetchCourses, 400)
}

async function fetchCourses() {
  loading.value = true
  try {
    const params = { page: page.value, limit: 12, ...filters }
    if (!params.category) delete params.category
    if (!params.level)    delete params.level
    if (params.is_free === '') delete params.is_free
    else params.is_free = params.is_free === 'true'

    const res = await api.get('/courses', { params })
    courses.value    = res.data.courses
    totalPages.value = res.data.pages
  } catch {}
  loading.value = false
}

onMounted(async () => {
  fetchCourses()
  try {
    const res = await api.get('/categories')
    categories.value = res.data
  } catch {}
})
</script>

<style scoped>
.courses-page { display: flex; flex-direction: column; gap: 24px; }
.page-header h1 { margin-bottom: 4px; }
.page-header p  { color: var(--text3); }

.filters { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; padding: 16px 20px; }
.search-wrap { position: relative; flex: 1; min-width: 200px; }
.search-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); font-size: 14px; }
.search-input { padding-left: 36px; }
.filter-select { width: auto; min-width: 140px; }

.loading-state { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 60px; color: var(--text3); }

.course-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
.course-card { display: flex; flex-direction: column; text-decoration: none; padding: 0; overflow: hidden; }
.cc-thumb { position: relative; aspect-ratio: 16/9; background: var(--bg3); overflow: hidden; }
.cc-thumb img { width: 100%; height: 100%; object-fit: cover; }
.cc-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 48px; }
.cc-price { position: absolute; top: 10px; right: 10px; }
.original-price { font-size: 10px; opacity: 0.7; }
.cc-body { padding: 16px; flex: 1; }
.cc-meta { display: flex; gap: 6px; margin-bottom: 10px; flex-wrap: wrap; }
.cc-title { font-size: 15px; font-weight: 700; color: var(--text); margin-bottom: 6px; line-height: 1.4; }
.cc-desc { font-size: 13px; color: var(--text3); line-height: 1.5; margin-bottom: 12px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.cc-stats { display: flex; gap: 12px; font-size: 12px; color: var(--text3); }
.cc-enrolled { padding: 10px 16px; border-top: 1px solid var(--border); display: flex; align-items: center; gap: 8px; }
.cc-enrolled .progress-bar { flex: 1; }

.pagination { display: flex; align-items: center; justify-content: center; gap: 16px; }
.page-info { font-size: 14px; color: var(--text2); }

@media (max-width: 768px) {
  .filters { flex-direction: column; }
  .search-wrap, .filter-select { width: 100%; }
  .course-grid { grid-template-columns: 1fr; }
}
</style>
