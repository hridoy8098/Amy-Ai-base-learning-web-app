<!-- AdminPayments.vue -->
<template>
  <AppLayout>
    <div class="admin-payments">
      <h1 class="mb-6">💰 Payment Management</h1>
      <div class="filters card mb-4">
        <select v-model="statusFilter" class="form-input" style="width:auto" @change="load">
          <option value="">All Status</option>
          <option value="pending">Pending</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
        </select>
      </div>
      <div class="card table-wrap">
        <table>
          <thead><tr><th>User</th><th>Amount</th><th>Method</th><th>Type</th><th>Status</th><th>Tx ID</th><th>Date</th><th>Action</th></tr></thead>
          <tbody>
            <tr v-for="p in payments" :key="p.id">
              <td>{{ p.user_name }}</td>
              <td class="font-semibold">৳{{ p.amount }}</td>
              <td>{{ p.method }}</td>
              <td><span class="chip chip-teal">{{ p.payment_type }}</span></td>
              <td><span class="chip" :class="p.status==='completed'?'chip-green':p.status==='pending'?'chip-amber':'chip-rose'">{{ p.status }}</span></td>
              <td class="text-xs text-muted">{{ p.transaction_id || '—' }}</td>
              <td class="text-xs text-muted">{{ new Date(p.created_at).toLocaleDateString() }}</td>
              <td>
                <select class="form-input" style="width:auto;padding:4px 8px;font-size:12px" @change="updateStatus(p,$event)">
                  <option value="">Change</option>
                  <option value="completed">✅ Complete</option>
                  <option value="failed">❌ Failed</option>
                  <option value="refunded">↩ Refund</option>
                </select>
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
const payments=ref([]),statusFilter=ref('')
async function load(){try{const r=await api.get('/admin/payments',{params:{status:statusFilter.value||undefined,limit:50}});payments.value=r.data.payments}catch{}}
async function updateStatus(p,e){if(!e.target.value)return;try{await api.put(`/admin/payments/${p.id}`,{status:e.target.value});toast.success('Payment updated!');p.status=e.target.value;e.target.value=''}catch{toast.error('Failed');e.target.value=''}}
onMounted(load)
</script>
<style scoped>.admin-payments{display:flex;flex-direction:column;gap:16px}.filters{display:flex;gap:12px;padding:14px 20px}</style>
