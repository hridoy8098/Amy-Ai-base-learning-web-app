<template>
  <div class="leaderboard-page">
    <!-- Header -->
    <header class="leaderboard-header">
      <h1>🏆 Global Leaderboard</h1>
      <div class="period-selector">
        <button
          v-for="period in periods"
          :key="period"
          @click="selectedPeriod = period"
          :class="{ active: selectedPeriod === period }"
          class="period-btn"
        >
          {{ formatPeriod(period) }}
        </button>
      </div>
    </header>

    <!-- Loading State -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Loading leaderboard...</p>
    </div>

    <!-- Leaderboard -->
    <div v-else class="leaderboard-container">
      <!-- Rank 1-3 (Podium) -->
      <div v-if="leaderboard.length > 0" class="podium">
        <div
          v-for="rank in [2, 1, 3].filter(r => r <= leaderboard.length)"
          :key="rank"
          class="podium-position"
          :class="`rank-${rank}`"
        >
          <div class="medal">
            {{ getMedal(rank) }}
          </div>
          <div class="podium-player">
            <img
              v-if="leaderboard[rank - 1].avatar"
              :src="leaderboard[rank - 1].avatar"
              :alt="leaderboard[rank - 1].name"
              class="avatar"
            />
            <div v-else class="avatar-placeholder">{{ leaderboard[rank - 1].name.charAt(0) }}</div>
            <h3>{{ leaderboard[rank - 1].name }}</h3>
            <p class="player-tier">{{ leaderboard[rank - 1].tier }}</p>
            <div class="xp-amount">{{ leaderboard[rank - 1].xp | formatNumber }} XP</div>
          </div>
          <div class="height" :class="`height-${rank}`"></div>
        </div>
      </div>

      <!-- Rank 4+ (Table) -->
      <div v-if="leaderboard.length > 3" class="leaderboard-table">
        <div class="table-header">
          <div class="col-rank">Rank</div>
          <div class="col-player">Player</div>
          <div class="col-tier">Tier</div>
          <div class="col-xp">XP</div>
          <div class="col-streak">Streak</div>
        </div>

        <div
          v-for="(player, index) in leaderboard.slice(3)"
          :key="index"
          class="table-row"
          :class="{ 'is-current-user': player.is_current_user }"
        >
          <div class="col-rank">
            <span class="rank-number">{{ index + 4 }}</span>
          </div>
          <div class="col-player">
            <img
              v-if="player.avatar"
              :src="player.avatar"
              :alt="player.name"
              class="row-avatar"
            />
            <div v-else class="row-avatar-placeholder">{{ player.name.charAt(0) }}</div>
            <span class="player-name">{{ player.name }}</span>
            <span v-if="player.is_current_user" class="badge-you">You</span>
          </div>
          <div class="col-tier">{{ player.tier }}</div>
          <div class="col-xp">
            <span class="xp-badge">{{ player.xp | formatNumber }}</span>
          </div>
          <div class="col-streak">
            <span v-if="player.streak > 0" class="streak-badge">🔥 {{ player.streak }}</span>
            <span v-else class="no-streak">-</span>
          </div>
        </div>
      </div>

      <!-- Your Rank Card (if not in top 3) -->
      <div v-if="!userInTopThree && currentUserRank" class="your-rank-card">
        <h3>Your Rank</h3>
        <div class="rank-display">
          <div class="rank-badge">#{{ currentUserRank }}</div>
          <div class="rank-stats">
            <div class="stat">
              <span class="label">XP</span>
              <span class="value">{{ currentUserXP | formatNumber }}</span>
            </div>
            <div class="stat">
              <span class="label">Tier</span>
              <span class="value">{{ currentUserTier }}</span>
            </div>
            <div class="stat">
              <span class="label">Streak</span>
              <span class="value">🔥 {{ currentUserStreak }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import gameAPI from '@/api/gameAPI'

export default {
  name: 'LeaderboardPage',
  data() {
    return {
      periods: ['weekly', 'monthly', 'all_time'],
      selectedPeriod: 'weekly',
      leaderboard: [],
      loading: false,
      currentUserRank: null,
      currentUserXP: 0,
      currentUserTier: '',
      currentUserStreak: 0
    }
  },
  computed: {
    userInTopThree() {
      return this.leaderboard.some((p, i) => p.is_current_user && i < 3)
    }
  },
  watches: {
    selectedPeriod(newPeriod) {
      this.loadLeaderboard(newPeriod)
    }
  },
  methods: {
    async loadLeaderboard(period) {
      try {
        this.loading = true
        const data = await gameAPI.getLeaderboard(period, 100)
        this.leaderboard = data.leaderboard

        // Find current user's rank
        const currentUser = this.leaderboard.find(p => p.is_current_user)
        if (currentUser) {
          this.currentUserRank = this.leaderboard.indexOf(currentUser) + 1
          this.currentUserXP = currentUser.xp
          this.currentUserTier = currentUser.tier
          this.currentUserStreak = currentUser.streak || 0
        }
      } catch (error) {
        console.error('Error loading leaderboard:', error)
      } finally {
        this.loading = false
      }
    },

    getMedal(rank) {
      const medals = { 1: '🥇', 2: '🥈', 3: '🥉' }
      return medals[rank] || ''
    },

    formatPeriod(period) {
      const formats = { weekly: 'This Week', monthly: 'This Month', all_time: 'All Time' }
      return formats[period] || period
    }
  },
  filters: {
    formatNumber(value) {
      return value?.toLocaleString() || '0'
    }
  },
  mounted() {
    this.loadLeaderboard(this.selectedPeriod)
  }
}
</script>

<style scoped lang="scss">
.leaderboard-page {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  padding: 20px;
}

.leaderboard-header {
  background: rgba(255, 255, 255, 0.95);
  padding: 30px 20px;
  border-radius: 16px;
  margin-bottom: 30px;
  text-align: center;

  h1 {
    margin: 0 0 20px 0;
    color: #333;
    font-size: 32px;
  }

  .period-selector {
    display: flex;
    gap: 10px;
    justify-content: center;
    flex-wrap: wrap;

    .period-btn {
      padding: 10px 20px;
      border: 2px solid #e0e0e0;
      background: white;
      border-radius: 8px;
      cursor: pointer;
      font-weight: 600;
      transition: all 0.3s;

      &:hover {
        border-color: #667eea;
        color: #667eea;
      }

      &.active {
        background: #667eea;
        color: white;
        border-color: #667eea;
      }
    }
  }
}

.leaderboard-container {
  max-width: 1000px;
  margin: 0 auto;
}

.podium {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 20px;
  margin-bottom: 40px;
  perspective: 1000px;

  .podium-position {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;

    &.rank-1 {
      flex-direction: column-reverse;
      order: 2;
    }

    &.rank-2 {
      order: 1;
    }

    &.rank-3 {
      order: 3;
    }

    .medal {
      font-size: 48px;
      margin: 10px 0;
    }

    .podium-player {
      background: rgba(255, 255, 255, 0.95);
      padding: 20px;
      border-radius: 12px;
      margin-bottom: 20px;
      min-width: 180px;

      .avatar,
      .avatar-placeholder {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        margin: 0 auto 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        font-size: 24px;
        font-weight: bold;
      }

      .avatar {
        object-fit: cover;
      }

      h3 {
        margin: 0 0 8px 0;
        color: #333;
        font-size: 16px;
      }

      .player-tier {
        margin: 0 0 8px 0;
        color: #999;
        font-size: 12px;
      }

      .xp-amount {
        font-weight: bold;
        color: #667eea;
        font-size: 18px;
      }
    }

    .height {
      background: rgba(255, 255, 255, 0.95);
      border-radius: 8px 8px 0 0;
      width: 140px;

      &.height-1 {
        height: 150px;
      }

      &.height-2 {
        height: 120px;
      }

      &.height-3 {
        height: 100px;
      }
    }
  }
}

.leaderboard-table {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);

  .table-header {
    display: grid;
    grid-template-columns: 80px 1fr 120px 120px 100px;
    gap: 15px;
    padding: 20px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    font-weight: 600;
    font-size: 13px;
    text-transform: uppercase;

    .col-rank,
    .col-tier,
    .col-xp,
    .col-streak {
      text-align: center;
    }
  }

  .table-row {
    display: grid;
    grid-template-columns: 80px 1fr 120px 120px 100px;
    gap: 15px;
    padding: 20px;
    border-bottom: 1px solid #f0f0f0;
    align-items: center;
    transition: background-color 0.3s;

    &:hover {
      background: rgba(102, 126, 234, 0.05);
    }

    &.is-current-user {
      background: rgba(102, 126, 234, 0.15);
      font-weight: 600;
    }

    .col-rank {
      text-align: center;

      .rank-number {
        display: inline-block;
        width: 40px;
        height: 40px;
        background: rgba(102, 126, 234, 0.2);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: #667eea;
      }
    }

    .col-player {
      display: flex;
      align-items: center;
      gap: 12px;

      .row-avatar,
      .row-avatar-placeholder {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        font-size: 16px;
        font-weight: bold;
        flex-shrink: 0;
      }

      .row-avatar {
        object-fit: cover;
      }

      .player-name {
        flex: 1;
        color: #333;
      }

      .badge-you {
        background: #667eea;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
      }
    }

    .col-tier {
      text-align: center;
      color: #666;
    }

    .col-xp {
      text-align: right;

      .xp-badge {
        background: rgba(255, 152, 0, 0.2);
        padding: 6px 12px;
        border-radius: 6px;
        color: #ff9800;
        font-weight: 600;
      }
    }

    .col-streak {
      text-align: center;

      .streak-badge {
        display: inline-block;
        font-weight: 600;
      }

      .no-streak {
        color: #ccc;
      }
    }
  }
}

