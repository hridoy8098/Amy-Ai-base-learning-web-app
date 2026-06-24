<template>
  <div class="app-layout">
    <Sidebar ref="sidebarRef" />
    <div class="main-wrap" :class="{ 'sidebar-open': sidebarOpen }">
      <Topbar @toggle-sidebar="toggleSidebar" />
      <main class="main-content">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, provide } from 'vue'
import Sidebar from './Sidebar.vue'
import Topbar  from './Topbar.vue'

const sidebarOpen = ref(true)

function toggleSidebar() {
  const sidebar = document.querySelector('.sidebar')
  if (!sidebar) return
  if (window.innerWidth <= 768) {
    sidebar.classList.toggle('open')
  } else {
    sidebar.classList.toggle('collapsed')
    const mainWrap = document.querySelector('.main-wrap')
    if (mainWrap) {
      mainWrap.style.marginLeft = sidebar.classList.contains('collapsed') ? '0' : 'var(--sidebar-w)'
    }
  }
}

provide('toggleSidebar', toggleSidebar)
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  background: var(--bg);
}
.main-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  margin-left: var(--sidebar-w);
  transition: margin-left 0.3s ease;
}
.main-content {
  flex: 1;
  padding: 28px 32px;
  overflow-y: auto;
  min-height: calc(100vh - var(--topbar-h));
}
@media (max-width: 768px) {
  .main-wrap { margin-left: 0 !important; }
  .main-content { padding: 16px; }
}
</style>
