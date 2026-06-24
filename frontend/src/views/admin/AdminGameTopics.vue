<template>
  <div class="admin-game-topics">
    <div class="header">
      <h1>📖 Manage Game Topics</h1>
      <button @click="showForm = !showForm" class="btn btn-primary">
        {{ showForm ? '✕ Cancel' : '+ New Topic' }}
      </button>
    </div>

    <div v-if="error" class="error-message">⚠️ {{ error }}</div>

    <div v-if="showForm" class="form-card">
      <h2>{{ editingId ? 'Edit Topic' : 'Create New Topic' }}</h2>
      <form @submit.prevent="saveTopic">
        <div class="form-group">
          <label>Topic Name *</label>
          <input v-model="form.name" type="text" required />
        </div>

        <div class="form-group">
          <label>Subject ID *</label>
          <input v-model="form.subject_id" type="number" required />
        </div>

        <div class="form-group">
          <label>Description</label>
          <textarea v-model="form.description" rows="3"></textarea>
        </div>

        <div class="form-actions">
          <button type="button" @click="showForm = false" class="btn btn-secondary">Cancel</button>
          <button type="submit" class="btn btn-primary">{{ editingId ? 'Update' : 'Create' }}</button>
        </div>
      </form>
    </div>

    <div class="topics-list">
      <h2>Topics</h2>
      <p>Coming soon...</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminGameTopics',
  data() {
    return {
      form: { name: '', subject_id: '', description: '' },
      showForm: false,
      editingId: null,
      error: null
    }
  },
  methods: {
    saveTopic() {
      console.log('Saving topic:', this.form)
      this.form = { name: '', subject_id: '', description: '' }
      this.showForm = false
    }
  }
}
</script>

<style scoped lang="scss">
.admin-game-topics {
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
      select,
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
      }
    }

    .form-actions {
      display: flex;
      gap: 10px;
      margin-top: 20px;
    }
  }

  .topics-list {
    background: white;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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

    .badge {
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;

      &.easy {
        background: rgba(76, 175, 80, 0.2);
        color: #4caf50;
      }

      &.medium {
        background: rgba(255, 152, 0, 0.2);
        color: #ff9800;
      }

      &.hard {
        background: rgba(244, 67, 54, 0.2);
        color: #f44336;
      }
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
