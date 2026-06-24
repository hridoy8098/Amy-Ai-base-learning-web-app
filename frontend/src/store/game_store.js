import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import gameAPI from '@/api/gameAPI'

export const useGameStore = defineStore('game', () => {
  // State
  const subjects = ref([])
  const currentSubject = ref(null)
  const currentTopic = ref(null)
  const currentLevel = ref(null)

  const currentAttempt = ref(null)
  const currentQuestions = ref([])
  const currentQuestionIndex = ref(0)

  const lastLevelResult = ref(null)

  const loadingSubjects = ref(false)
  const loadingTopics = ref(false)
  const loadingLevels = ref(false)
  const loadingGameStart = ref(false)
  const loadingAnswer = ref(false)
  const error = ref(null)

  // Getters (Computed)
  const currentQuestion = computed(() => {
    if (currentQuestionIndex.value < currentQuestions.value.length) {
      return currentQuestions.value[currentQuestionIndex.value]
    }
    return null
  })

  const isLastQuestion = computed(() => {
    return currentQuestionIndex.value === currentQuestions.value.length - 1
  })

  const questionsAnswered = computed(() => {
    return currentQuestionIndex.value
  })

  const totalQuestions = computed(() => {
    return currentQuestions.value.length
  })

  const progressPercentage = computed(() => {
    const total = currentQuestions.value.length
    if (total === 0) return 0
    return Math.round(((currentQuestionIndex.value + 1) / total) * 100)
  })

  // Actions
  async function fetchSubjects() {
    try {
      loadingSubjects.value = true
      error.value = null
      const data = await gameAPI.getSubjects()
      subjects.value = data.subjects
    } catch (err) {
      error.value = err.message
    } finally {
      loadingSubjects.value = false
    }
  }

  async function fetchTopics(subjectId) {
    try {
      loadingTopics.value = true
      error.value = null
      const data = await gameAPI.getTopics(subjectId)
      currentTopic.value = null
      return data.topics
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loadingTopics.value = false
    }
  }

  async function fetchLevels(topicId) {
    try {
      loadingLevels.value = true
      error.value = null
      const data = await gameAPI.getLevels(topicId)
      return data.levels
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loadingLevels.value = false
    }
  }

  async function fetchLeaderboard(period = 'weekly', limit = 10) {
    try {
      error.value = null
      const data = await gameAPI.getLeaderboard(period, limit)
      return data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  async function startLevel(levelId) {
    try {
      loadingGameStart.value = true
      error.value = null
      const data = await gameAPI.startLevel(levelId)
      currentAttempt.value = data.attempt_id
      currentQuestions.value = data.questions
      currentLevel.value = data.level
      currentQuestionIndex.value = 0
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loadingGameStart.value = false
    }
  }

  async function submitAnswer({ attemptId, questionId, answer, timeTaken, confidence }) {
    try {
      loadingAnswer.value = true
      const data = await gameAPI.submitAnswer(attemptId, questionId, answer, timeTaken, confidence)
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loadingAnswer.value = false
    }
  }

  async function completeLevel(attemptId) {
    try {
      const data = await gameAPI.completeLevel(attemptId)
      lastLevelResult.value = data
      return data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  function nextQuestion() {
    if (currentQuestionIndex.value < currentQuestions.value.length - 1) {
      currentQuestionIndex.value++
    }
  }

  function prevQuestion() {
    if (currentQuestionIndex.value > 0) {
      currentQuestionIndex.value--
    }
  }

  function jumpToQuestion(index) {
    if (index >= 0 && index < currentQuestions.value.length) {
      currentQuestionIndex.value = index
    }
  }

  function resetGame() {
    currentAttempt.value = null
    currentQuestions.value = []
    currentQuestionIndex.value = 0
    lastLevelResult.value = null
    error.value = null
  }

  function setCurrentSubject(subject) {
    currentSubject.value = subject
  }

  function setCurrentTopic(topic) {
    currentTopic.value = topic
  }

  function setCurrentLevel(level) {
    currentLevel.value = level
  }

  return {
    // State
    subjects,
    currentSubject,
    currentTopic,
    currentLevel,
    currentAttempt,
    currentQuestions,
    currentQuestionIndex,
    lastLevelResult,
    loadingSubjects,
    loadingTopics,
    loadingLevels,
    loadingGameStart,
    loadingAnswer,
    error,

    // Getters
    currentQuestion,
    isLastQuestion,
    questionsAnswered,
    totalQuestions,
    progressPercentage,

    // Actions
    fetchSubjects,
    fetchTopics,
    fetchLevels,
    fetchLeaderboard,
    startLevel,
    submitAnswer,
    completeLevel,
    nextQuestion,
    prevQuestion,
    jumpToQuestion,
    resetGame,
    setCurrentSubject,
    setCurrentTopic,
    setCurrentLevel
  }
})
