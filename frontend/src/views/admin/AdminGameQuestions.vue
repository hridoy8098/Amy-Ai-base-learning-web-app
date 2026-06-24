<template>
  <div class="admin-game-questions">
    <div class="header">
      <h1>Manage Game Questions</h1>
      <button @click="showForm = !showForm" class="btn btn-primary">
        {{ showForm ? 'Cancel' : '+ Add Question' }}
      </button>
    </div>

    <div v-if="showForm" class="form-card">
      <form @submit.prevent="saveQuestion">
        <div class="form-group">
          <label>Level *</label>
          <select v-model="form.level_id" required>
            <option value="">Select Level</option>
            <option value="1">Level 1-1</option>
            <option value="2">Level 1-2</option>
            <option value="3">Level 2-1</option>
            <option value="4">Level 2-2</option>
          </select>
        </div>

        <div class="form-group">
          <label>Question Text *</label>
          <textarea v-model="form.question_text" rows="3" required></textarea>
        </div>

        <div class="form-group">
          <label>Question Type *</label>
          <select v-model="form.question_type" required>
            <option value="multiple_choice">Multiple Choice</option>
            <option value="true_false">True/False</option>
            <option value="fill_blank">Fill in the Blank</option>
            <option value="matching">Matching</option>
            <option value="ordering">Ordering</option>
          </select>
        </div>

        <div v-if="form.question_type !== 'true_false'" class="form-group">
          <label>Options (one per line or JSON)</label>
          <textarea v-model="form.options" rows="4" placeholder="e.g.,&#10;Option A&#10;Option B&#10;Option C&#10;Option D"></textarea>
        </div>

        <div class="form-group">
          <label>Correct Answer *</label>
          <input v-model="form.correct_answer" type="text" placeholder="e.g., A or Option B" required />
        </div>

        <div class="form-group">
          <label>Explanation</label>
          <textarea v-model="form.explanation" rows="3" placeholder="Explain why this is correct"></textarea>
        </div>

        <div class="form-actions">
          <button type="button" @click="showForm = false" class="btn btn-secondary">Cancel</button>
          <button type="submit" class="btn btn-primary">{{ editingId ? 'Update' : 'Create' }}</button>
        </div>
      </form>
    </div>

    <div class="filters">
      <select v-model="filterLevel" class="filter-select">
        <option value="">All Levels</option>
        <option value="1">Level 1-1</option>
        <option value="2">Level 1-2</option>
        <option value="3">Level 2-1</option>
        <option value="4">Level 2-2</option>
      </select>

      <select v-model="filterType" class="filter-select">
        <option value="">All Types</option>
        <option value="multiple_choice">Multiple Choice</option>
        <option value="true_false">True/False</option>
        <option value="fill_blank">Fill in the Blank</option>
      </select>
    </div>

    <div class="questions-list">
      <h2>Questions ({{ filteredQuestions.length }})</h2>
      <div class="questions-grid">
        <div v-for="question in filteredQuestions" :key="question.id" class="question-card">
          <div class="card-header">
            <span class="level-badge">{{ getLevelName(question.level_id) }}</span>
            <span class="type-badge">{{ formatType(question.question_type) }}</span>
          </div>

          <p class="question-text">{{ question.question_text }}</p>

          <div class="card-footer">
            <span class="answer-count">{{ question.attempts }} attempts</span>
            <div class="actions">
              <button @click="editQuestion(question)" class="btn-icon">&#9998;</button>
              <button @click="deleteQuestion(question.id)" class="btn-icon delete">&#10005;</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminGameQuestions',
  data() {
    return {
      questions: [
        {
          id: 1,
          level_id: '1',
          question_text: 'What is the correct form of the verb in this sentence: "He _____ to school every day."',
          question_type: 'multiple_choice',
          options: ['A) goes', 'B) go', 'C) going', 'D) gone'],
          correct_answer: 'A',
          explanation: 'Third person singular requires "goes"',
          attempts: 145
        },
        {
          id: 2,
          level_id: '1',
          question_text: 'Is the following sentence correct? "She have a cat."',
          question_type: 'true_false',
          options: ['True', 'False'],
          correct_answer: 'False',
          explanation: 'Should be "She has a cat."',
          attempts: 98
        },
        {
          id: 3,
          level_id: '2',
          question_text: 'Complete the sentence: "Yesterday, I _____ to the store."',
          question_type: 'fill_blank',
          options: [],
          correct_answer: 'went',
          explanation: 'Past tense of "go"',
          attempts: 234
        }
      ],
      form: {
        level_id: '',
        question_text: '',
        question_type: 'multiple_choice',
        options: '',
        correct_answer: '',
        explanation: ''
      },
      showForm: false,
      editingId: null,
      filterLevel: '',
      filterType: ''
    }
  },
  computed: {
    filteredQuestions() {
      return this.questions.filter(q => {
        if (this.filterLevel && q.level_id !== this.filterLevel) return false
        if (this.filterType && q.question_type !== this.filterType) return false
        return true
      })
    }
  },
  methods: {
    saveQuestion() {
      if (this.editingId) {
        const idx = this.questions.findIndex(q => q.id === this.editingId)
        if (idx >= 0) {
          this.questions[idx] = { ...this.form, id: this.editingId }
        }
      } else {
        this.questions.push({
          ...this.form,
          id: Math.max(...this.questions.map(q => q.id), 0) + 1,
          attempts: 0
        })
      }
      this.resetForm()
    },
    editQuestion(question) {
      this.form = { ...question }
      this.editingId = question.id
      this.showForm = true
    },
    deleteQuestion(id) {
      if (confirm('Delete this question?')) {
        this.questions = this.questions.filter(q => q.id !== id)
      }
    },
    resetForm() {
      this.form = {
        level_id: '',
        question_text: '',
        question_type: 'multiple_choice',
        options: '',
        correct_answer: '',
        explanation: ''
      }
      this.editingId = null
      this.showForm = false
    },
    formatType(type) {
      const types = {
        'multiple_choice': 'Multiple Choice',
        'true_false': 'True/False',
        'fill_blank': 'Fill in Blank',
        'matching': 'Matching',
        'ordering': 'Ordering'
      }
      return types[type] || type
    },
    getLevelName(levelId) {
      const levels = { '1': 'Level 1-1', '2': 'Level 1-2', '3': 'Level 2-1', '4': 'Level 2-2' }
      return levels[levelId] || 'Unknown'
    }
  }
}
</script>

