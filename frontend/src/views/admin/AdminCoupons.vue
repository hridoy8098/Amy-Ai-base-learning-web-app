<template>
  <AppLayout>
    <div class="admin-coupons">
      <div class="page-header flex justify-between items-center">
        <h1>🎫 Coupons</h1>
        <button class="btn btn-primary" @click="showForm=true">+ New Coupon</button>
      </div>
      <div class="card table-wrap">
        <table>
          <thead><tr><th>Code</th><th>Discount</th><th>Used</th><th>Max Uses</th><th>Status</th><th>Action</th></tr></thead>
          <tbody>
            <tr v-for="c in coupons" :key="c.id">
              <td><code class="chip chip-purple">{{ c.code }}</code></td>
              <td>{{ c.discount_pct > 0 ? c.discount_pct+'%' : '৳'+c.discount_amt }}</td>
              <td>{{ c.used_count }}</td>
              <td>{{ c.max_uses }}</td>
              <td><span class="chip" :class="c.is_active?'chip-green':'chip-rose'">{{ c.is_active?'Active':'Inactive' }}</span></td>
              <td><button class="btn btn-danger btn-sm" @click="del(c)">Delete</button></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="modal-overlay" v-if="showForm" @click.self="showForm=false">
        <div class="modal">
          <h3 class="mb-4">Create Coupon</h3>
          <div class="flex flex-col gap-4">
            <div class="form-group"><label class="form-label">Code *</label><input v-model="form.code" type="text" class="form-input" placeholder="SAVE20" style="text-transform:uppercase" /></div>
            <div class="form-group"><label class="form-label">Discount %</label><input v-model.number="form.discount_pct" type="number" min="0" max="100" class="form-input" /></div>
            <div class="form-group"><label class="form-label">Or Fixed Amount (৳)</label><input v-model.number="form.discount_amt" type="number" min="0" class="form-input" /></div>
            <div class="form-group"><label class="form-label">Max Uses</label><input v-model.number="form.max_uses" type="number" min="1" class="form-input" /></div>
            <div class="flex gap-2"><button class="btn btn-primary" @click="save">Create</button><button class="btn btn-outline" @click="showForm=false">Cancel</button></div>
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
const coupons=ref([]),showForm=ref(false)
const form=reactive({code:'',discount_pct:0,discount_amt:0,max_uses:100})
async function load(){try{const r=await api.get('/admin/coupons');coupons.value=r.data}catch{}}
async function save(){try{await api.post('/admin/coupons',{...form,code:form.code.toUpperCase()});toast.success('Coupon created!');showForm.value=false;Object.assign(form,{code:'',discount_pct:0,discount_amt:0,max_uses:100});load()}catch(e){toast.error(e.response?.data?.detail||'Failed')}}
async function del(c){if(!confirm('Delete coupon?'))return;try{await api.delete(`/admin/coupons/${c.id}`);toast.success('Deleted');load()}catch{toast.error('Failed')}}
onMounted(load)
</script>
<style scoped>.admin-coupons{display:flex;flex-direction:column;gap:20px}</style>
