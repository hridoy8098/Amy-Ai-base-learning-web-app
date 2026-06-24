<template>
  <AppLayout>
    <div class="admin-lessons">
      <div class="page-header flex items-center gap-4">
        <router-link to="/admin/courses" class="btn btn-outline btn-sm">← Courses</router-link>
        <div><h1>📝 Lessons</h1><p v-if="course">{{ course.title }}</p></div>
        <button class="btn btn-primary ml-auto" @click="openCreate">+ Add Lesson</button>
      </div>

      <!-- Lessons list -->
      <div class="card">
        <div v-if="lessons.length === 0" class="empty-state">
          <div class="icon">📖</div>
          <h3>No lessons yet</h3>
          <p>Add your first lesson to this course</p>
        </div>
        <div class="lesson-list" v-else>
          <div v-for="(l, i) in lessons" :key="l.id" class="lesson-row">
            <div class="lr-drag">⠿</div>
            <div class="lr-num">{{ i+1 }}</div>
            <div class="lr-type-icon">{{ typeIcon(l.lesson_type) }}</div>
            <div class="lr-info">
              <div class="lr-title">{{ l.title }}</div>
              <div class="lr-meta">
                <span class="chip chip-teal" style="font-size:10px">{{ l.lesson_type }}</span>
                <span class="chip chip-green" style="font-size:10px" v-if="l.is_free">Free</span>
                <span class="chip chip-amber" style="font-size:10px" v-if="!l.is_published">Draft</span>
                <span class="text-xs text-muted" v-if="l.duration">{{ l.duration }} min</span>
              </div>
            </div>
            <div class="lr-actions">
              <button class="btn btn-sm btn-outline" @click="openEdit(l)">Edit</button>
              <button class="btn btn-sm btn-danger" @click="deleteLesson(l)">Del</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Lesson form modal -->
      <div class="modal-overlay" v-if="showForm" @click.self="showForm=false">
        <div class="modal modal-lg">
          <h3 class="mb-6">{{ editLesson ? 'Edit Lesson' : 'Add New Lesson' }}</h3>

          <div class="form-grid mb-4">
            <div class="form-group" style="grid-column:1/-1">
              <label class="form-label">Title *</label>
              <input v-model="lForm.title" type="text" class="form-input" required placeholder="Lesson title" />
            </div>
            <div class="form-group">
              <label class="form-label">Lesson Type</label>
              <select v-model="lForm.lesson_type" class="form-input">
                <option value="text">📖 Text</option>
                <option value="video">🎬 Video</option>
                <option value="pdf">📄 PDF</option>
                <option value="doc">📝 Document</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Duration (minutes)</label>
              <input v-model.number="lForm.duration" type="number" min="0" class="form-input" placeholder="0" />
            </div>
            <div class="form-group">
              <label class="form-label">Sort Order</label>
              <input v-model.number="lForm.sort_order" type="number" min="0" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Options</label>
              <div class="flex gap-3">
                <label class="checkbox-label"><input type="checkbox" v-model="lForm.is_free" /> Free preview</label>
                <label class="checkbox-label"><input type="checkbox" v-model="lForm.is_published" /> Published</label>
              </div>
            </div>
            <div class="form-group" style="grid-column:1/-1">
              <label class="form-label">Description</label>
              <textarea v-model="lForm.description" class="form-input" rows="2" placeholder="Short description..."></textarea>
            </div>
          </div>

          <!-- Video options -->
          <div class="form-group mb-4" v-if="lForm.lesson_type==='video'">
            <label class="form-label">Video Source</label>
            <div class="toggle-row mb-3">
              <button type="button" :class="['toggle-btn',lForm.video_type==='youtube'?'active':'']" @click="lForm.video_type='youtube'">▶ YouTube</button>
              <button type="button" :class="['toggle-btn',lForm.video_type==='upload'?'active':'']" @click="lForm.video_type='upload'">⬆ Upload</button>
            </div>
            <input v-if="lForm.video_type==='youtube'" v-model="lForm.video_url" type="text" class="form-input" placeholder="YouTube URL: https://youtube.com/watch?v=..." />
            <div v-if="lForm.video_type==='upload'">
              <div v-if="lForm.video_url" class="uploaded-file">
                <span>🎬 {{ lForm.video_url.split('/').pop() }}</span>
                <button class="btn btn-danger btn-sm" @click="lForm.video_url=''">✕</button>
              </div>
              <label class="upload-area" v-else>
                <span>🎬 Click to upload video</span>
                <span class="text-xs text-muted">MP4, WebM · Max 50MB</span>
                <input type="file" accept="video/*" @change="uploadVideo" hidden />
                <div class="spinner mt-2" v-if="uploading"></div>
              </label>
            </div>
          </div>

          <!-- PDF/Doc upload -->
          <div class="form-group mb-4" v-if="lForm.lesson_type==='pdf'||lForm.lesson_type==='doc'">
            <label class="form-label">{{ lForm.lesson_type==='pdf'?'PDF File':'Document File' }}</label>
            <div v-if="lForm.file_url" class="uploaded-file">
              <span>📄 {{ lForm.file_url.split('/').pop() }}</span>
              <button class="btn btn-danger btn-sm" @click="lForm.file_url=''">✕</button>
            </div>
            <label class="upload-area" v-else>
              <span>📄 Click to upload {{ lForm.lesson_type==='pdf'?'PDF':'document' }}</span>
              <input type="file" :accept="lForm.lesson_type==='pdf'?'.pdf':'.doc,.docx'" @change="uploadDoc" hidden />
              <div class="spinner mt-2" v-if="uploading"></div>
            </label>
          </div>

          <!-- Rich text content -->
          <div class="form-group mb-6" v-if="lForm.lesson_type==='text'">
            <label class="form-label">Lesson Content</label>
            <div class="editor-wrap">
              <div class="editor-toolbar">
                <button type="button" @click="execCmd('bold')" class="tb-btn"><b>B</b></button>
                <button type="button" @click="execCmd('italic')" class="tb-btn"><i>I</i></button>
                <button type="button" @click="execCmd('underline')" class="tb-btn"><u>U</u></button>
                <span class="tb-sep"></span>
                <button type="button" @click="execCmd('insertUnorderedList')" class="tb-btn">• List</button>
                <button type="button" @click="execCmd('insertOrderedList')" class="tb-btn">1. List</button>
                <span class="tb-sep"></span>
                <button type="button" @click="execCmd('formatBlock','h2')" class="tb-btn">H2</button>
                <button type="button" @click="execCmd('formatBlock','h3')" class="tb-btn">H3</button>
                <button type="button" @click="execCmd('formatBlock','p')" class="tb-btn">P</button>
              </div>
              <div ref="editorEl" class="editor-content" contenteditable="true"
                @input="lForm.content=editorEl.innerHTML"
                v-html="lForm.content" style="min-height:200px;outline:none;padding:16px;font-size:14px;line-height:1.7;color:var(--text)">
              </div>
            </div>
          </div>

          <div class="flex gap-3">
            <button class="btn btn-primary" @click="saveLesson" :disabled="saving">
              <span class="spinner" v-if="saving"></span>
              <span v-else>{{ editLesson ? 'Update' : 'Add Lesson' }}</span>
            </button>
            <button class="btn btn-outline" @click="showForm=false">Cancel</button>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import { toast } from 'vue3-toastify'
