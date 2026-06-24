<template>
  <AppLayout>
    <div class="lesson-page" v-if="lesson">
      <div class="lesson-layout">

        <!-- ── Sidebar ── -->
        <div class="lesson-sidebar">
          <div class="ls-header">
            <router-link :to="`/courses/${route.params.slug}`" class="back-link">
              ← {{ course?.title }}
            </router-link>
            <div class="ls-progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="`width:${courseProgress}%`"></div>
              </div>
              <span>{{ courseProgress.toFixed(0) }}%</span>
            </div>
          </div>

          <div class="ls-lessons">
            <div
              v-for="(l, i) in lessons" :key="l.id"
              class="ls-lesson"
              :class="{ active: l.id === lesson.id, locked: l.locked, completed: l.completed }"
              @click="goLesson(l)"
            >
              <span class="lsl-num">{{ i + 1 }}</span>
              <span class="lsl-title">{{ l.title }}</span>
              <span class="lsl-status">
                {{ l.locked ? '🔒' : l.completed ? '✅' : '' }}
              </span>
            </div>
          </div>
        </div>

        <!-- ── Main ── -->
        <div class="lesson-main">
          <div class="lm-header">
            <div>
              <span class="chip chip-teal">{{ lesson.lesson_type }}</span>
              <h2>{{ lesson.title }}</h2>
            </div>
            <button
              class="btn btn-primary btn-sm"
              @click="markComplete"
              :disabled="marked || completing"
            >
              {{ marked ? '✅ Completed' : completing ? '...' : 'Mark Complete' }}
            </button>
          </div>

          <!-- Video -->
          <div class="lesson-video" v-if="lesson.lesson_type === 'video' && lesson.video_url">
            <div v-if="lesson.video_type === 'youtube'" class="yt-wrap">
              <iframe :src="youtubeEmbed(lesson.video_url)" frameborder="0" allowfullscreen></iframe>
            </div>
            <div v-else class="vid-wrap">
              <video
                :src="lesson.video_url"
                controls
                @timeupdate="onVideoProgress"
                ref="videoEl"
              >Your browser does not support video.</video>
            </div>
          </div>

          <!-- PDF -->
          <div class="lesson-pdf" v-if="lesson.lesson_type === 'pdf' && lesson.file_url">
            <div class="pdf-actions">
              <a :href="lesson.file_url" target="_blank" class="btn btn-secondary btn-sm">📄 Open PDF</a>
              <a :href="lesson.file_url" download class="btn btn-outline btn-sm">⬇ Download</a>
            </div>
            <iframe :src="lesson.file_url" class="pdf-frame"></iframe>
          </div>

          <!-- DOC -->
          <div class="lesson-doc" v-if="lesson.lesson_type === 'doc' && lesson.file_url">
            <div class="doc-card card">
              <span class="doc-icon">📝</span>
              <div>
                <h3>Document File</h3>
                <p>Download and open this document to view the lesson content.</p>
              </div>
              <a :href="lesson.file_url" download class="btn btn-primary">⬇ Download Document</a>
            </div>
          </div>

          <!-- Text content -->
          <div class="lesson-text card" v-if="lesson.content">
            <div v-html="lesson.content" class="rich-content"></div>
          </div>

          <!-- Navigation -->
          <div class="lesson-nav">
            <button class="btn btn-outline" @click="prevLesson" :disabled="!prevL">← Previous</button>
            <span class="lesson-pos">{{ currentIdx + 1 }} / {{ lessons.length }}</span>
            <button class="btn btn-primary" @click="nextLesson" :disabled="!nextL">Next →</button>
          </div>

          <!-- Notes -->
          <div class="lesson-notes card mt-4">
            <h3>📝 My Notes</h3>
            <textarea
              v-model="noteContent"
              class="form-input mt-2"
              rows="4"
              placeholder="Write your notes here..."
            ></textarea>
            <button class="btn btn-secondary btn-sm mt-2" @click="saveNote">Save Note</button>
          </div>
        </div>

      </div>
    </div>

    <!-- Loading -->
    <div class="loading-state" v-else-if="loading">
      <div class="spinner"></div>
    </div>

    <!-- Error: not found or no access -->
    <div class="error-state" v-else>
      <div class="error-icon">🔒</div>
      <h3>{{ errorMsg || 'Lesson not found' }}</h3>
      <router-link :to="`/courses/${route.params.slug}`" class="btn btn-primary mt-4">
        ← Back to Course
      </router-link>
    </div>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import { toast } from 'vue3-toastify'
