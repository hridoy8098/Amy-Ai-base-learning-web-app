<!-- AdminCategories.vue -->
<template>
  <AppLayout>
    <div class="admin-cats">
      <div class="page-header flex justify-between items-center">
        <h1>🏷️ Categories</h1>
        <button class="btn btn-primary" @click="openCreate">+ New Category</button>
      </div>
      <div class="card table-wrap">
        <table>
          <thead><tr><th>Icon</th><th>Name</th><th>Courses</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody>
            <tr v-for="c in cats" :key="c.id">
              <td style="font-size:24px">{{ c.icon || '📁' }}</td>
              <td><div class="font-semibold">{{ c.name }}</div><div class="text-xs text-muted">{{ c.description }}</div></td>
              <td>{{ c.course_count }}</td>
              <td><span class="chip" :class="c.is_active?'chip-green':'chip-rose'">{{ c.is_active?'Active':'Hidden' }}</span></td>
              <td><div class="flex gap-2"><button class="btn btn-sm btn-outline" @click="openEdit(c)">Edit</button><button class="btn btn-sm btn-danger" @click="deleteCat(c)">Del</button></div></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="modal-overlay" v-if="showForm" @click.self="showForm=false">
        <div class="modal">
          <h3 class="mb-4">{{ editCat?'Edit':'New' }} Category</h3>
          <div class="flex flex-col gap-4">
            <div class="form-group"><label class="form-label">Name *</label><input v-model="form.name" type="text" class="form-input" required /></div>
            <div class="form-group"><label class="form-label">Icon (emoji)</label><input v-model="form.icon" type="text" class="form-input" placeholder="📚" /></div>
            <div class="form-group"><label class="form-label">Color</label><input v-model="form.color" type="color" class="form-input" style="height:40px" /></div>
            <div class="form-group"><label class="form-label">Description</label><textarea v-model="form.description" class="form-input" rows="2"></textarea></div>
            <div class="form-group" v-if="editCat"><label class="form-label">Status</label><select v-model="form.is_active" class="form-input"><option :value="true">Active</option><option :value="false">Hidden</option></select></div>
            <div class="flex gap-2"><button class="btn btn-primary" @click="save">Save</button><button class="btn btn-outline" @click="showForm=false">Cancel</button></div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
<script setup>
import { ref, reactive, onMounted } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { toast } from 'vue3-toastify'
import api from '@/api'
const cats=ref([]),showForm=ref(false),editCat=ref(null)
const form=reactive({name:'',icon:'',color:'#7b6ef6',description:'',is_active:true})
function openCreate(){Object.assign(form,{name:'',icon:'',color:'#7b6ef6',description:'',is_active:true});editCat.value=null;showForm.value=true}
function openEdit(c){Object.assign(form,c);editCat.value=c;showForm.value=true}
async function save(){try{if(editCat.value)await api.put(`/categories/${editCat.value.id}`,form);else await api.post('/categories',form);toast.success('Saved!');showForm.value=false;loadCats()}catch{toast.error('Failed')}}
async function deleteCat(c){if(!confirm('Delete?'))return;try{await api.delete(`/categories/${c.id}`);toast.success('Deleted');loadCats()}catch{toast.error('Failed')}}
async function loadCats(){try{const r=await api.get('/categories/all');cats.value=r.data}catch{}}
onMounted(loadCats)
</script>
<style scoped>.admin-cats{display:flex;flex-direction:column;gap:20px}</style>