import api from '@/api'

const route = useRoute()
const courseId = route.params.id
const course  = ref(null)
const lessons = ref([])
const showForm = ref(false)
const editLesson = ref(null)
const saving  = ref(false)
const uploading = ref(false)
const editorEl = ref(null)

const lForm = reactive({ title:'', description:'', content:'', lesson_type:'text', video_url:'', video_type:'youtube', file_url:'', duration:0, sort_order:0, is_free:false, is_published:true, course_id: parseInt(courseId) })

function typeIcon(t) { return {text:'📖',video:'🎬',pdf:'📄',doc:'📝',quiz:'🧠'}[t]||'📖' }

function openCreate() { Object.assign(lForm,{title:'',description:'',content:'',lesson_type:'text',video_url:'',video_type:'youtube',file_url:'',duration:0,sort_order:lessons.value.length,is_free:false,is_published:true}); editLesson.value=null; showForm.value=true }
function openEdit(l) { Object.assign(lForm,{...l,video_type:l.video_type||'youtube'}); editLesson.value=l; showForm.value=true }

async function uploadVideo(e) { const file=e.target.files[0];if(!file)return;uploading.value=true;const fd=new FormData();fd.append('file',file);try{const r=await api.post('/upload/video',fd);lForm.video_url=r.data.url;toast.success('Video uploaded!')}catch{toast.error('Upload failed')}finally{uploading.value=false} }
async function uploadDoc(e) { const file=e.target.files[0];if(!file)return;uploading.value=true;const fd=new FormData();fd.append('file',file);try{const r=await api.post('/upload/document',fd);lForm.file_url=r.data.url;toast.success('File uploaded!')}catch{toast.error('Upload failed')}finally{uploading.value=false} }
function execCmd(cmd,val=null){document.execCommand(cmd,false,val)}

