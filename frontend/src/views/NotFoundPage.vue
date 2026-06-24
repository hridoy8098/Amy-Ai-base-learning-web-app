<template>
  <div class="not-found">
    <div class="nf-content">
      <div class="nf-robot">🤖</div>
      <h1>404</h1>
      <h2>Page Not Found</h2>
      <p>Oops! Amy couldn't find this page. Let's go back to learning!</p>
      <div class="nf-actions">
        <router-link to="/dashboard" class="btn btn-primary">Go to Dashboard</router-link>
        <router-link to="/" class="btn btn-outline">Home</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.not-found { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: var(--bg); padding: 24px; }
.nf-content { text-align: center; }
.nf-robot { font-size: 80px; animation: bounce 2s ease-in-out infinite; margin-bottom: 16px; }
@keyframes bounce { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-16px)} }
h1 { font-size: 80px; font-weight: 900; color: var(--p); line-height: 1; }
h2 { font-size: 24px; margin: 8px 0 12px; }
p  { color: var(--text3); margin-bottom: 28px; }
.nf-actions { display: flex; gap: 12px; justify-content: center; }
</style>
