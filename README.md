# Amy Ai — English Learning Web App

A comprehensive, AI-powered English learning platform built with **FastAPI** (backend) and **Vue.js 3** (frontend). Designed to help learners improve speaking, writing, listening, reading, vocabulary, and grammar through interactive features, gamification, and personalized AI tutoring.

---

## Features

### 🧠 AI Tutor (Amy)
- Conversational AI English tutor with voice support
- Context-aware memory for personalized learning
- Daily free & voice message limits per subscription plan

### 🎓 Courses & Lessons
- Structured course management with lessons
- Admin panel for creating/editing courses and lessons
- Rich text editor (Tiptap) for content creation

### 🎮 Gamification & Games
- Mini-games, level-based games, and tournaments
- Subject/topic/level progression system
- Leaderboards, badges, and rewards
- Daily challenges

### 🗣️ Speaking & Pronunciation
- Accent training modules
- Pronunciation practice with feedback
- Fluency assessment

### 📝 Writing & Grammar
- Essay checker with AI feedback
- Mistake journal to track and review errors
- Industry English for professional writing

### 📖 Vocabulary
- Spaced repetition vocabulary trainer (VocabSpaced)
- Song-based learning
- News-based learning

### 🧪 Assessment & Progress
- Placement test for level assessment
- Quiz system with daily/weekly/monthly limits per plan
- Learning path and learning style detection
- Goal tracking
- Micro-certificates on completion

### 💳 Subscription & Payments
- Multiple plans: Free, Basic, Pro, Premium
- Quiz limits and Amy usage limits per tier
- Coupon support

### 🛠️ Admin Panel
- Dashboard with analytics
- Manage users, courses, lessons, categories
- Game configuration (subjects, topics, levels, questions)
- Coupons and payment management

---

## Tech Stack

### Backend
- **Framework:** FastAPI 0.115
- **Server:** Uvicorn 0.30
- **ORM:** SQLAlchemy 2.0
- **Database:** MySQL (PyMySQL)
- **Auth:** JWT (python-jose), bcrypt/passlib
- **AI:** OpenAI API, HugChat
- **Other:** Pillow, python-multipart, aiofiles, python-dotenv

### Frontend
- **Framework:** Vue.js 3 (Composition API)
- **Build Tool:** Vite 5
- **State:** Pinia
- **Router:** Vue Router 4
- **HTTP Client:** Axios
- **Rich Text:** Tiptap (starter-kit, image, link, underline, placeholder, text-align)
- **Utilities:** VueUse, vue3-toastify, Sass

---

## Project Structure

```
AmyAi main/
├── backend/
│   ├── core/               # Config, database, security, AI providers
│   ├── models/             # SQLAlchemy models (db models + game models)
│   ├── routers/            # 36 API route modules
│   ├── uploads/            # User uploads (avatars, thumbnails, docs)
│   ├── main.py             # FastAPI app entry point
│   ├── run.py              # Server runner
│   ├── requirements.txt
│   └── .env                # Environment variables (not tracked)
├── frontend/
│   ├── src/
│   │   ├── api/            # API client (Axios)
│   │   ├── components/     # Reusable Vue components
│   │   ├── router/         # Vue Router config
│   │   ├── store/          # Pinia stores
│   │   ├── views/          # Page components
│   │   └── App.vue         # Root component
│   ├── dist/               # Production build output
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
└── .gitignore
```

---

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- MySQL

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate    # Windows
# source venv/bin/activate # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env   # or create .env manually
# Edit .env with your DB credentials, API keys, etc.

# Run the server
python run.py
# Server starts at http://localhost:8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
# App runs at http://localhost:5173

# Build for production
npm run build
```

---

## Environment Variables (`.env`)

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | Amy Learning | Application name |
| `FRONTEND_URL` | http://localhost:5173 | Frontend origin for CORS |
| `UPLOAD_DIR` | uploads | File upload directory |
| `MAX_UPLOAD_SIZE` | 52428800 | Max upload size (bytes, 50MB) |
| `ADMIN_EMAIL` | admin@amy.com | Default admin email |
| `ADMIN_PASSWORD` | admin123 | Default admin password |
| `OPENAI_API_KEY` | — | OpenAI API key |
| Database variables | — | MySQL connection settings |

---

## API Routes

The backend exposes **35+ API modules** under `/api/`:

- `/api/auth` — Authentication & registration
- `/api/users` — User profiles & management
- `/api/courses`, `/api/lessons` — Course & lesson content
- `/api/amy` — AI Tutor (Amy)
- `/api/quiz` — Quiz engine
- `/api/game` — Game player endpoints
- `/api/admin` — Admin dashboard & management
- `/api/admin/game` — Game configuration (admin)
- `/api/pronunciation`, `/api/accent` — Speaking tools
- `/api/essay` — Essay checker
- `/api/vocab-spaced` — Spaced repetition vocabulary
- Plus many more (placement test, daily challenge, tournaments, etc.)

---

## License

MIT
