<template>
  <AppLayout>
    <div class="payments-page">
      <div class="page-head">
        <div>
          <h1>{{ checkoutTitle }}</h1>
          <p class="text-muted">{{ checkoutSubtitle }}</p>
        </div>
      </div>

      <div class="card checkout-card" v-if="selectedCourse || selectedPlan">
        <div class="checkout-summary">
          <div>
            <div class="summary-label">{{ selectedCourse ? 'Course Payment' : 'Subscription Payment' }}</div>
            <h3>{{ selectedCourse ? selectedCourse.title : selectedPlan?.name }}</h3>
            <p class="text-muted">
              {{ selectedCourse ? 'Ei course er payment alada vabe process hobe.' : 'AI plan upgrade payment ekhane complete koro.' }}
            </p>
          </div>
          <div class="summary-price">৳{{ payableAmount }}</div>
        </div>

        <div v-if="selectedCourse" class="course-meta">
          <span>{{ selectedCourse.level }}</span>
          <span>{{ selectedCourse.total_lessons }} lessons</span>
          <span>{{ selectedCourse.total_duration }} min</span>
        </div>

        <div class="checkout-grid mt-6" v-if="!paymentDraft">
          <div class="form-group">
            <label class="form-label">Payment Method</label>
            <select v-model="paymentMethod" class="form-input">
              <option value="bkash">bKash</option>
              <option value="nagad">Nagad</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Coupon Code</label>
            <input v-model="couponCode" class="form-input" placeholder="Optional coupon code" />
          </div>
        </div>

        <div v-if="paymentDraft" class="payment-instructions mt-6">
          <div class="instruction-box">
            <div class="instruction-title">Payment Instructions</div>
            <p>{{ paymentDraft.instructions?.instructions }}</p>
            <div class="instruction-meta">
              <span>Method: {{ paymentDraft.instructions?.method || paymentMethod }}</span>
              <span>Amount: ৳{{ paymentDraft.amount }}</span>
              <span>Ref: {{ paymentDraft.instructions?.reference || ('AMY-' + paymentDraft.payment_id) }}</span>
            </div>
          </div>

          <div class="checkout-grid mt-4">
            <div class="form-group">
              <label class="form-label">Transaction ID</label>
              <input v-model="transactionId" class="form-input" placeholder="Enter your bKash/Nagad transaction ID" />
            </div>
          </div>
        </div>

        <div class="checkout-actions mt-6">
          <button v-if="!paymentDraft" class="btn btn-primary" @click="initiatePayment" :disabled="processing">
            {{ processing ? 'Processing...' : 'Initiate Payment' }}
          </button>
          <button v-else class="btn btn-primary" @click="confirmPayment" :disabled="processing || !transactionId.trim()">
            {{ processing ? 'Submitting...' : 'Submit Transaction ID' }}
          </button>
          <button v-if="paymentDraft" class="btn btn-outline" @click="resetDraft" :disabled="processing">Start Over</button>
          <router-link v-if="selectedCourse" :to="`/courses/${selectedCourse.slug}`" class="btn btn-secondary">Back to Course</router-link>
        </div>
      </div>

      <div class="plans-section" v-if="!selectedCourse">
        <div class="section-head">
          <div>
            <h3>Subscription Plans</h3>
            <p class="text-muted">Paid courses pricing ekhane na, course page theke alada payment hobe.</p>
          </div>
        </div>

        <div class="plans-grid">
          <div v-for="plan in plans" :key="plan.id" class="plan-card card" :class="{ popular: plan.popular, active: selectedPlan?.id === plan.id }">
            <div class="plan-badge chip chip-purple" v-if="plan.popular">Most Popular</div>
            <h3>{{ plan.name }}</h3>
            <div class="plan-price">{{ plan.price === 0 ? 'Free' : '৳' + plan.price }}<span v-if="plan.period">/{{ plan.period }}</span></div>
            <ul class="plan-features">
              <li v-for="feature in plan.features" :key="feature">{{ feature }}</li>
            </ul>
            <button
              v-if="plan.id !== 'free'"
              class="btn btn-primary w-full mt-4"
              @click="selectPlan(plan)"
              :disabled="auth.user?.subscription_plan === plan.id"
            >
              {{ auth.user?.subscription_plan === plan.id ? 'Current Plan' : 'Choose ' + plan.name }}
            </button>
            <div v-else class="btn btn-outline w-full mt-4" style="pointer-events:none">Free Plan</div>
          </div>
        </div>
      </div>

      <div v-if="history.length > 0">
        <h3 class="mb-4">Payment History</h3>
        <div class="card table-wrap">
          <table>
            <thead><tr><th>Type</th><th>Amount</th><th>Method</th><th>Status</th><th>Date</th></tr></thead>
            <tbody>
              <tr v-for="payment in history" :key="payment.id">
                <td>{{ payment.payment_type }}</td>
                <td class="font-semibold">৳{{ payment.amount }}</td>
                <td>{{ payment.method }}</td>
                <td><span class="chip" :class="payment.status === 'completed' ? 'chip-green' : payment.status === 'pending' ? 'chip-amber' : 'chip-rose'">{{ payment.status }}</span></td>
                <td class="text-xs text-muted">{{ new Date(payment.created_at).toLocaleDateString() }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue3-toastify'

import api from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useAuthStore } from '@/store/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const plans = ref([])
const history = ref([])
const selectedPlan = ref(null)
const selectedCourse = ref(null)
const paymentMethod = ref('bkash')
const couponCode = ref('')
const transactionId = ref('')
const paymentDraft = ref(null)
const processing = ref(false)