.your-rank-card {
  background: rgba(255, 255, 255, 0.95);
  padding: 30px;
  border-radius: 12px;
  margin-top: 40px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);

  h3 {
    margin: 0 0 20px 0;
    color: #333;
    text-align: center;
  }

  .rank-display {
    display: flex;
    align-items: center;
    gap: 40px;
    justify-content: center;

    .rank-badge {
      font-size: 48px;
      font-weight: bold;
      color: #667eea;
      background: rgba(102, 126, 234, 0.1);
      width: 100px;
      height: 100px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .rank-stats {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 30px;

      .stat {
        display: flex;
        flex-direction: column;
        gap: 8px;
        text-align: center;

        .label {
          font-size: 12px;
          color: #999;
          text-transform: uppercase;
        }

        .value {
          font-size: 24px;
          font-weight: bold;
          color: #333;
        }
      }
    }
  }
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 20px;

  .spinner {
    width: 60px;
    height: 60px;
    border: 5px solid rgba(255, 255, 255, 0.3);
    border-top: 5px solid white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  p {
    margin-top: 25px;
    color: white;
    font-size: 16px;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .podium {
    flex-wrap: wrap;
    gap: 15px;

    .podium-position {
      &.rank-1,
      &.rank-2,
      &.rank-3 {
        order: initial;
        flex: 1;
        min-width: 140px;
      }

      .height {
        display: none;
      }

      .podium-player {
        min-width: auto;
      }
    }
  }

  .leaderboard-table {
    .table-header,
    .table-row {
      grid-template-columns: 50px 1fr 80px;

      .col-xp,
      .col-streak {
        display: none;
      }
    }
  }

  .your-rank-card {
    .rank-display {
      flex-direction: column;
      gap: 30px;

      .rank-stats {
        grid-template-columns: 1fr;
      }
    }
  }
}
</style>
