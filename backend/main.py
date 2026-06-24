from importlib import import_module
from pathlib import Path
import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.config import FRONTEND_URL, UPLOAD_DIR
from core.database import Base, engine
from models.game_models import *  # Import all game models

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


def configure_stdio():
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream and hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")


def log(message):
    print(message)


configure_stdio()

for subdir in ("avatars", "thumbnails", "videos", "docs", "certificates"):
    os.makedirs(Path(UPLOAD_DIR) / subdir, exist_ok=True)

try:
    Base.metadata.create_all(bind=engine)
    log("Database tables ready")
except Exception as exc:
    log(f"DB error: {exc}")

app = FastAPI(title="Amy Learning Platform API", version="3.0.0")

allowed_origins = sorted({
    FRONTEND_URL.rstrip("/"),
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
})

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/")
def root():
    return {"message": "Backend Running"}


@app.get("/health")
def health():
    return {"status": "ok"}


def safe_include(module_name, prefixes, tag):
    try:
        module = import_module(f"routers.{module_name}")
        for prefix in prefixes:
            app.include_router(module.router, prefix=prefix, tags=[tag])
        log(f"{module_name} loaded")
    except Exception as exc:
        log(f"{module_name} error: {exc}")


ROUTERS = [
    ("auth", ["/api/auth"], "Auth"),
    ("users", ["/api/users"], "Users"),
    ("courses", ["/api/courses"], "Courses"),
    ("lessons", ["/api/lessons"], "Lessons"),
    ("amy", ["/api/amy"], "AI"),
    ("amy_memory", ["/api/amy_memory", "/api/amy-memory"], "AI Memory"),
    ("accent_training", ["/api/accent_training", "/api/accent-training", "/api/accent"], "Accent Training"),
    ("admin", ["/api/admin"], "Admin"),
    ("categories", ["/api/categories"], "Categories"),
    ("coding_interview", ["/api/coding_interview", "/api/coding-interview"], "Coding Interview"),
    ("cultural_context", ["/api/cultural_context", "/api/cultural"], "Cultural Context"),
    ("daily_challenge", ["/api/daily_challenge", "/api/daily-challenge"], "Daily Challenge"),
    ("essay_checker", ["/api/essay_checker", "/api/essay"], "Essay Checker"),
    ("fluency", ["/api/fluency"], "Fluency"),
    ("goal_tracking", ["/api/goal_tracking", "/api/goals"], "Goal Tracking"),
    ("industry_english", ["/api/industry_english", "/api/industry"], "Industry English"),
    ("micro_cert", ["/api/micro_cert", "/api/micro-cert"], "Micro Certificate"),
    ("mini_games", ["/api/mini_games", "/api/mini-games"], "Mini Games"),
    ("mistake_journal", ["/api/mistake_journal", "/api/mistakes"], "Mistake Journal"),
    ("news_learning", ["/api/news_learning", "/api/news-learning"], "News Learning"),
    ("payments", ["/api/payments"], "Payments"),
    ("placement_test", ["/api/placement_test", "/api/placement"], "Placement Test"),
    ("pronunciation", ["/api/pronunciation"], "Pronunciation"),
    ("quiz", ["/api/quiz"], "Quiz"),
    ("reminders", ["/api/reminders"], "Reminders"),
    ("sleep_learning", ["/api/sleep_learning", "/api/sleep-learning"], "Sleep Learning"),
    ("song_learning", ["/api/song_learning", "/api/song-learning"], "Song Learning"),
    ("learning_path", ["/api/learning_path", "/api/learning-path"], "Learning Path"),
    ("learning_style", ["/api/learning_style", "/api/learning-style"], "Learning Style"),
    ("tournament", ["/api/tournament"], "Tournament"),
    ("uploads", ["/api/uploads", "/api/upload"], "Uploads"),
    ("vocab_spaced", ["/api/vocab_spaced", "/api/vocab-spaced"], "Vocabulary Trainer"),
    ("game_admin", ["/api/admin/game"], "Game Admin"),
    ("game_user", ["/api/game"], "Game Player"),
]

for module_name, prefixes, tag in ROUTERS:
    safe_include(module_name, prefixes, tag)


@app.on_event("startup")
async def startup():
    log("Server started")
