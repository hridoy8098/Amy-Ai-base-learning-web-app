import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import gameAPI from '@/api/gameAPI'

export const useGamificationStore = defineStore('gamification', () => {
  // State
  const totalXP = ref(0)
  const tier = ref('bronze')
  const currentStreak = ref(0)
  const bestStreak = ref(0)

  const currentHearts = ref(3)
  const maxHearts = ref(3)
  const heartRegenTime = ref(null)

  const sessionXP = ref(0)
  const sessionHearts = ref(3)
  const comboCurrent = ref(0)

  const weakAreas = ref([])
  const loadingProgress = ref(false)
  const error = ref(null)

  // Computed
  const heartsPercentage = computed(() => {
    return (currentHearts.value / maxHearts.value) * 100
  })

  const canAttemptLevel = computed(() => {
    return currentHearts.value > 0
  })

  const tierDisplay = computed(() => {
    const tiers = {
      bronze: '🥉 Bronze',
      silver: '🥈 Silver',
      gold: '🥇 Gold',
      diamond: '💎 Diamond'
    }
    return tiers[tier.value] || tier.value
  })

  const streakDisplay = computed(() => {
    if (currentStreak.value === 0) return 'Start your streak! 🔥'
    if (currentStreak.value === 1) return '🔥 Keep it up!'
    if (currentStreak.value < 7) return `🔥 ${currentStreak.value} day streak!`
    if (currentStreak.value < 30) return `🔥🔥 ${currentStreak.value} day streak!`
    return `🔥🔥🔥 ${currentStreak.value} day streak!`
  })

  const weakAreasCount = computed(() => {
    return weakAreas.value.length
  })

  // Actions
  async function fetchUserProgress() {
    try {
      loadingProgress.value = true
      error.value = null
      const data = await gameAPI.getUserProgress()
      totalXP.value = data.total_xp
      tier.value = data.tier
      currentStreak.value = data.current_streak
      bestStreak.value = data.best_streak
      currentHearts.value = data.hearts?.current || 3
      maxHearts.value = data.hearts?.total || 3
    } catch (err) {
      error.value = err.message
    } finally {
      loadingProgress.value = false
    }
  }

  async function fetchWeakAreas() {
    try {
      error.value = null
      const data = await gameAPI.getWeakAreas()
      weakAreas.value = data.weak_areas || []
    } catch (err) {
      error.value = err.message
    }
  }

  function addXP(xp) {
    totalXP.value += xp
    sessionXP.value += xp
  }

  function updateCombo(combo) {
    comboCurrent.value = combo
  }

  function useHeart() {
    if (currentHearts.value > 0 && sessionHearts.value > 0) {
      currentHearts.value--
      sessionHearts.value--
    }
  }

  function restoreHeart() {
    if (currentHearts.value < maxHearts.value) {
      currentHearts.value++
    }
  }

  function restoreAllHearts() {
    currentHearts.value = maxHearts.value
  }

  function updateStreak(streak) {
    currentStreak.value = streak
  }

  function resetSession() {
    sessionXP.value = 0
    sessionHearts.value = maxHearts.value
    comboCurrent.value = 0
  }

  return {
    // State
    totalXP,
    tier,
    currentStreak,
    bestStreak,
    currentHearts,
    maxHearts,
    heartRegenTime,
    sessionXP,
    sessionHearts,
    comboCurrent,
    weakAreas,
    loadingProgress,
    error,

    // Computed
    heartsPercentage,
    canAttemptLevel,
    tierDisplay,
    streakDisplay,
    weakAreasCount,

    // Actions
    fetchUserProgress,
    fetchWeakAreas,
    addXP,
    updateCombo,
    useHeart,
    restoreHeart,
    restoreAllHearts,
    updateStreak,
    resetSession
  }
})