async function saveLesson() {
  if(!lForm.title.trim()){toast.error('Title required');return}
  saving.value=true
  try {
    if(editLesson.value){await api.put(`/lessons/${editLesson.value.id}`,lForm);toast.success('Lesson updated!')}
    else{await api.post('/lessons',lForm);toast.success('Lesson added!')}
    showForm.value=false; loadLessons()
  }catch(e){toast.error(e.response?.data?.detail||'Failed')}finally{saving.value=false}
}

async function deleteLesson(l) { if(!confirm(`Delete "${l.title}"?`))return;try{await api.delete(`/lessons/${l.id}`);toast.success('Deleted');loadLessons()}catch{toast.error('Failed')} }

async function loadLessons() { try{const r=await api.get(`/lessons/course/${courseId}`);lessons.value=r.data}catch{} }

onMounted(async()=>{
  loadLessons()
  try{const r=await api.get('/courses/admin/all');course.value=r.data.find(c=>c.id==courseId)}catch{}
})
</script>

<style scoped>
.admin-lessons{display:flex;flex-direction:column;gap:20px}
.lesson-list{display:flex;flex-direction:column}
.lesson-row{display:flex;align-items:center;gap:12px;padding:14px 16px;border-bottom:1px solid var(--border);transition:background .15s}
.lesson-row:hover{background:var(--bg3)}
.lesson-row:last-child{border-bottom:none}
.lr-drag{color:var(--text3);cursor:grab;font-size:16px}
.lr-num{width:24px;height:24px;border-radius:50%;background:var(--p-soft);color:var(--p);font-size:11px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.lr-type-icon{font-size:20px;flex-shrink:0}
.lr-info{flex:1;min-width:0}
.lr-title{font-size:14px;font-weight:600;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.lr-meta{display:flex;gap:6px;align-items:center;margin-top:4px;flex-wrap:wrap}
.lr-actions{display:flex;gap:6px;flex-shrink:0}
.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.toggle-row{display:flex;gap:6px}
.toggle-btn{flex:1;padding:8px;border:1.5px solid var(--border);border-radius:var(--r);background:transparent;color:var(--text2);font-size:13px;font-weight:600;cursor:pointer;transition:all .18s}
.toggle-btn.active{border-color:var(--p);background:var(--p-soft);color:var(--p)}
.upload-area{display:flex;flex-direction:column;align-items:center;gap:6px;padding:24px;border:2px dashed var(--border);border-radius:var(--r);cursor:pointer;transition:all .18s;text-align:center;font-size:13px;color:var(--text3)}
.upload-area:hover{border-color:var(--p);color:var(--p)}
.uploaded-file{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;background:var(--bg3);border-radius:var(--r);font-size:13px;color:var(--text2)}
.editor-wrap{border:1.5px solid var(--border);border-radius:var(--r);overflow:hidden}
.editor-toolbar{display:flex;align-items:center;gap:4px;padding:8px 12px;background:var(--bg3);border-bottom:1px solid var(--border);flex-wrap:wrap}
.tb-btn{padding:4px 8px;border:1px solid var(--border);border-radius:6px;background:var(--bg2);cursor:pointer;font-size:12px;color:var(--text2);transition:all .15s}
.tb-btn:hover{border-color:var(--p);color:var(--p)}
.tb-sep{width:1px;height:18px;background:var(--border);margin:0 4px}
.checkbox-label{display:flex;align-items:center;gap:6px;font-size:13px;color:var(--text2);cursor:pointer}
@media(max-width:768px){.form-grid{grid-template-columns:1fr}}
</style>
