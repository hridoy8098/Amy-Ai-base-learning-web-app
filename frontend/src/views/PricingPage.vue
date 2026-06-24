<template>
  <div class="pricing-page">
    <nav class="navbar">
      <div class="nav-container">
        <router-link to="/" class="nav-logo">🤖 Amy<span>Learn</span></router-link>
        <div class="nav-links">
          <router-link to="/login" class="btn btn-outline btn-sm">Login</router-link>
          <router-link to="/register" class="btn btn-primary btn-sm">Get Started</router-link>
        </div>
      </div>
    </nav>

    <div class="pricing-content">
      <h1 class="text-center">Simple, Transparent Subscription Pricing</h1>
      <p class="text-center text-muted mt-2 mb-4">Choose the AI plan that works for you. Upgrade anytime.</p>
      <div class="separate-note card mb-8">
        Paid courses are not included here. Every paid course has its own separate payment from the course page.
      </div>

      <div class="plans-grid" v-if="plans.length">
        <div v-for="plan in plans" :key="plan.id"
          class="plan-card card" :class="{popular: plan.popular}">
          <div class="plan-badge" v-if="plan.popular">⭐ Most Popular</div>
          <h3>{{ plan.name }}</h3>
          <div class="plan-price">
            <span class="price-amt">{{ plan.price === 0 ? 'Free' : '৳' + plan.price }}</span>
            <span class="price-period" v-if="plan.period">/{{ plan.period }}</span>
          </div>
          <ul class="plan-features">
            <li v-for="f in plan.features" :key="f">✅ {{ f }}</li>
          </ul>
          <router-link :to="plan.id === 'free' ? '/register' : '/register'" class="btn btn-primary w-full mt-6">
            {{ plan.id === 'free' ? 'Start Free' : 'Get ' + plan.name }}
          </router-link>
        </div>
      </div>

      <div class="faq card mt-8">
        <h3 class="mb-6">Frequently Asked Questions</h3>
        <div class="faq-list">
          <div class="faq-item">
            <h4>Can I cancel anytime?</h4>
            <p>Yes, you can cancel or change your plan at any time. No lock-in contracts.</p>
          </div>
          <div class="faq-item">
            <h4>What payment methods are accepted?</h4>
            <p>We accept bKash and Nagad. More payment options coming soon.</p>
          </div>
          <div class="faq-item">
            <h4>Is there a free trial?</h4>
            <p>Yes! The Free plan gives you 10 Amy messages and 3 quiz generations per day to try before upgrading.</p>
          </div>
          <div class="faq-item">
            <h4>Will Amy work in Bangla?</h4>
            <p>Yes! Amy fully supports Bangla voice and text conversations.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
const plans = ref([])
onMounted(async () => {
  try { const r = await api.get('/payments/plans'); plans.value = r.data } catch {}
})
</script>

<style scoped>
.pricing-page { min-height: 100vh; background: var(--bg); }
.navbar { position: sticky; top: 0; z-index: 100; background: var(--bg2); border-bottom: 1px solid var(--border); }
.nav-container { max-width: 1100px; margin: 0 auto; padding: 0 24px; height: 64px; display: flex; align-items: center; justify-content: space-between; }
.nav-logo { font-size: 20px; font-weight: 800; color: var(--text); text-decoration: none; }
.nav-logo span { color: var(--p); }
.nav-links { display: flex; gap: 12px; }
.pricing-content { max-width: 1100px; margin: 0 auto; padding: 60px 24px; }
.separate-note { max-width: 760px; margin: 0 auto; text-align: center; color: var(--text2); }
.plans-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 24px; }
.plan-card { position: relative; padding: 32px 24px; text-align: center; }
.plan-card.popular { border: 2px solid var(--p); box-shadow: 0 0 0 4px var(--p-soft); }
.plan-badge { background: linear-gradient(135deg, var(--p), #a78bfa); color: #fff; font-size: 11px; font-weight: 700; padding: 4px 12px; border-radius: 20px; display: inline-block; margin-bottom: 12px; }
.plan-card h3 { font-size: 20px; margin-bottom: 8px; }
.plan-price { margin: 16px 0; }
.price-amt { font-size: 36px; font-weight: 900; color: var(--p); }
.price-period { font-size: 14px; color: var(--text3); }
.plan-features { list-style: none; padding: 0; text-align: left; display: flex; flex-direction: column; gap: 10px; }
.plan-features li { font-size: 13px; color: var(--text2); }
.faq { max-width: 700px; margin: 0 auto; }
.faq-list { display: flex; flex-direction: column; gap: 20px; }
.faq-item h4 { font-size: 15px; font-weight: 700; color: var(--text); margin-bottom: 6px; }
.faq-item p  { font-size: 14px; color: var(--text3); margin: 0; }
</style>
