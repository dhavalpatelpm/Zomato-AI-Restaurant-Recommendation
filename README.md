# Zomato AI Restaurant Recommendation

## Quick Start

In Cursor, simply say **"Run the project"** to start, or **"Stop the project"** to stop.

Or run manually:

```bash
npm start    # start backend + frontend
npm run stop # stop both
```

The start script will:
1. Start the backend API (port 8000)
2. Wait until it's ready
3. Start the frontend (http://localhost:5173)

Ensure you have:
- Node.js and npm (for frontend)
- Python 3 with venv (for backend)
- `ai-restaurant-recommender/.env` with `GROQ_API_KEY`
- `cd ai-restaurant-recommender && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt` (first-time setup)
- `cd frontend && npm install` (first-time setup)

## Manual Start

If you prefer to run services separately:

1. **Backend:**
   ```bash
   cd ai-restaurant-recommender && source .venv/bin/activate
   PYTHONPATH=. python -m uvicorn src.phase3_api_service.app:app --reload --port 8000
   ```

2. **Frontend** (in a new terminal):
   ```bash
   cd frontend && npm run dev
   ```

The frontend will auto-retry loading localities and cuisines if the backend isn't ready yet.
