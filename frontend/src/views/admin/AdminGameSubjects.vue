<template>
  <div class="admin-game-subjects">
    <div class="header">
      <h1>📚 Manage Game Subjects</h1>
      <button @click="showForm = !showForm" class="btn btn-primary" :disabled="loading">
        {{ showForm ? '✕ Cancel' : '+ New Subject' }}
      </button>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="error-message">
      ⚠️ {{ error }}
    </div>

    <!-- Form -->
    <div v-if="showForm" class="form-card">
      <h2>{{ editingId ? 'Edit Subject' : 'Create New Subject' }}</h2>
      <form @submit.prevent="saveSubject">
        <div class="form-group">
          <label>Subject Name *</label>
          <input v-model="form.name" type="text" required :disabled="loading" />
        </div>

        <div class="form-group">
          <label>Description</label>
          <textarea v-model="form.description" rows="3" :disabled="loading"></textarea>
        </div>

        <div class="form-group">
          <label>Icon/Emoji</label>
          <input v-model="form.icon" type="text" placeholder="e.g., 📚" :disabled="loading" />
        </div>

        <div class="form-group">
          <label>Color</label>
          <input v-model="form.color" type="color" :disabled="loading" />
        </div>

        <div class="form-actions">
          <button type="button" @click="showForm = false" class="btn btn-secondary" :disabled="loading">Cancel</button>
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? '⏳ Saving...' : (editingId ? 'Update' : 'Create') }}
          </button>
        </div>
      </form>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !showForm" class="loading">
      <div class="spinner"></div>
      <p>Loading subjects...</p>
    </div>

    <!-- List -->
    <div v-else class="subjects-list">
      <h2>Subjects ({{ subjects.length }})</h2>
      
      <div v-if="subjects.length === 0" class="empty-state">
        <p>No subjects created yet. Create your first subject above!</p>
      </div>
      
      <table v-else class="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Description</th>
            <th>Topics</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="subject in subjects" :key="subject.id">
            <td>{{ subject.icon }} {{ subject.name }}</td>
            <td>{{ subject.description || '-' }}</td>
            <td>{{ subject.topic_count || 0 }}</td>
            <td>
              <button @click="editSubject(subject)" class="btn-icon">✎</button>
              <button @click="deleteSubject(subject.id)" class="btn-icon delete">✕</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import api from '@/api'

export default {
  name: 'AdminGameSubjects',
  data() {
    return {
      subjects: [],
      form: {
        name: '',
        description: '',
        icon: '',
        color: '#667eea'
      },
      showForm: false,
      editingId: null,
      loading: false,
      error: null
    }
  },
  methods: {
    async fetchSubjects() {
      this.loading = true
      this.error = null
      try {
        console.log('Fetching subjects from API...')
        const response = await api.get('/admin/game/subjects')
        console.log('✅ Subjects fetched:', response.data)
        this.subjects = response.data.subjects || []
      } catch (err) {
        console.error('❌ Error fetching subjects:', err.response?.status, err.response?.data)
        this.error = err.response?.data?.detail || 'Failed to load subjects'
      } finally {
        this.loading = false
      }
    },

    async saveSubject() {
      if (!this.form.name.trim()) {
        this.error = 'Subject name is required'
        return
      }

      this.loading = true
      this.error = null

      try {
        if (this.editingId) {
          // Update existing subject
          await api.put(`/admin/game/subjects/${this.editingId}`, {
            name: this.form.name,
            description: this.form.description,
            icon: this.form.icon,
            color: this.form.color
          })
        } else {
          // Create new subject
          await api.post('/admin/game/subjects', {
            name: this.form.name,
            description: this.form.description,
            icon: this.form.icon,
            color: this.form.color
          })
        }
        
        await this.fetchSubjects()
        this.resetForm()
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to save subject'
        console.error(err)
      } finally {
        this.loading = false
      }
    },

    editSubject(subject) {
      this.form = {
        name: subject.name,
        description: subject.description || '',
        icon: subject.icon || '',
        color: subject.color || '#667eea'
      }
      this.editingId = subject.id
      this.showForm = true
    },

    async deleteSubject(id) {
      if (!confirm('Delete this subject?')) return

      this.loading = true
      this.error = null

      try {
        await api.delete(`/admin/game/subjects/${id}`)
        await this.fetchSubjects()
      } catch (err) {
        this.error = 'Failed to delete subject'
        console.error(err)
      } finally {
        this.loading = false
      }
    },

    resetForm() {
      this.form = { name: '', description: '', icon: '', color: '#667eea' }
      this.editingId = null
      this.showForm = false
    }
  },
  mounted() {
    this.fetchSubjects()
  }
}
</script>

<style scoped lang="scss">
.admin-game-subjects {
  padding: 30px;

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
  }

  h1 {
    margin: 0;
    color: #333;
  }

  h2 {
    margin: 20px 0 15px 0;
    color: #333;
    font-size: 18px;
  }

  .error-message {
    background: #ffebee;
    border: 1px solid #f44336;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 20px;
    color: #c62828;
  }

  .loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 100px 30px;
    color: #999;

    .spinner {
      width: 40px;
      height: 40px;
      border: 4px solid #f3f3f3;
      border-top: 4px solid #667eea;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-bottom: 20px;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  }

  .form-card {
    background: white;
    border-radius: 12px;
    padding: 25px;
    margin-bottom: 30px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

    form {
      max-width: 600px;
    }

    .form-group {
      margin-bottom: 20px;

      label {
        display: block;
        margin-bottom: 8px;
        color: #333;
        font-weight: 600;
      }

      input,
      textarea {
        width: 100%;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 6px;
        font-family: inherit;

        &:focus {
          outline: none;
          border-color: #667eea;
        }

        &:disabled {
          background: #f5f5f5;
          cursor: not-allowed;
        }
      }
    }

    .form-actions {
      display: flex;
      gap: 10px;
      margin-top: 20px;
    }
  }

  .subjects-list {
    background: white;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .empty-state {
    text-align: center;
    padding: 60px 20px;
    color: #999;
  }

  .data-table {
    width: 100%;
    border-collapse: collapse;

    thead {
      border-bottom: 2px solid #ddd;

      th {
        text-align: left;
        padding: 12px;
        color: #333;
        font-weight: 600;
      }
    }

    tbody tr {
      border-bottom: 1px solid #eee;

      &:hover {
        background: #f9f9f9;
      }
    }

    td {
      padding: 12px;
      color: #666;
    }

    .btn-icon {
      background: none;
      border: none;
      cursor: pointer;
      font-size: 16px;
      padding: 4px 8px;
      margin: 0 4px;
      border-radius: 4px;

      &:hover {
        background: rgba(0, 0, 0, 0.1);
      }

      &.delete {
        color: #f44336;
      }
    }
  }
}
</style>
