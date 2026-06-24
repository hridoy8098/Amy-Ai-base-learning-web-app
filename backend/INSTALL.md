# Amy Backend v2 — Install Guide
## Groq (10 keys) + HuggingChat | No Ollama

---

## Step 1 — MySQL Database

1. XAMPP চালু করো → Apache + MySQL start
2. http://localhost/phpmyadmin
3. New → Database name: `amy_learning` → Create

---

## Step 2 — Groq API Keys নাও (Free)

1. console.groq.com → Sign up (Gmail দিয়ে)
2. API Keys → Create API Key → Copy
3. ১০টা Gmail দিয়ে ১০টা key বানাও

---

## Step 3 — Python Setup

```bash
cd backend

# Virtual environment
python -m venv venv
venv\Scripts\activate       # Windows

# Install
pip install -r requirements.txt
```

---

## Step 4 — .env Configure করো

```bash
copy .env.example .env
```

`.env` খুলে Groq keys দাও:
```
GROQ_API_KEY_1=gsk_xxxx   ← Gmail 1
GROQ_API_KEY_2=gsk_xxxx   ← Gmail 2
...
GROQ_API_KEY_10=gsk_xxxx  ← Gmail 10
```

---

## Step 5 — HuggingChat Cookie (Fallback)

1. hugchat.huggingface.co → Login
2. Browser DevTools → Application → Cookies
3. `hf-chat` cookie value copy করো
4. `backend/cookie.json` file বানাও:

```json
[{"name":"hf-chat","value":"your-cookie-value-here","domain":".huggingface.co","path":"/","secure":true,"httpOnly":true}]
```

---

## Step 6 — Run করো

```bash
venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

চালু হলে দেখবে:
```
✅ Database tables ready
✅ Admin created: admin@amy.com / admin123
✅ Default badges seeded
🤖 AI Providers: ['groq', 'hugchat'] (10 Groq keys loaded)
```

---

## URLs

| URL | Description |
|-----|-------------|
| http://localhost:8000 | API Root |
| http://localhost:8000/docs | Swagger UI (সব API) |
| http://localhost:8000/health | Health check |
| http://localhost:8000/api/amy/status | AI provider status |

---

## Admin Login

- Email: admin@amy.com
- Password: admin123

---

## Provider Chain

```
Request আসলে:
  1. Groq key 1 try → success হলে return
  2. Groq key 2 try (next rotation) ...
  3. কোনো Groq key fail করলে → HuggingChat
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| MySQL connection error | XAMPP-এ MySQL চালু আছে কিনা দেখো |
| No AI provider | .env-এ GROQ_API_KEY_1 দিয়েছ? |
| Groq 429 error | Rate limit — automatically next key-এ যাবে |
| HuggingChat error | cookie.json ঠিকমতো আছে কিনা দেখো |
