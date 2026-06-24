/**
 * Game Learning System API
 * All game endpoints with proper error handling and response types
 */

import api from '@/api'

const gameAPI = {
  // ═══════════════════════════════════════════════════════════════════════════
  // CURRICULUM ENDPOINTS
  // ═══════════════════════════════════════════════════════════════════════════

  // Get all subjects with user progress
  async getSubjects() {
    try {
      const response = await api.get('/game/subjects')
      return response.data
    } catch (error) {
      console.error('Error fetching subjects:', error)
      throw error
    }
  },

  // Get topics under a subject
  async getTopics(subjectId) {
    try {
      const response = await api.get(`/game/subjects/${subjectId}/topics`)
      return response.data
    } catch (error) {
      console.error('Error fetching topics:', error)
      throw error
    }
  },

  // Get progression map for topic (levels with progress)
  async getLevels(topicId) {
    try {
      const response = await api.get(`/game/topics/${topicId}/levels`)
      return response.data
    } catch (error) {
      console.error('Error fetching levels:', error)
      throw error
    }
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // GAMEPLAY ENDPOINTS
  // ═══════════════════════════════════════════════════════════════════════════

  // Start a level
  async startLevel(levelId) {
    try {
      const response = await api.post(`/game/levels/${levelId}/start`)
      return response.data
    } catch (error) {
      console.error('Error starting level:', error)
      throw error
    }
  },

  // Submit an answer
  async submitAnswer(attemptId, questionId, userAnswer, timeTaken, confidence) {
    try {
      const response = await api.post(
        `/game/attempts/${attemptId}/answer`,
        {
          question_id: questionId,
          user_answer: userAnswer,
          time_taken_seconds: timeTaken,
          confidence_level: confidence
        }
      )
      return response.data
    } catch (error) {
      console.error('Error submitting answer:', error)
      throw error
    }
  },

  // Complete a level
  async completeLevel(attemptId) {
    try {
      const response = await api.post(`/game/attempts/${attemptId}/complete`)
      return response.data
    } catch (error) {
      console.error('Error completing level:', error)
      throw error
    }
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // PROGRESS ENDPOINTS
  // ═══════════════════════════════════════════════════════════════════════════

  // Get user overall progress
  async getUserProgress() {
    try {
      const response = await api.get('/game/user/progress')
      return response.data
    } catch (error) {
      console.error('Error fetching user progress:', error)
      throw error
    }
  },

  // Get weak areas
  async getWeakAreas() {
    try {
      const response = await api.get('/game/user/weak-areas')
      return response.data
    } catch (error) {
      console.error('Error fetching weak areas:', error)
      throw error
    }
  },

  // Get leaderboard
  async getLeaderboard(period = 'weekly', limit = 10) {
    try {
      const response = await api.get('/game/leaderboard', { params: { period, limit } })
      return response.data
    } catch (error) {
      console.error('Error fetching leaderboard:', error)
      throw error
    }
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // ADMIN ENDPOINTS (For admin panel)
  // ═══════════════════════════════════════════════════════════════════════════

  // Create subject
  async createSubject(name, description, icon, color) {
    try {
      const response = await api.post('/admin/game/subjects', {
        name,
        description,
        icon,
        color
      })
      return response.data
    } catch (error) {
      console.error('Error creating subject:', error)
      throw error
    }
  },

  // Create topic
  async createTopic(subjectId, name, description, icon) {
    try {
      const response = await api.post(
        `/admin/game/subjects/${subjectId}/topics`,
        { name, description, icon }
      )
      return response.data
    } catch (error) {
      console.error('Error creating topic:', error)
      throw error
    }
  },

  // Create level
  async createLevel(topicId, title, levelNumber, difficulty, questionCount, xpReward) {
    try {
      const response = await api.post(
        `/admin/game/topics/${topicId}/levels`,
        {
          title,
          level_number: levelNumber,
          difficulty,
          question_count: questionCount,
          xp_reward: xpReward
        }
      )
      return response.data
    } catch (error) {
      console.error('Error creating level:', error)
      throw error
    }
  },

  // Upload questions
  async uploadQuestions(levelId, file) {
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await api.post(
        `/admin/game/questions/upload?level_id=${levelId}`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )
      return response.data
    } catch (error) {
      console.error('Error uploading questions:', error)
      throw error
    }
  },

  // Get admin dashboard stats
  async getAdminStats() {
    try {
      const response = await api.get('/admin/game/dashboard/stats')
      return response.data
    } catch (error) {
      console.error('Error fetching admin stats:', error)
      throw error
    }
  }
}

export default gameAPI