import api from '@/api'

const route    = useRoute()
const router   = useRouter()
const lesson   = ref(null)
const course   = ref(null)
const lessons  = ref([])
const marked   = ref(false)
const completing = ref(false)
const noteContent = ref('')
const videoEl  = ref(null)
const loading  = ref(true)
const errorMsg = ref('')
let videoTimer = null

// ── Computed ──────────────────────────────────────────────
const currentIdx = computed(() =>
  lessons.value.findIndex(l => l.id === lesson.value?.id)
)
const prevL = computed(() => lessons.value[currentIdx.value - 1])
const nextL = computed(() => lessons.value[currentIdx.value + 1])
const courseProgress = computed(() => {
  const done = lessons.value.filter(l => l.completed).length
  return lessons.value.length ? (done / lessons.value.length) * 100 : 0
})

// ── Helpers ───────────────────────────────────────────────
function youtubeEmbed(url) {
  const id = url.match(/(?:v=|youtu\.be\/)([^&\n]+)/)?.[1]
  return id ? `https://www.youtube.com/embed/${id}` : url
}

function onVideoProgress() {
  clearTimeout(videoTimer)
  videoTimer = setTimeout(async () => {
    if (videoEl.value) {
      await api.post(`/lessons/${lesson.value.id}/video-progress`, {
        watch_seconds: Math.floor(videoEl.value.currentTime)
      })
    }
  }, 5000)
}

// ── Load lesson ───────────────────────────────────────────
async function loadLesson() {
  loading.value = true
  lesson.value  = null
  errorMsg.value = ''

  try {
    const lessonId = Number(route.params.id)  // ✅ string → number

    // 1. Load course info + lesson list
    const courseRes = await api.get(`/courses/${route.params.slug}`)
    course.value = courseRes.data

    // 2. Load lessons with locked flag from public endpoint
    const lessonsRes = await api.get(`/lessons/public/course/${course.value.id}`)
    lessons.value = lessonsRes.data

    // 3. Load progress for each lesson to mark completed
    const progressList = await Promise.allSettled(
      lessons.value.map(l => api.get(`/lessons/${l.id}/progress`))
    )
    progressList.forEach((result, i) => {
      if (result.status === 'fulfilled') {
        lessons.value[i].completed = result.value.data.completed
      }
    })

    // 4. Find the target lesson
    const foundLesson = lessons.value.find(l => l.id === lessonId)

    if (!foundLesson) {
      errorMsg.value = 'Lesson not found'
      loading.value = false
      return
    }

    if (foundLesson.locked) {
      errorMsg.value = 'Enroll in this course to access this lesson'
      loading.value = false
      return
    }

    // 5. Load full lesson content (with access check from backend)
    const detailRes = await api.get(`/lessons/detail/${lessonId}`)
    lesson.value = detailRes.data
    marked.value = detailRes.data.completed

    // 6. Restore video position
    if (detailRes.data.watch_seconds && videoEl.value) {
      videoEl.value.currentTime = detailRes.data.watch_seconds
    }

  } catch (e) {
    const status = e.response?.status
    if (status === 403) {
      errorMsg.value = 'You need to enroll in this course to access this lesson'
    } else if (status === 404) {
      errorMsg.value = 'Lesson not found'
    } else {
      errorMsg.value = 'Failed to load lesson'
      toast.error('Failed to load lesson')
    }
    console.error('loadLesson error:', e)
  } finally {
    loading.value = false
  }
}

// ── Actions ───────────────────────────────────────────────
async function markComplete() {
  completing.value = true
  try {
    await api.post(`/courses/${course.value.id}/progress/${lesson.value.id}`)
    marked.value = true
    const l = lessons.value.find(l2 => l2.id === lesson.value.id)
    if (l) l.completed = true
    toast.success('+5 XP earned! 🎉')
    if (nextL.value && !nextL.value.locked) {
      setTimeout(() => nextLesson(), 1200)
    }
  } catch {
    toast.error('Failed to mark complete')
  } finally {
    completing.value = false
  }
}

async function saveNote() {
  if (!noteContent.value.trim()) return
  try {
    await api.post('/users/notes', {
      content: noteContent.value,
      lesson_id: lesson.value.id,
      title: lesson.value.title
    })
    toast.success('Note saved!')
  } catch {
    toast.error('Failed to save note')
  }
}

