<template>
  <AppLayout>
    <div class="course-detail" v-if="course">

      <!-- ── Hero ── -->
      <div class="course-hero">
        <div class="hero-info">
          <div class="hero-meta">
            <span class="chip chip-teal">{{ course.category_name || 'General' }}</span>
            <span class="chip chip-purple">{{ course.level }}</span>
            <span class="chip chip-green" v-if="course.is_free">Free</span>
          </div>
          <h1>{{ course.title }}</h1>
          <p class="hero-desc">{{ course.short_desc }}</p>
          <div class="hero-stats">
            <span>📚 {{ course.total_lessons }} lessons</span>
            <span>⏱ {{ course.total_duration }} min</span>
            <span>👥 {{ course.enrolled_count }} enrolled</span>
            <span v-if="course.rating_avg > 0">⭐ {{ course.rating_avg }} ({{ course.rating_count }})</span>
          </div>
          <p class="hero-instructor" v-if="course.instructor_name">
            By <strong>{{ course.instructor_name }}</strong>
          </p>
        </div>

        <div class="hero-card card">
          <div class="hc-thumb">
            <img v-if="course.thumbnail" :src="course.thumbnail" :alt="course.title" />
            <div v-else class="hc-placeholder">📖</div>
          </div>

          <div class="hc-price" v-if="!course.is_free">
            <span class="price-main">৳{{ course.discount_price || course.price }}</span>
            <s class="price-old" v-if="course.discount_price">৳{{ course.price }}</s>
          </div>
          <div class="hc-price free" v-else><span class="price-main">Free Course</span></div>
          <div class="hc-note" v-if="!course.is_free">This paid course has a separate payment checkout.</div>

          <!-- Progress bar if enrolled -->
          <div v-if="course.enrolled" class="hc-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="`width:${courseProgress}%`"></div>
            </div>
            <span class="chip chip-green">{{ courseProgress.toFixed(0) }}% done</span>
          </div>

          <!-- Enroll / Continue button -->
          <button
            v-if="!course.enrolled"
            class="btn btn-primary w-full btn-lg"
            @click="handleEnroll"
            :disabled="enrolling"
          >
            <span class="spinner" v-if="enrolling"></span>
            <span v-else>{{ course.is_free || course.price === 0 ? 'Enroll Free' : 'Buy Now' }}</span>
          </button>

          <router-link
            v-else-if="firstLesson"
            :to="`/learn/${course.slug}/${firstLesson.id}`"
            class="btn btn-primary w-full btn-lg"
          >
            {{ courseProgress > 0 ? 'Continue Learning' : 'Start Learning' }} →
          </router-link>
        </div>
      </div>

      <!-- ── Body ── -->
      <div class="course-body">
        <div class="course-main">

          <!-- What you learn -->
          <div class="card mb-4" v-if="course.what_you_learn?.length">
            <h3>What you'll learn</h3>
            <div class="learn-grid mt-4">
              <div v-for="item in course.what_you_learn" :key="item" class="learn-item">
                <span>✅</span><span>{{ item }}</span>
              </div>
            </div>
          </div>

          <!-- Description -->
          <div class="card mb-4">
            <h3>About this course</h3>
            <p class="mt-4" style="white-space:pre-line">{{ course.description }}</p>
          </div>

          <!-- Lesson list -->
          <div class="card">
            <h3>Course Content</h3>
            <p class="text-muted text-sm mt-1">
              {{ lessons.length }} lessons · {{ course.total_duration }} minutes
            </p>

            <!-- Loading lessons -->
            <div v-if="lessonsLoading" class="lessons-loading mt-4">
              <div class="spinner"></div>
            </div>

            <div class="lesson-list mt-4" v-else>
              <div
                v-for="(l, i) in lessons" :key="l.id"
                class="lesson-row"
                :class="{ locked: l.locked, completed: l.completed }"
                @click="goToLesson(l)"
              >
                <div class="lr-num">{{ i + 1 }}</div>
                <div class="lr-icon">
                  {{ l.lesson_type === 'video' ? '🎬' :
                     l.lesson_type === 'pdf'   ? '📄' :
                     l.lesson_type === 'doc'   ? '📝' : '📖' }}
                </div>
                <div class="lr-info">
                  <div class="lr-title">{{ l.title }}</div>
                  <div class="lr-meta">
                    <span class="chip chip-teal" style="font-size:10px">{{ l.lesson_type }}</span>
                    <span class="text-xs text-muted" v-if="l.duration">{{ l.duration }} min</span>
                    <span class="chip chip-green" style="font-size:10px" v-if="l.is_free">Free</span>
                  </div>
                </div>
                <div class="lr-status">
                  <span v-if="l.locked">🔒</span>
                  <span v-else-if="l.completed">✅</span>
                  <span v-else>▶</span>
                </div>
              </div>

              <div class="empty-lessons" v-if="!lessonsLoading && lessons.length === 0">
                <p>No lessons available yet.</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Side -->
        <div class="course-side">
          <div class="card" v-if="course.requirements?.length">
            <h3>Requirements</h3>
            <ul class="req-list mt-4">
              <li v-for="r in course.requirements" :key="r">{{ r }}</li>
            </ul>
          </div>
          <div class="card mt-4" v-if="course.tags?.length">
            <h3>Tags</h3>
            <div class="flex gap-2 mt-4" style="flex-wrap:wrap">
              <span v-for="t in course.tags" :key="t" class="chip chip-purple">{{ t }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="loading-state" v-else>
      <div class="spinner"></div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useAuthStore } from '@/store/auth'
