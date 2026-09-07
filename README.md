# VideoLens

Paste a YouTube link, tell it what you're looking for, and find out if the video
actually covers it — before you spend time watching.

## Features
- Video metadata + transcript retrieval
- AI-generated summaries (overview, key points, topics, takeaways)
- Personalized relevance scoring against a stated goal
- RAG-powered chat grounded in the video's transcript, with timestamp jump-links
- Accounts, saved videos, and history via Clerk
- "Fill the gaps" — finds other videos covering what this one misses

## Stack
- **Frontend:** React, TypeScript, Vite, Tailwind CSS
- **Backend:** FastAPI, SQLAlchemy (async), Pydantic
- **AI:** Google Gemini (generation + embeddings)
- **Database:** PostgreSQL + pgvector
- **Auth:** Clerk

## Local setup

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env   # fill in your keys
npm run dev
```

### Database
```bash
docker run --name videolens-postgres \
  -e POSTGRES_USER=videolens \
  -e POSTGRES_PASSWORD=videolens \
  -e POSTGRES_DB=videolens \
  -p 5432:5432 \
  -d pgvector/pgvector:pg16
```

## Required API keys
- `YOUTUBE_API_KEY` — [Google Cloud Console](https://console.cloud.google.com)
- `GEMINI_API_KEY` — [Google AI Studio](https://aistudio.google.com/apikey)
- `CLERK_SECRET_KEY` / `VITE_CLERK_PUBLISHABLE_KEY` — [clerk.com](https://clerk.com)