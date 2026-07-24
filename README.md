# CodeCoach MVP

Full-stack scaffold: FastAPI + SQLAlchemy + SQLite backend, React + Vite +
Tailwind frontend, OpenAI-powered question generation and streaming code
review.

Runs locally with Python + Node — no Docker required.

## Folder structure

```
codecoach-mvp/
├── backend/app/
│   ├── core/          # config.py (env settings), security.py (auth/JWT)
│   ├── db/            # database.py (SQLAlchemy setup), models.py (User, Submission)
│   ├── routers/       # auth.py (register/login/profile), practice.py (questions/review)
│   ├── services/llm.py  # all OpenAI calls
│   └── main.py
├── frontend/src/components/
│   ├── CodeEditor.jsx, StreamPanel.jsx, Dashboard.jsx   # requested
│   ├── Navbar.jsx, Profile.jsx, Login.jsx, Register.jsx # needed to wire up
│   │                                                     # theme toggle, /profile, and auth
│   └── App.jsx, main.jsx
└── .env.example
```

Files beyond the exact list originally given: `Navbar.jsx` (holds the
theme toggle), `Profile.jsx` (the `/profile` page itself), `Login.jsx` /
`Register.jsx` (there's no functioning app without a way to create an
account), and `src/api.js` (fetch client shared by all components).

## First-time setup

### 1. Set your API key

```bash
cp .env.example .env
# edit .env and paste your real OPENAI_API_KEY
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env .env                 # pydantic-settings reads ./.env relative to where you run uvicorn
uvicorn app.main:app --reload
```
Backend runs at http://localhost:8000 (interactive docs at `/docs`).
SQLite file (`codecoach.db`) is created automatically on first run.

### 3. Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```
Frontend runs at http://localhost:5173.

### 4. Use it

- Go to http://localhost:5173, click **Register**, create an account.
- New accounts start at `skill_level = "beginner"` and
  `daily_question_count = 1`.
- Click **Get today's question** — for a beginner this will always be
  "Hello World" first, then step through variables → if/else → loops →
  arrays → functions before ever touching DSA (see `BEGINNER_PROGRESSION`
  in `backend/app/services/llm.py`).
- Paste/write code, hit **Submit for review** — the AI coach's response
  streams into the panel below word-by-word.
- Toggle dark/light mode from the navbar (persists via localStorage).
- Visit `/profile` to see username/email/streak/skill level and edit
  your username.

## Deploying

This has no Docker/deploy config baked in on purpose (kept minimal) — but
it's built to deploy cleanly to typical platforms:

**Backend** (Render, Railway, Fly.io, or similar):
- Point the platform at `backend/` as the root, `pip install -r requirements.txt`
  as the build command.
- `Procfile` is included: `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  — most platforms auto-detect this.
- Set environment variables on the platform: `OPENAI_API_KEY`, `SECRET_KEY`,
  `CORS_ORIGINS` (your deployed frontend's exact URL), and `DATABASE_URL`.
- **Switch `DATABASE_URL` to Postgres before deploying.** SQLite is a file
  on local disk — Render/Railway/Heroku/Fly all wipe local disk on every
  redeploy, so your users/submissions would vanish. Most of these
  platforms offer a one-click managed Postgres add-on; copy its connection
  string into `DATABASE_URL`. `psycopg2-binary` is already in
  `requirements.txt`, so no code changes are needed — SQLAlchemy handles
  the dialect switch automatically.

**Frontend** (Vercel, Netlify, or similar):
- Build command: `npm run build` → outputs static files to `frontend/dist`.
- Set `VITE_API_BASE` (see `frontend/.env.example`) to your deployed
  backend's URL before building — Vite bakes it in at build time, it's
  not read at runtime.
- Deploy the `dist` folder as a static site.

**After both are deployed:** set the backend's `CORS_ORIGINS` to the
frontend's real deployed URL (not `*`) — the app won't work cross-origin
otherwise.

## Known limitations / next steps

- **No test-case judge.** Correctness is assessed by the AI reading your
  code, not by executing it against hidden test cases. Good enough for an
  MVP; a real sandboxed runner would make "pass/fail" verdicts trustworthy.
- **Skill-level progression is a simple counter** (7 solved beginner
  submissions → bumped to "easy"). Tune `BEGINNER_GRADUATION_THRESHOLD` in
  `practice.py` as you get real usage data.
- **Leaderboard / Battle Mode / Friends list are not built.** The `users`
  table is the single source of truth for `username`, so those features
  can be added later by joining on `user_id` without migrating existing
  data.
- **CORS is wide open** (`allow_origins=["*"]`) for local dev — restrict
  this before deploying anywhere public.
- **SQLite** is fine for the MVP but is a single-file, single-writer
  database — move to Postgres before you have concurrent users; only
  `DATABASE_URL` in `.env` needs to change.
- This was generated in a sandboxed environment with no internet access,
  so it hasn't been run end-to-end. Python files passed `py_compile`
  syntax checks and the JSX passed a TypeScript-based parse check; please
  run it locally and report back anything that doesn't boot cleanly.
