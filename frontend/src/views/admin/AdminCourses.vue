<template>
  <AppLayout>
    <div class="admin-courses">
      <div class="page-header flex justify-between items-center">
        <div><h1>📚 Course Management</h1></div>
        <router-link to="/admin/courses/create" class="btn btn-primary">+ New Course</router-link>
      </div>
      <div class="card table-wrap">
        <table>
          <thead><tr><th>Course</th><th>Category</th><th>Level</th><th>Status</th><th>Price</th><th>Enrolled</th><th>Actions</th></tr></thead>
          <tbody>
            <tr v-for="c in courses" :key="c.id">
              <td>
                <div class="flex items-center gap-2">
                  <img v-if="c.thumbnail" :src="c.thumbnail" style="width:40px;height:30px;object-fit:cover;border-radius:6px" />
                  <div>
                    <div class="font-semibold" style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ c.title }}</div>
                    <div class="text-xs text-muted">{{ c.total_lessons }} lessons</div>
                  </div>
                </div>
              </td>
              <td>{{ c.category_name || '—' }}</td>
              <td><span class="chip chip-teal">{{ c.level }}</span></td>
              <td>
                <span class="chip" :class="c.status==='published'?'chip-green':c.status==='draft'?'chip-amber':'chip-rose'">{{ c.status }}</span>
              </td>
              <td>{{ c.is_free ? 'Free' : '৳' + c.price }}</td>
              <td>{{ c.enrolled_count }}</td>
              <td>
                <div class="flex gap-2">
                  <router-link :to="`/admin/courses/${c.id}/edit`" class="btn btn-sm btn-outline">Edit</router-link>
                  <router-link :to="`/admin/courses/${c.id}/lessons`" class="btn btn-sm btn-secondary">Lessons</router-link>
                  <button class="btn btn-sm btn-danger" @click="deleteCourse(c)">Del</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </AppLayout>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { toast } from 'vue3-toastify'
import api from '@/api'
const courses = ref([])
async function loadCourses() { try { const r = await api.get('/courses/admin/all'); courses.value = r.data } catch {} }
async function deleteCourse(c) { if(!confirm(`Delete "${c.title}"?`))return; try { await api.delete(`/courses/admin/${c.id}`); toast.success('Deleted'); loadCourses() } catch { toast.error('Failed') } }
onMounted(loadCourses)
</script>
<style scoped>
.admin-courses { display: flex; flex-direction: column; gap: 20px; }
</style>