import { toast } from 'vue3-toastify'
import api from '@/api'

const route    = useRoute()
const router   = useRouter()
const auth     = useAuthStore()
const course   = ref(null)
const lessons  = ref([])
const enrolling      = ref(false)
const lessonsLoading = ref(false)

// ── Computed ──────────────────────────────────────────────
// First unlocked lesson for "Start / Continue" button
const firstLesson = computed(() =>
  lessons.value.find(l => !l.locked)
)

// Overall progress: how many lessons completed
const courseProgress = computed(() => {
  if (!lessons.value.length) return 0
  const done = lessons.value.filter(l => l.completed).length
  return (done / lessons.value.length) * 100
})

// ── Navigate to lesson ────────────────────────────────────
function goToLesson(l) {
  if (l.locked) {
    if (!auth.isLoggedIn) {
      toast.warning('Login to access this lesson')
      router.push('/login')
    } else {
      toast.warning('Enroll to access this lesson')
    }
    return
  }
  router.push(`/learn/${course.value.slug}/${l.id}`)
}

// ── Enroll ────────────────────────────────────────────────
async function handleEnroll() {
  if (!auth.isLoggedIn) { router.push('/login'); return }
  enrolling.value = true
  try {
    if (!course.value.is_free && course.value.price > 0) {
      router.push(`/payments?course_id=${course.value.id}`)
      return
    }
    await api.post(`/courses/${course.value.id}/enroll`)
    toast.success('Enrolled successfully! 🎉')
    await loadCourse()          // refresh enrolled flag
    await loadLessons()         // refresh locked flags
  } catch (e) {
    if (e.response?.status === 402) {
      router.push(`/payments?course_id=${course.value.id}`)
    } else {
      toast.error(e.response?.data?.detail || 'Failed to enroll')
    }
  } finally {
    enrolling.value = false
  }
}

// ── Load course info ──────────────────────────────────────
async function loadCourse() {
  const res = await api.get(`/courses/${route.params.slug}`)
  course.value = res.data
}

