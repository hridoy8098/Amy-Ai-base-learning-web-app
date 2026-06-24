<template>
  <AppLayout>
    <div class="course-form">
      <div class="page-header flex items-center gap-4">
        <router-link to="/admin/courses" class="btn btn-outline btn-sm">← Back</router-link>
        <h1>{{ isEdit ? 'Edit Course' : 'Create New Course' }}</h1>
      </div>

      <form @submit.prevent="save" class="form-grid-layout">
        <!-- Left: Main info -->
        <div class="form-main">
          <div class="card mb-4">
            <h3 class="mb-4">Course Information</h3>
            <div class="form-grid">
              <div class="form-group" style="grid-column:1/-1">
                <label class="form-label">Title *</label>
                <input v-model="form.title" type="text" class="form-input" required placeholder="e.g. Complete English Grammar Mastery" />
              </div>
              <div class="form-group" style="grid-column:1/-1">
                <label class="form-label">Short Description</label>
                <input v-model="form.short_desc" type="text" class="form-input" placeholder="One-line description (shown in cards)" />
              </div>
              <div class="form-group" style="grid-column:1/-1">
                <label class="form-label">Full Description</label>
                <textarea v-model="form.description" class="form-input" rows="5" placeholder="Detailed course description..."></textarea>
              </div>
              <div class="form-group">
                <label class="form-label">Category</label>
                <select v-model="form.category_id" class="form-input">
                  <option :value="null">No Category</option>
                  <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.icon }} {{ c.name }}</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Level</label>
                <select v-model="form.level" class="form-input">
                  <option value="beginner">🌱 Beginner</option>
                  <option value="intermediate">⚡ Intermediate</option>
                  <option value="advanced">🔥 Advanced</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Language</label>
                <select v-model="form.language" class="form-input">
                  <option value="en">English</option>
                  <option value="bn">Bangla</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Status</label>
                <select v-model="form.status" class="form-input">
                  <option value="draft">Draft</option>
                  <option value="published">Published</option>
                  <option value="archived">Archived</option>
                </select>
              </div>
            </div>
          </div>

          <div class="card mb-4">
            <h3 class="mb-4">Pricing</h3>
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Course Type</label>
                <div class="toggle-row">
                  <button type="button" :class="['toggle-btn', form.is_free?'active':'']" @click="form.is_free=true">🆓 Free</button>
                  <button type="button" :class="['toggle-btn', !form.is_free?'active':'']" @click="form.is_free=false">💎 Paid</button>
                </div>
              </div>
              <div class="form-group" v-if="!form.is_free">
                <label class="form-label">Price (BDT)</label>
                <input v-model.number="form.price" type="number" min="0" class="form-input" placeholder="0" />
              </div>
              <div class="form-group" v-if="!form.is_free">
                <label class="form-label">Discount Price (optional)</label>
                <input v-model.number="form.discount_price" type="number" min="0" class="form-input" placeholder="Leave empty for no discount" />
              </div>
            </div>
          </div>

          <div class="card mb-4">
            <h3 class="mb-4">What You'll Learn</h3>
            <div v-for="(item, i) in form.what_you_learn" :key="i" class="list-input-row">
              <input v-model="form.what_you_learn[i]" type="text" class="form-input" placeholder="Learning outcome..." />
              <button type="button" class="btn btn-danger btn-sm btn-icon" @click="form.what_you_learn.splice(i,1)">✕</button>
            </div>
            <button type="button" class="btn btn-outline btn-sm mt-2" @click="form.what_you_learn.push('')">+ Add item</button>
          </div>

          <div class="card">
            <h3 class="mb-4">Requirements</h3>
            <div v-for="(item, i) in form.requirements" :key="i" class="list-input-row">
              <input v-model="form.requirements[i]" type="text" class="form-input" placeholder="Requirement..." />
              <button type="button" class="btn btn-danger btn-sm btn-icon" @click="form.requirements.splice(i,1)">✕</button>
            </div>
            <button type="button" class="btn btn-outline btn-sm mt-2" @click="form.requirements.push('')">+ Add requirement</button>
          </div>
        </div>

        <!-- Right: Thumbnail + tags -->
        <div class="form-side">
          <div class="card mb-4">
            <h3 class="mb-4">Course Thumbnail</h3>
            <div class="thumb-preview" v-if="form.thumbnail">
              <img :src="form.thumbnail" alt="thumbnail" />
              <button type="button" class="btn btn-danger btn-sm mt-2 w-full" @click="form.thumbnail=''">Remove</button>
            </div>
            <div class="thumb-upload" v-else>
              <label class="upload-area">
                <span class="upload-icon">🖼️</span>
                <span>Click to upload thumbnail</span>
                <span class="text-xs text-muted">JPG, PNG, WebP · Max 5MB</span>
                <input type="file" accept="image/*" @change="uploadThumb" hidden />
              </label>
            </div>
            <div class="spinner mt-2 mx-auto" v-if="uploadingThumb"></div>
          </div>

          <div class="card">
            <h3 class="mb-4">Tags</h3>
            <div class="tags-wrap">
              <span v-for="(t,i) in form.tags" :key="t" class="chip chip-purple" style="cursor:pointer" @click="form.tags.splice(i,1)">{{ t }} ✕</span>
            </div>
            <div class="flex gap-2 mt-2">
              <input v-model="newTag" type="text" class="form-input" placeholder="Add tag..." @keydown.enter.prevent="addTag" />
              <button type="button" class="btn btn-outline btn-sm" @click="addTag">+</button>
            </div>
          </div>
        </div>
      </form>

      <div class="form-actions card">
        <button type="button" class="btn btn-primary btn-lg" @click="save" :disabled="saving">
          <span class="spinner" v-if="saving"></span>
          <span v-else>{{ isEdit ? 'Update Course' : 'Create Course' }}</span>
        </button>
        <router-link to="/admin/courses" class="btn btn-outline btn-lg">Cancel</router-link>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import { toast } from 'vue3-toastify'