<style scoped lang="scss">
.admin-game-questions {
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
      max-width: 700px;
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

  .filters {
    display: flex;
    gap: 15px;
    margin-bottom: 30px;
    background: white;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

    .filter-select {
      padding: 8px 12px;
      border: 1px solid #ddd;
      border-radius: 6px;
      font-family: inherit;
      cursor: pointer;

      &:focus {
        outline: none;
        border-color: #667eea;
      }
    }
  }

  .questions-list {
    background: white;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .questions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
  }

  .question-card {
    border: 1px solid #ddd;
    border-radius: 12px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 15px;
    transition: all 0.2s;

    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      transform: translateY(-2px);
    }

    .card-header {
      display: flex;
      gap: 8px;
    }

    .level-badge,
    .type-badge {
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
    }

    .level-badge {
      background: rgba(102, 126, 234, 0.2);
      color: #667eea;
    }

    .type-badge {
      background: rgba(255, 152, 0, 0.2);
      color: #ff9800;
    }

    .question-text {
      margin: 0;
      color: #333;
      font-size: 14px;
      line-height: 1.5;
      flex: 1;
    }

    .card-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 10px;
      border-top: 1px solid #eee;

      .answer-count {
        font-size: 12px;
        color: #999;
      }

      .actions {
        display: flex;
        gap: 5px;
      }
    }

    .btn-icon {
      background: none;
      border: none;
      cursor: pointer;
      font-size: 16px;
      padding: 4px 8px;
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