// ── Load lessons with locked + completed flags ────────────
async function loadLessons() {
  if (!course.value?.id) return
  lessonsLoading.value = true
  try {
    // Fetch lesson list with locked flag
    const res = await api.get(`/lessons/public/course/${course.value.id}`)
    const rawLessons = res.data

    // Fetch progress for each lesson in parallel (only if logged in)
    if (auth.isLoggedIn) {
      const progressResults = await Promise.allSettled(
        rawLessons.map(l => api.get(`/lessons/${l.id}/progress`))
      )
      progressResults.forEach((result, i) => {
        if (result.status === 'fulfilled') {
          rawLessons[i].completed = result.value.data.completed ?? false
          rawLessons[i].watch_seconds = result.value.data.watch_seconds ?? 0
        } else {
          rawLessons[i].completed = false
        }
      })
    } else {
      // Not logged in: no progress
      rawLessons.forEach(l => { l.completed = false })
    }

    lessons.value = rawLessons
  } catch (e) {
    console.error('loadLessons error:', e)
    toast.error('Could not load lesson list')
  } finally {
    lessonsLoading.value = false
  }
}

// ── Init ──────────────────────────────────────────────────
onMounted(async () => {
  try {
    await loadCourse()
    await loadLessons()
  } catch {
    toast.error('Course not found')
  }
})
</script>

<style scoped>
.course-detail { display: flex; flex-direction: column; gap: 28px; }
.loading-state { display: flex; justify-content: center; padding: 80px; }

/* ── Hero ── */
.course-hero { display: grid; grid-template-columns: 1fr 360px; gap: 32px; align-items: start; }
.hero-meta   { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }
.hero-info h1 { margin-bottom: 12px; }
.hero-desc    { font-size: 16px; color: var(--text2); margin-bottom: 16px; }
.hero-stats   { display: flex; gap: 16px; flex-wrap: wrap; font-size: 14px; color: var(--text3); margin-bottom: 8px; }
.hero-instructor { font-size: 14px; color: var(--text3); }

.hero-card    { padding: 0; overflow: hidden; position: sticky; top: 80px; }
.hc-thumb     { aspect-ratio: 16/9; background: var(--bg3); overflow: hidden; }
.hc-thumb img { width: 100%; height: 100%; object-fit: cover; }
.hc-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 56px; }

.hc-price     { padding: 16px 20px; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 10px; }
.hc-note      { padding: 12px 20px 0; font-size: 12px; color: var(--text3); }
.price-main   { font-size: 26px; font-weight: 800; color: var(--p); }
.price-old    { font-size: 16px; color: var(--text3); }
.hc-price.free .price-main { color: var(--green); }

.hc-progress  { padding: 0 20px 12px; display: flex; align-items: center; gap: 10px; }
.hc-progress .progress-bar { flex: 1; }
.hero-card .btn { margin: 0 20px 20px; width: calc(100% - 40px); }

/* ── Body ── */
.course-body { display: grid; grid-template-columns: 1fr 280px; gap: 24px; align-items: start; }
.learn-grid  { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.learn-item  { display: flex; gap: 8px; font-size: 13px; color: var(--text2); }

.lessons-loading { display: flex; justify-content: center; padding: 32px; }
.empty-lessons p { text-align: center; color: var(--text3); padding: 20px 0; font-size: 14px; }

.lesson-list { display: flex; flex-direction: column; }
.lesson-row  {
  display: flex; align-items: center; gap: 12px;
  padding: 12px; border-radius: var(--r);
  cursor: pointer; transition: background var(--t);
}
.lesson-row:hover:not(.locked) { background: var(--bg3); }
.lesson-row.locked    { opacity: 0.5; cursor: not-allowed; }
.lesson-row.completed { opacity: 0.8; }

.lr-num  {
  width: 24px; height: 24px; border-radius: 50%;
  background: var(--p-soft); color: var(--p);
  font-size: 11px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.lr-icon  { font-size: 18px; flex-shrink: 0; }
.lr-info  { flex: 1; min-width: 0; }
.lr-title { font-size: 14px; font-weight: 600; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.lr-meta  { display: flex; gap: 6px; align-items: center; margin-top: 4px; }
.lr-status { font-size: 16px; flex-shrink: 0; }

.req-list { padding-left: 20px; display: flex; flex-direction: column; gap: 8px; }
.req-list li { font-size: 14px; color: var(--text2); }

@media (max-width: 1024px) {
  .course-hero,
  .course-body { grid-template-columns: 1fr; }
  .hero-card   { position: static; }
}
</style>