import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior: () => ({ top: 0 }),
  routes: [
    // ── Public ──
    { path: '/',          name: 'Home',     component: () => import('@/views/HomePage.vue') },
    { path: '/courses',   name: 'Courses',  component: () => import('@/views/courses/CoursesPage.vue') },
    { path: '/courses/:slug', name: 'CourseDetail', component: () => import('@/views/courses/CourseDetailPage.vue') },
    { path: '/pricing',   name: 'Pricing',  component: () => import('@/views/PricingPage.vue') },
    { path: '/verify/:code', name: 'VerifyCert', component: () => import('@/views/features/MicroCertPage.vue') },

    // ── Auth ──
    { path: '/login',     name: 'Login',    component: () => import('@/views/auth/LoginPage.vue'),    meta: { guest: true } },
    { path: '/register',  name: 'Register', component: () => import('@/views/auth/RegisterPage.vue'), meta: { guest: true } },

    // ── User (auth required) ──
    { path: '/dashboard',         name: 'Dashboard',      component: () => import('@/views/user/DashboardPage.vue'),    meta: { auth: true } },
    { path: '/profile',           name: 'Profile',        component: () => import('@/views/user/ProfilePage.vue'),      meta: { auth: true } },
    { path: '/my-courses',        name: 'MyCourses',      component: () => import('@/views/user/MyCoursesPage.vue'),    meta: { auth: true } },
    { path: '/learn/:slug/:id',   name: 'Lesson',         component: () => import('@/views/courses/LessonPage.vue'),    meta: { auth: true } },
    { path: '/amy',               name: 'Amy',            component: () => import('@/views/amy/AiTutorPage.vue'),       meta: { auth: true } },
    { path: '/quiz',              name: 'Quiz',           component: () => import('@/views/quiz/QuizPage.vue'),         meta: { auth: true } },
    { path: '/quiz/:id',          name: 'QuizTake',       component: () => import('@/views/quiz/QuizTakePage.vue'),     meta: { auth: true } },
    { path: '/leaderboard',       name: 'Leaderboard',    component: () => import('@/views/user/LeaderboardPage.vue'),  meta: { auth: true } },
    { path: '/certificates',      name: 'Certificates',   component: () => import('@/views/user/CertificatesPage.vue'),meta: { auth: true } },
    { path: '/payments',          name: 'Payments',       component: () => import('@/views/user/PaymentsPage.vue'),     meta: { auth: true } },
    { path: '/notifications',     name: 'Notifications',  component: () => import('@/views/user/NotificationsPage.vue'),meta: { auth: true } },

    // ── New Features (auth required) ──
    { path: '/learning-path',     name: 'LearningPath',   component: () => import('@/views/features/LearningPathPage.vue'),    meta: { auth: true } },
    { path: '/placement-test',    name: 'PlacementTest',  component: () => import('@/views/features/PlacementTestPage.vue'),   meta: { auth: true } },
    { path: '/mini-games',        name: 'MiniGames',      component: () => import('@/views/features/MiniGamesPage.vue'),       meta: { auth: true } },
    { path: '/fluency',           name: 'Fluency',        component: () => import('@/views/features/FluencyPage.vue'),         meta: { auth: true } },
    { path: '/pronunciation',     name: 'Pronunciation',  component: () => import('@/views/features/PronunciationPage.vue'),   meta: { auth: true } },
    { path: '/essay-checker',     name: 'EssayChecker',   component: () => import('@/views/features/EssayCheckerPage.vue'),    meta: { auth: true } },
    { path: '/vocabulary',        name: 'Vocabulary',     component: () => import('@/views/features/VocabSpacedPage.vue'),     meta: { auth: true } },
    { path: '/daily-challenge',   name: 'DailyChallenge', component: () => import('@/views/features/DailyChallengePage.vue'),  meta: { auth: true } },
    { path: '/tournament',        name: 'Tournament',     component: () => import('@/views/features/TournamentPage.vue'),      meta: { auth: true } },
    { path: '/learning-style',    name: 'LearningStyle',  component: () => import('@/views/features/LearningStylePage.vue'),  meta: { auth: true } },
    { path: '/news-learning',     name: 'NewsLearning',   component: () => import('@/views/features/NewsLearningPage.vue'),    meta: { auth: true } },
    { path: '/song-learning',     name: 'SongLearning',   component: () => import('@/views/features/SongLearningPage.vue'),    meta: { auth: true } },
    { path: '/sleep-learning',    name: 'SleepLearning',  component: () => import('@/views/features/SleepLearningPage.vue'),  meta: { auth: true } },
    { path: '/reminders',         name: 'Reminders',      component: () => import('@/views/features/RemindersPage.vue'),      meta: { auth: true } },
    { path: '/cultural',          name: 'Cultural',       component: () => import('@/views/features/CulturalContextPage.vue'),meta: { auth: true } },
    { path: '/industry-english',  name: 'IndustryEnglish',component: () => import('@/views/features/IndustryEnglishPage.vue'),meta: { auth: true } },
    { path: '/amy-memory',        name: 'AmyMemory',      component: () => import('@/views/features/AmyMemoryPage.vue'),      meta: { auth: true } },
    { path: '/micro-certs',       name: 'MicroCerts',     component: () => import('@/views/features/MicroCertPage.vue'),      meta: { auth: true } },
    { path: '/mistake-journal',   name: 'MistakeJournal', component: () => import('@/views/features/MistakeJournalPage.vue'), meta: { auth: true } },
    { path: '/goals',             name: 'Goals',          component: () => import('@/views/features/GoalTrackingPage.vue'),   meta: { auth: true } },
    { path: '/coding-interview',  name: 'CodingInterview',component: () => import('@/views/features/CodingInterviewPage.vue'),meta: { auth: true } },
    { path: '/accent-training',   name: 'AccentTraining', component: () => import('@/views/features/AccentTrainingPage.vue'), meta: { auth: true } },

    // ── Game Learning System (auth required) ──
    { path: '/game',                    name: 'GameHome',      component: () => import('@/views/GameHomePage.vue'),        meta: { auth: true } },
    { path: '/game/subject/:subjectId', name: 'SubjectView',   component: () => import('@/views/SubjectTopicsPage.vue'),   meta: { auth: true } },
    { path: '/game/topic/:topicId',     name: 'LevelMap',      component: () => import('@/views/LevelMapPage.vue'),        meta: { auth: true } },
    { path: '/game/play/:levelId',      name: 'PlayLevel',     component: () => import('@/views/LevelGamePage.vue'),       meta: { auth: true } },
    { path: '/game/leaderboard',        name: 'GameLB',        component: () => import('@/views/features/LeaderboardPage.vue'), meta: { auth: true } },
    { path: '/game/weak-areas',         name: 'WeakAreas',     component: () => import('@/views/WeakAreasPage.vue'),       meta: { auth: true } },
    { path: '/game/results/:attemptId', name: 'GameResults',   component: () => import('@/views/GameResultsPage.vue'),    meta: { auth: true } },

    // ── Admin ──
    { path: '/admin',                    name: 'AdminDash',        component: () => import('@/views/admin/AdminDashboard.vue'),    meta: { admin: true } },
    { path: '/admin/users',              name: 'AdminUsers',       component: () => import('@/views/admin/AdminUsers.vue'),        meta: { admin: true } },
    { path: '/admin/courses',            name: 'AdminCourses',     component: () => import('@/views/admin/AdminCourses.vue'),      meta: { admin: true } },
    { path: '/admin/courses/create',     name: 'AdminCourseCreate',component: () => import('@/views/admin/AdminCourseForm.vue'),   meta: { admin: true } },
    { path: '/admin/courses/:id/edit',   name: 'AdminCourseEdit',  component: () => import('@/views/admin/AdminCourseForm.vue'),   meta: { admin: true } },
    { path: '/admin/courses/:id/lessons',name: 'AdminLessons',     component: () => import('@/views/admin/AdminLessons.vue'),      meta: { admin: true } },
    { path: '/admin/categories',         name: 'AdminCategories',  component: () => import('@/views/admin/AdminCategories.vue'),   meta: { admin: true } },
    { path: '/admin/payments',           name: 'AdminPayments',    component: () => import('@/views/admin/AdminPayments.vue'),     meta: { admin: true } },
    { path: '/admin/coupons',            name: 'AdminCoupons',     component: () => import('@/views/admin/AdminCoupons.vue'),      meta: { admin: true } },
    { path: '/admin/badges',             name: 'AdminBadges',      component: () => import('@/views/admin/AdminBadges.vue'),       meta: { admin: true } },

    // ── Admin - Game System ──
    { path: '/admin/game',              name: 'AdminGameDash',    component: () => import('@/views/admin/AdminGameDashboard.vue'), meta: { admin: true } },
    { path: '/admin/game/subjects',     name: 'AdminGameSubjects',component: () => import('@/views/admin/AdminGameSubjects.vue'),  meta: { admin: true } },
    { path: '/admin/game/topics',       name: 'AdminGameTopics',  component: () => import('@/views/admin/AdminGameTopics.vue'),    meta: { admin: true } },
    { path: '/admin/game/levels',       name: 'AdminGameLevels',  component: () => import('@/views/admin/AdminGameLevels.vue'),    meta: { admin: true } },
    { path: '/admin/game/questions',    name: 'AdminGameQuestions',component:() => import('@/views/admin/AdminGameQuestions.vue'), meta: { admin: true } },

    // ── 404 ──
    { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('@/views/NotFoundPage.vue') },
  ]
})

router.beforeEach((to, from, next) => {
  const token    = localStorage.getItem('amy_token')
  const userStr  = localStorage.getItem('amy_user')
  const loggedIn = !!(token && userStr)
  let parsedUser = null
  try { parsedUser = JSON.parse(userStr) } catch {}
  const role     = parsedUser?.role ?? null
  const isAdmin  = ['admin', 'superadmin'].includes(role)

  if (to.meta.auth  && !loggedIn) return next('/login')
  if (to.meta.admin && !isAdmin)  return next(loggedIn ? '/dashboard' : '/login')
  if (to.meta.guest && loggedIn)  return next(isAdmin ? '/admin' : '/dashboard')
  next()
})

export default router
