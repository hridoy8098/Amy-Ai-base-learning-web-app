const STORAGE_KEY_PREFIX = 'amy_recent_quizzes'
const LEGACY_STORAGE_KEY = 'amy_recent_quizzes'

export function getTimerForDifficulty(difficulty) {
  return difficulty === 'advanced' ? 30 : 50
}

function getCurrentUserId() {
  try {
    const user = JSON.parse(localStorage.getItem('amy_user') || 'null')
    return user?.id ? String(user.id) : 'guest'
  } catch {
    return 'guest'
  }
}

function getStorageKey() {
  return `${STORAGE_KEY_PREFIX}:${getCurrentUserId()}`
}

function normalizeQuiz(entry) {
  if (!entry || !entry.id) return null

  return {
    id: entry.id,
    topic: entry.topic || 'Untitled Quiz',
    subject: entry.subject || '',
    difficulty: entry.difficulty || 'intermediate',
    language: entry.language || 'en',
    total_q: entry.total_q ?? entry.total ?? 0,
    correct: entry.correct ?? 0,
    score: entry.score ?? 0,
    xp_earned: entry.xp_earned ?? 0,
    time_per_question: entry.time_per_question ?? getTimerForDifficulty(entry.difficulty),
    created_at: entry.created_at || new Date().toISOString(),
    questions: Array.isArray(entry.questions) ? entry.questions : [],
    submitted_result: entry.submitted_result || null,
  }
}

function readScopedCache() {
  try {
    const parsed = JSON.parse(localStorage.getItem(getStorageKey()) || '[]')
    return parsed.map(normalizeQuiz).filter(Boolean)
  } catch {
    return []
  }
}

export function getRecentQuizCache() {
  return readScopedCache()
}

export function saveRecentQuizCache(quizzes) {
  const normalized = quizzes
    .map(normalizeQuiz)
    .filter(Boolean)
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 20)

  localStorage.removeItem(LEGACY_STORAGE_KEY)
  localStorage.setItem(getStorageKey(), JSON.stringify(normalized))
  return normalized
}

export function clearCurrentQuizCache() {
  localStorage.removeItem(getStorageKey())
  localStorage.removeItem(LEGACY_STORAGE_KEY)
}

export function upsertRecentQuiz(entry) {
  const normalized = normalizeQuiz(entry)
  if (!normalized) return getRecentQuizCache()

  const existing = getRecentQuizCache().filter(quiz => quiz.id !== normalized.id)
  return saveRecentQuizCache([normalized, ...existing])
}

export function mergeRecentQuizzes(apiHistory = []) {
  const merged = [...getRecentQuizCache()]

  for (const item of apiHistory) {
    const normalized = normalizeQuiz(item)
    if (!normalized) continue

    const index = merged.findIndex(quiz => quiz.id === normalized.id)
    if (index === -1) {
      merged.push(normalized)
      continue
    }

    merged[index] = {
      ...merged[index],
      ...normalized,
      submitted_result: merged[index].submitted_result || normalized.submitted_result || null,
    }
  }

  return saveRecentQuizCache(merged)
}
