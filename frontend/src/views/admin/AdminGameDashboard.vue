<template>
  <div class="admin-game-dashboard">
    <h1>🎮 Game Management Dashboard</h1>
    
    <div class="dashboard-grid">
      <!-- Stats Cards -->
      <router-link to="/admin/game/subjects" class="stat-card">
        <div class="icon">📚</div>
        <div class="content">
          <h3>Subjects</h3>
          <p class="value">{{ stats.subjects }}</p>
          <span class="manage-btn">Manage →</span>
        </div>
      </router-link>

      <router-link to="/admin/game/topics" class="stat-card">
        <div class="icon">📖</div>
        <div class="content">
          <h3>Topics</h3>
          <p class="value">{{ stats.topics }}</p>
          <span class="manage-btn">Manage →</span>
        </div>
      </router-link>

      <router-link to="/admin/game/levels" class="stat-card">
        <div class="icon">🎯</div>
        <div class="content">
          <h3>Levels</h3>
          <p class="value">{{ stats.levels }}</p>
          <span class="manage-btn">Manage →</span>
        </div>
      </router-link>

      <router-link to="/admin/game/questions" class="stat-card">
        <div class="icon">❓</div>
        <div class="content">
          <h3>Questions</h3>
          <p class="value">{{ stats.questions }}</p>
          <span class="manage-btn">Manage →</span>
        </div>
      </router-link>
    </div>

    <div class="quick-stats">
      <h2>Quick Stats</h2>
      <div class="stats-list">
        <div class="stat">
          <span>Active Users:</span>
          <strong>156</strong>
        </div>
        <div class="stat">
          <span>Levels Completed:</span>
          <strong>892</strong>
        </div>
        <div class="stat">
          <span>Avg Score:</span>
          <strong>78%</strong>
        </div>
        <div class="stat">
          <span>Total XP Earned:</span>
          <strong>45.2K</strong>
        </div>
      </div>
    </div>

    <div class="menu">
      <h2>Management Menu</h2>
      <div class="menu-buttons">
        <router-link to="/admin/game/subjects" class="btn btn-primary">Manage Subjects</router-link>
        <router-link to="/admin/game/topics" class="btn btn-primary">Manage Topics</router-link>
        <router-link to="/admin/game/levels" class="btn btn-primary">Manage Levels</router-link>
        <router-link to="/admin/game/questions" class="btn btn-primary">Manage Questions</router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminGameDashboard',
  data() {
    return {
      stats: {
        subjects: 4,
        topics: 12,
        levels: 45,
        questions: 1200
      }
    }
  }
}
</script>

<style scoped lang="scss">
.admin-game-dashboard {
  padding: 30px;
  background: #f5f5f5;
  min-height: 100vh;

  h1 {
    margin-bottom: 30px;
    color: #333;
  }

  h2 {
    margin: 30px 0 20px 0;
    color: #333;
    font-size: 20px;
  }
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  display: flex;
  gap: 20px;
  align-items: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  text-decoration: none;
  color: inherit;
  cursor: pointer;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
  }

  .icon {
    font-size: 40px;
    min-width: 50px;
    text-align: center;
  }

  .content {
    flex: 1;

    h3 {
      margin: 0 0 8px 0;
      color: #333;
      font-size: 14px;
      text-transform: uppercase;
    }

    .value {
      margin: 0 0 10px 0;
      font-size: 28px;
      font-weight: bold;
      color: #667eea;
    }

    .manage-btn {
      color: #667eea;
      font-size: 13px;
      font-weight: 600;
    }
  }
}

.quick-stats {
  background: white;
  border-radius: 12px;
  padding: 25px;
  margin-bottom: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

  .stats-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 20px;
  }

  .stat {
    display: flex;
    flex-direction: column;
    gap: 8px;

    span {
      color: #999;
      font-size: 12px;
    }

    strong {
      font-size: 24px;
      color: #667eea;
    }
  }
}

.menu {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

  .menu-buttons {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
  }
}
</style>
