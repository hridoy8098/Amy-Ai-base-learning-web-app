<template>
  <AppLayout>
    <div class="admin-users">
      <div class="page-header flex justify-between items-center">
        <div><h1>👥 User Management</h1><p>Manage all registered users</p></div>
      </div>
      <div class="filters card">
        <input v-model="search" type="text" class="form-input" placeholder="Search by name or email..." @input="debounceLoad" style="max-width:300px" />
        <select v-model="roleFilter" class="form-input" style="width:auto" @change="loadUsers">
          <option value="">All Roles</option>
          <option value="user">User</option>
          <option value="admin">Admin</option>
        </select>
      </div>
      <div class="card table-wrap">
        <table>
          <thead><tr><th>User</th><th>Role</th><th>Plan</th><th>XP</th><th>Level</th><th>Joined</th><th>Actions</th></tr></thead>
          <tbody>
            <tr v-for="u in users" :key="u.id">
              <td>
                <div class="font-semibold">{{ u.name }}</div>
                <div class="text-xs text-muted">{{ u.email }}</div>
              </td>
              <td><span class="chip" :class="u.role==='admin'||u.role==='superadmin'?'chip-purple':'chip-teal'">{{ u.role }}</span></td>
              <td><span class="chip chip-amber">{{ u.subscription_plan }}</span></td>
              <td>{{ u.xp_points }}</td>
              <td>{{ u.level }}</td>
              <td>{{ new Date(u.created_at).toLocaleDateString() }}</td>
              <td>
                <div class="flex gap-2">
                  <button class="btn btn-sm btn-outline" @click="openEdit(u)">Edit</button>
                  <button class="btn btn-sm btn-danger" @click="deleteUser(u)" v-if="u.role!=='superadmin'">Del</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="table-footer">
          <span class="text-sm text-muted">Total: {{ total }} users</span>
          <div class="flex gap-2">
            <button class="btn btn-outline btn-sm" :disabled="page===1" @click="page--;loadUsers()">← Prev</button>
            <button class="btn btn-outline btn-sm" :disabled="page*20>=total" @click="page++;loadUsers()">Next →</button>
          </div>
        </div>
      </div>

      <!-- Edit modal -->
      <div class="modal-overlay" v-if="editUser" @click.self="editUser=null">
        <div class="modal">
          <h3 class="mb-4">Edit User: {{ editUser.name }}</h3>
          <div class="form-group mb-4">
            <label class="form-label">Role</label>
            <select v-model="editForm.role" class="form-input">
              <option value="user">User</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          <div class="form-group mb-4">
            <label class="form-label">Status</label>
            <select v-model="editForm.is_active" class="form-input">
              <option :value="true">Active</option>
              <option :value="false">Banned</option>
            </select>
          </div>
          <div class="form-group mb-4">
            <label class="form-label">Subscription Plan</label>
            <select v-model="editForm.subscription_plan" class="form-input">
              <option value="free">Free</option>
              <option value="basic">Basic</option>
              <option value="pro">Pro</option>
              <option value="premium">Premium</option>
            </select>
          </div>
          <div class="flex gap-2">
            <button class="btn btn-primary" @click="saveUser">Save</button>
            <button class="btn btn-outline" @click="editUser=null">Cancel</button>
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
const users=ref([]),total=ref(0),page=ref(1),search=ref(''),roleFilter=ref(''),editUser=ref(null)
const editForm=reactive({role:'user',is_active:true,subscription_plan:'free'})
let st=null
function debounceLoad(){clearTimeout(st);st=setTimeout(loadUsers,400)}
async function loadUsers(){try{const r=await api.get('/admin/users',{params:{page:page.value,limit:20,search:search.value||undefined,role:roleFilter.value||undefined}});users.value=r.data.users;total.value=r.data.total}catch{}}
function openEdit(u){editUser.value=u;editForm.role=u.role;editForm.is_active=u.is_active;editForm.subscription_plan=u.subscription_plan}
async function saveUser(){try{await api.put(`/admin/users/${editUser.value.id}`,editForm);toast.success('Updated');editUser.value=null;loadUsers()}catch{toast.error('Failed')}}
async function deleteUser(u){if(!confirm(`Delete ${u.name}?`))return;try{await api.delete(`/admin/users/${u.id}`);toast.success('Deleted');loadUsers()}catch{toast.error('Failed')}}
onMounted(loadUsers)
</script>
<style scoped>
.admin-users{display:flex;flex-direction:column;gap:20px}
.filters{display:flex;gap:12px;align-items:center;padding:14px 20px}
.table-footer{display:flex;justify-content:space-between;align-items:center;padding:14px 16px;border-top:1px solid var(--border)}
</style>