function goLesson(l) {
  if (l.locked) {
    toast.warning('Complete enrollment to access this lesson')
    return
  }
  router.push(`/learn/${route.params.slug}/${l.id}`)
}

function prevLesson() {
  if (prevL.value && !prevL.value.locked) goLesson(prevL.value)
}
function nextLesson() {
  if (nextL.value && !nextL.value.locked) goLesson(nextL.value)
}

// ── Lifecycle ─────────────────────────────────────────────
// Reload when navigating between lessons (same route, different id)
watch(() => route.params.id, () => {
  if (route.params.id) loadLesson()
})

onMounted(loadLesson)
</script>

<style scoped>
.lesson-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 0;
  min-height: calc(100vh - 130px);
}

/* ── Sidebar ── */
.lesson-sidebar { background: var(--bg2); border-right: 1px solid var(--border); display: flex; flex-direction: column; }
.ls-header { padding: 16px; border-bottom: 1px solid var(--border); }
.back-link { font-size: 13px; color: var(--p); text-decoration: none; display: block; margin-bottom: 10px; }
.ls-progress { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--text3); }
.ls-progress .progress-bar { flex: 1; }
.ls-lessons { flex: 1; overflow-y: auto; padding: 8px; }

.ls-lesson {
  display: flex; align-items: center; gap: 8px;
  padding: 10px; border-radius: var(--r);
  cursor: pointer; transition: background var(--t);
}
.ls-lesson:hover:not(.locked) { background: var(--bg3); }
.ls-lesson.active  { background: var(--p-soft); }
.ls-lesson.locked  { opacity: 0.5; cursor: not-allowed; }

.lsl-num {
  width: 20px; height: 20px; border-radius: 50%;
  background: var(--border); font-size: 10px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; color: var(--text3);
}
.ls-lesson.active .lsl-num  { background: var(--p); color: #fff; }
.lsl-title { flex: 1; font-size: 13px; color: var(--text2); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ls-lesson.active .lsl-title { color: var(--p); font-weight: 600; }
.lsl-status { font-size: 14px; flex-shrink: 0; }

/* ── Main ── */
.lesson-main { padding: 28px; display: flex; flex-direction: column; gap: 20px; overflow-y: auto; }
.lm-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; }
.lm-header h2 { margin: 6px 0 0; }

.yt-wrap, .vid-wrap { border-radius: var(--r2); overflow: hidden; background: #000; }
.yt-wrap iframe { width: 100%; aspect-ratio: 16/9; display: block; }
.vid-wrap video  { width: 100%; aspect-ratio: 16/9; display: block; }

.pdf-actions { display: flex; gap: 10px; margin-bottom: 12px; }
.pdf-frame   { width: 100%; height: 600px; border: 1px solid var(--border); border-radius: var(--r2); }

.doc-card { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.doc-icon { font-size: 48px; }

.rich-content :deep(h1),
.rich-content :deep(h2),
.rich-content :deep(h3) { margin: 16px 0 8px; color: var(--text); }
.rich-content :deep(p)  { margin-bottom: 12px; color: var(--text2); line-height: 1.7; }
.rich-content :deep(ul),
.rich-content :deep(ol) { margin: 12px 0; padding-left: 24px; color: var(--text2); }
.rich-content :deep(li) { margin-bottom: 6px; }
.rich-content :deep(code) { background: var(--p-soft); color: var(--p); padding: 2px 6px; border-radius: 4px; font-size: 13px; }
.rich-content :deep(blockquote) { border-left: 3px solid var(--p); padding: 8px 16px; background: var(--bg3); border-radius: 0 var(--r) var(--r) 0; margin: 12px 0; }
.rich-content :deep(img) { max-width: 100%; border-radius: var(--r); }

.lesson-nav { display: flex; align-items: center; justify-content: space-between; }
.lesson-pos { font-size: 13px; color: var(--text3); }

/* ── States ── */
.loading-state { display: flex; justify-content: center; padding: 80px; }
.error-state   { display: flex; flex-direction: column; align-items: center; padding: 80px; text-align: center; gap: 12px; }
.error-icon    { font-size: 56px; }
.error-state h3 { color: var(--text2); }

@media (max-width: 768px) {
  .lesson-layout { grid-template-columns: 1fr; }
  .lesson-sidebar { display: none; }
}
</style>