import api from '@/api'

const route  = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)
const saving = ref(false)
const uploadingThumb = ref(false)
const categories = ref([])
const newTag = ref('')

const form = reactive({
  title:'', short_desc:'', description:'', thumbnail:'',
  level:'beginner', language:'en', status:'draft',
  is_free:false, price:0, discount_price:null,
  category_id:null, what_you_learn:[], requirements:[], tags:[],
})

function addTag() { if(newTag.value.trim()&&!form.tags.includes(newTag.value.trim())){form.tags.push(newTag.value.trim());newTag.value=''} }

async function uploadThumb(e) {
  const file = e.target.files[0]; if(!file)return
  uploadingThumb.value=true
  const fd=new FormData(); fd.append('file',file)
  try { const r=await api.post('/upload/thumbnail',fd); form.thumbnail=r.data.url; toast.success('Thumbnail uploaded!') }
  catch { toast.error('Upload failed') } finally { uploadingThumb.value=false }
}

async function save() {
  if(!form.title.trim()){toast.error('Title required');return}
  saving.value=true
  try {
    const data = {...form, what_you_learn:form.what_you_learn.filter(Boolean), requirements:form.requirements.filter(Boolean), discount_price:form.discount_price||null}
    if(isEdit.value) { await api.put(`/courses/admin/${route.params.id}`,data); toast.success('Course updated!') }
    else { await api.post('/courses/admin/create',data); toast.success('Course created!') }
    router.push('/admin/courses')
  } catch(e){ toast.error(e.response?.data?.detail||'Failed') } finally{saving.value=false}
}

onMounted(async()=>{
  try{const r=await api.get('/categories/all');categories.value=r.data}catch{}
  if(isEdit.value){
    try{const r=await api.get('/courses/admin/all');const c=r.data.find(c=>c.id==route.params.id);if(c){Object.assign(form,{title:c.title,short_desc:c.short_desc||'',description:c.description||'',thumbnail:c.thumbnail||'',level:c.level,language:c.language||'en',status:c.status,is_free:c.is_free,price:c.price,discount_price:c.discount_price,category_id:c.category_id,what_you_learn:c.what_you_learn||[],requirements:c.requirements||[],tags:c.tags||[]})}}catch{}
  }
})
</script>
<style scoped>
.course-form{display:flex;flex-direction:column;gap:24px}
.form-grid-layout{display:grid;grid-template-columns:1fr 300px;gap:24px;align-items:start}
.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.list-input-row{display:flex;gap:8px;margin-bottom:8px}
.toggle-row{display:flex;gap:6px}
.toggle-btn{flex:1;padding:8px;border:1.5px solid var(--border);border-radius:var(--r);background:transparent;color:var(--text2);font-size:13px;font-weight:600;cursor:pointer;transition:all .18s}
.toggle-btn.active{border-color:var(--p);background:var(--p-soft);color:var(--p)}
.thumb-preview img{width:100%;border-radius:var(--r);aspect-ratio:16/9;object-fit:cover}
.upload-area{display:flex;flex-direction:column;align-items:center;gap:6px;padding:24px;border:2px dashed var(--border);border-radius:var(--r);cursor:pointer;transition:all .18s;text-align:center;font-size:13px;color:var(--text3)}
.upload-area:hover{border-color:var(--p);color:var(--p)}
.upload-icon{font-size:32px}
.tags-wrap{display:flex;flex-wrap:wrap;gap:6px;min-height:32px}
.form-actions{display:flex;gap:12px;padding:20px 24px}
@media(max-width:1024px){.form-grid-layout{grid-template-columns:1fr}}
@media(max-width:768px){.form-grid{grid-template-columns:1fr}}
</style>
