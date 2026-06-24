# Amy Frontend — Install Guide

## Requirements
- Node.js 18+
- npm or yarn
- Backend running on port 8000

## Setup

```bash
# 1. Go to frontend folder
cd amy_frontend

# 2. Install dependencies
npm install

# 3. Run development server
npm run dev
```

Frontend runs at: http://localhost:5173

## Build for production

```bash
npm run build
# Output in: dist/
```

## Important

Make sure backend is running first:
- Backend: http://localhost:8000
- Frontend proxy is configured in vite.config.js

## Default Admin Login

Email: admin@amy.com
Password: admin123
(Change in backend .env)