const checkoutTitle = computed(() => selectedCourse.value ? 'Course Payment' : selectedPlan.value ? 'Plan Payment' : 'Payments')
const checkoutSubtitle = computed(() => {
  if (selectedCourse.value) return 'Course er jonno alada payment ekhane complete koro.'
  if (selectedPlan.value) return 'Subscription plan payment ekhane complete koro.'
  return 'Subscription plan ar course payment alada vabe handle kora hoy.'
})
const payableAmount = computed(() => {
  if (paymentDraft.value) return paymentDraft.value.amount
  if (selectedCourse.value) return selectedCourse.value.discount_price || selectedCourse.value.price || 0
  return selectedPlan.value?.price || 0
})

function selectPlan(plan) {
  selectedPlan.value = plan
  selectedCourse.value = null
  paymentDraft.value = null
  transactionId.value = ''
  router.replace({ path: '/payments', query: { plan: plan.id } })
}

function resetDraft() {
  paymentDraft.value = null
  transactionId.value = ''
}

async function loadBaseData() {
  const [plansResult, historyResult] = await Promise.allSettled([
    api.get('/payments/plans'),
    api.get('/payments/history'),
  ])

  if (plansResult.status === 'fulfilled') {
    plans.value = plansResult.value.data
    if (route.query.plan) {
      selectedPlan.value = plans.value.find(plan => plan.id === route.query.plan) || null
    }
  }

  if (historyResult.status === 'fulfilled') {
    history.value = historyResult.value.data
  }
}

async function loadCourseCheckout() {
  const courseId = route.query.course_id
  if (!courseId) {
    selectedCourse.value = null
    return
  }

  try {
    const response = await api.get(`/courses/id/${courseId}`)
    selectedCourse.value = response.data
    selectedPlan.value = null
  } catch (error) {
    selectedCourse.value = null
    toast.error(error.response?.data?.detail || 'Unable to load course payment info')
  }
}

async function initiatePayment() {
  const paymentType = selectedCourse.value ? 'course' : 'subscription'
  if (!selectedCourse.value && !selectedPlan.value) {
    toast.warning('Please select a plan or course first')
    return
  }

  processing.value = true
  try {
    const payload = {
      payment_type: paymentType,
      method: paymentMethod.value,
      coupon_code: couponCode.value || null,
      course_id: selectedCourse.value?.id || null,
      plan: selectedPlan.value?.id || null,
    }
    const response = await api.post('/payments/initiate', payload)
    paymentDraft.value = response.data
    toast.success('Payment initiated. Follow the instructions below.')
  } catch (error) {
    toast.error(error.response?.data?.detail || 'Failed to initiate payment')
  } finally {
    processing.value = false
  }
}

async function confirmPayment() {
  if (!paymentDraft.value || !transactionId.value.trim()) return

  processing.value = true
  try {
    await api.post('/payments/confirm', {
      payment_id: paymentDraft.value.payment_id,
      transaction_id: transactionId.value.trim(),
    })
    toast.success('Payment submitted for verification')
    paymentDraft.value = null
    transactionId.value = ''
    couponCode.value = ''
    await loadBaseData()
  } catch (error) {
    toast.error(error.response?.data?.detail || 'Failed to submit transaction ID')
  } finally {
    processing.value = false
  }
}

watch(() => route.query.plan, planId => {
  if (!planId) {
    selectedPlan.value = null
    return
  }
  selectedPlan.value = plans.value.find(plan => plan.id === planId) || null
  selectedCourse.value = null
  paymentDraft.value = null
})

watch(() => route.query.course_id, async courseId => {
  paymentDraft.value = null
  transactionId.value = ''
  if (courseId) {
    await loadCourseCheckout()
  } else {
    selectedCourse.value = null
  }
})

onMounted(async () => {
  await loadBaseData()
  if (route.query.course_id) await loadCourseCheckout()
})
</script>

<style scoped>
.payments-page { display: flex; flex-direction: column; gap: 24px; }
.page-head p { margin-top: 4px; }
.checkout-card { padding: 24px; }
.checkout-summary { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; }
.summary-label { font-size: 11px; font-weight: 800; color: var(--text3); text-transform: uppercase; letter-spacing: .08em; }
.summary-price { font-size: 34px; font-weight: 900; color: var(--p); }
.course-meta { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 12px; color: var(--text3); font-size: 13px; }
.course-meta span { padding: 6px 10px; border-radius: 999px; background: var(--bg3); }
.checkout-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.instruction-box { padding: 16px; border: 1px solid var(--border); border-radius: var(--r); background: var(--bg3); }
.instruction-title { font-size: 13px; font-weight: 800; color: var(--text); margin-bottom: 8px; }
.instruction-box p { margin: 0; color: var(--text2); }
.instruction-meta { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px; font-size: 12px; color: var(--text3); }
.checkout-actions { display: flex; gap: 12px; flex-wrap: wrap; }
.plans-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; }
.plan-card { position: relative; padding: 28px 20px; }
.plan-card.popular { border-color: var(--p); box-shadow: 0 0 0 2px var(--p); }
.plan-card.active { background: var(--p-soft); }
.plan-badge { position: absolute; top: -12px; left: 50%; transform: translateX(-50%); white-space: nowrap; }
.plan-price { font-size: 28px; font-weight: 900; color: var(--p); margin: 8px 0; }
.plan-price span { font-size: 14px; font-weight: 400; color: var(--text3); }
.plan-features { list-style: none; padding: 0; display: flex; flex-direction: column; gap: 8px; margin-top: 16px; }
.plan-features li { font-size: 13px; color: var(--text2); }
.section-head { margin-bottom: 18px; }
@media (max-width: 768px) {
  .checkout-summary { flex-direction: column; }
  .checkout-grid { grid-template-columns: 1fr; }
}
</style>
