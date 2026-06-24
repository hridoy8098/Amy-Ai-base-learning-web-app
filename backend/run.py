"""
Amy Learning Platform — Backend Runner
=======================================
Double-click করো অথবা terminal-এ: python run.py
"""

import os
import sys
import subprocess

# ── Path fix ──────────────────────────────────────────────────────
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)
os.chdir(_BASE_DIR)

for stream_name in ("stdout", "stderr"):
    stream = getattr(sys, stream_name, None)
    if stream and hasattr(stream, "reconfigure"):
        stream.reconfigure(errors="replace")

# ── Color helpers ──────────────────────────────────────────────────
def green(t):  return f"\033[92m{t}\033[0m"
def yellow(t): return f"\033[93m{t}\033[0m"
def red(t):    return f"\033[91m{t}\033[0m"
def cyan(t):   return f"\033[96m{t}\033[0m"
def bold(t):   return f"\033[1m{t}\033[0m"

def banner():
    print(cyan("""
  ╔══════════════════════════════════════════╗
  ║   🤖  Amy Learning Platform  v3.0       ║
  ║   AI-Powered English Learning Backend    ║
  ╚══════════════════════════════════════════╝
"""))

def check_env():
    if not os.path.exists(".env"):
        print(yellow("⚠️  .env file পাওয়া যায়নি! .env.example থেকে copy করা হচ্ছে..."))
        if os.path.exists(".env.example"):
            import shutil
            shutil.copy(".env.example", ".env")
            print(green("✅ .env file তৈরি হয়েছে। DB password ও API keys দিন।"))
        else:
            print(red("❌ .env.example ও নেই! .env file manually তৈরি করুন।"))
            sys.exit(1)
    else:
        print(green("✅ .env file পাওয়া গেছে"))

def check_dependencies():
    print(yellow("\n📦 Dependencies check করা হচ্ছে..."))
    required = ["fastapi", "uvicorn", "sqlalchemy", "pymysql", "python-jose", "passlib", "python-dotenv", "openai", "python-multipart"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg.replace("-", "_").split("[")[0])
        except ImportError:
            missing.append(pkg)

    if missing:
        print(yellow(f"⚠️  Missing packages: {', '.join(missing)}"))
        print(yellow("📥 Install করা হচ্ছে..."))
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print(green("✅ সব packages install হয়েছে"))
    else:
        print(green("✅ সব dependencies আছে"))

def check_database():
    print(yellow("\n🗄️  Database connection check করা হচ্ছে..."))
    try:
        from dotenv import load_dotenv
        load_dotenv()
        import pymysql
        conn = pymysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "amy_learning"),
            connect_timeout=5,
        )
        conn.close()
        print(green("✅ MySQL connected successfully"))
    except Exception as e:
        err = str(e)
        if "Unknown database" in err:
            print(yellow(f"⚠️  Database নেই — তৈরি করা হচ্ছে..."))
            _create_database()
        elif "Access denied" in err:
            print(red(f"❌ MySQL Access Denied! .env-এ DB_USER ও DB_PASSWORD ঠিক করুন"))
            print(red(f"   Error: {err}"))
            sys.exit(1)
        elif "Can't connect" in err or "Connection refused" in err:
            print(red("❌ MySQL চালু নেই! XAMPP-এ MySQL Start করুন।"))
            input(yellow("XAMPP-এ MySQL start করে Enter চাপুন..."))
            check_database()
        else:
            print(red(f"❌ DB Error: {err}"))
            sys.exit(1)

def _create_database():
    try:
        from dotenv import load_dotenv
        load_dotenv()
        import pymysql
        conn = pymysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            connect_timeout=5,
        )
        db_name = os.getenv("DB_NAME", "amy_learning")
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
        conn.close()
        print(green(f"✅ Database '{db_name}' তৈরি হয়েছে"))
    except Exception as e:
        print(red(f"❌ Database তৈরি করা যায়নি: {e}"))
        sys.exit(1)

def print_info():
    from dotenv import load_dotenv
    load_dotenv()
    host    = os.getenv("HOST", "0.0.0.0")
    port    = int(os.getenv("PORT", 8000))
    reload  = os.getenv("DEV_MODE", "true").lower() == "true"
    frontend = os.getenv("FRONTEND_URL", "http://localhost:5173")

    print(bold(cyan("\n🚀 Server শুরু হচ্ছে...\n")))
    print(f"  {green('➜')} Local:    {cyan(f'http://localhost:{port}')}")
    print(f"  {green('➜')} API Docs: {cyan(f'http://localhost:{port}/docs')}")
    print(f"  {green('➜')} Frontend: {cyan(frontend)}")
    print(f"  {green('➜')} Reload:   {green('ON') if reload else yellow('OFF')}")
    print(f"\n  {yellow('Stop করতে: Ctrl + C')}\n")

def run():
    banner()
    check_env()
    check_dependencies()
    check_database()
    print_info()

    from dotenv import load_dotenv
    load_dotenv()
    host   = os.getenv("HOST", "0.0.0.0")
    port   = int(os.getenv("PORT", 8000))
    reload = os.getenv("DEV_MODE", "true").lower() == "true"

    import uvicorn
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        reload_dirs=[_BASE_DIR],
        log_level="info",
    )

if __name__ == "__main__":
    run()
