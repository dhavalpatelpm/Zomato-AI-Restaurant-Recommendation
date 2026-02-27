# Zomato AI Restaurant Recommendation

An AI-powered restaurant recommendation service for Bangalore city. The system ingests restaurant data from Hugging Face, applies structured filtering based on user preferences, and leverages **GROQ LLM** to generate ranked, contextual recommendations.

---

## Features

- **Smart filtering** by locality, price range, cuisines, and minimum rating
- **LLM-powered explanations** for each recommendation
- **92 localities** and **106 cuisines** from curated Zomato dataset
- React frontend + FastAPI backend
- Auto-retry for localities/cuisines loading
- Responsive design with dark theme

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/dhavalpatelpm/Zomato-AI-Restaurant-Recommendation.git
cd Zomato-AI-Restaurant-Recommendation

# One-command start (backend + frontend)
npm start

# Stop
npm run stop
```

Open **http://localhost:5173** in your browser.

---

## Prerequisites

- **Node.js** and npm (for frontend)
- **Python 3** with venv (for backend)
- **GROQ API key** ([get one here](https://console.groq.com/))

---

## Setup

### 1. Backend

```bash
cd ai-restaurant-recommender
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env`:

```
GROQ_API_KEY=your_groq_api_key_here
```

### 2. Frontend

```bash
cd frontend
npm install
```

### 3. Run

From project root:

```bash
npm start    # Starts backend, waits for it, then frontend
npm run stop # Stops both
```

Or manually:

```bash
# Terminal 1 - Backend
cd ai-restaurant-recommender && source .venv/bin/activate
PYTHONPATH=. python -m uvicorn src.phase3_api_service.app:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend && npm run dev
```

---

## Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  FRONTEND (React + Vite)                                         │
│  Select Locality | Price Range | Cuisines | Min Rating           │
│  → Get Recommendations                                           │
└─────────────────────────────────────┬───────────────────────────┘
                                      │ HTTP POST /api/recommend
                                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  API LAYER (FastAPI)                                             │
│  Request validation → Structured filtering → LLM call            │
└─────────────────────────────────────┬───────────────────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────┐
│  Phase 1        │    │  Phase 3             │    │  Phase 4        │
│  Data           │    │  Filtering           │    │  GROQ LLM       │
│  Acquisition    │ →  │  (locality, price,   │ →  │  Ranked recs +  │
│  (HuggingFace)  │    │   cuisines, rating)  │    │  explanations   │
└─────────────────┘    └──────────────────────┘    └─────────────────┘
```

### Phases

| Phase | Description |
|-------|-------------|
| **1. Data Acquisition** | Ingests from [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation) (Hugging Face) |
| **2. Data Processing** | Cleaning, normalization, feature engineering, deduplication |
| **3. API & Filtering** | FastAPI service; filters by locality, price, cuisines, min rating |
| **4. LLM Engine** | GROQ API for ranked recommendations with explanations |
| **5. Response Layer** | Schema validation, formatting, ranking |
| **6. Frontend** | React UI with form, loading states, error handling |
| **7. Infrastructure** | Docker, docker-compose for deployment |
| **8. Observability** | Logging, metrics, health checks |

### Tech Stack

- **Frontend:** React 18, Vite, Axios
- **Backend:** FastAPI, Uvicorn
- **LLM:** GROQ API
- **Data:** Hugging Face Datasets, Pandas
- **Infrastructure:** Docker, docker-compose

---

## Project Structure

```
├── ai-restaurant-recommender/    # Backend
│   ├── streamlit_app.py          # Streamlit UI for deployment
│   ├── requirements-streamlit.txt
│   ├── src/
│   │   ├── phase1_data_acquisition/
│   │   ├── phase2_data_processing/
│   │   ├── phase3_api_service/
│   │   ├── phase4_llm_engine/
│   │   └── phase5_response_layer/
│   ├── observability/
│   └── requirements.txt
├── frontend/                     # React app
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── App.jsx
│   └── package.json
├── infrastructure/               # Docker, deployment
├── docs/
│   └── ARCHITECTURE.md           # Full architecture document
├── start.sh
├── stop.sh
└── package.json
```

---

## API

- `GET /api/localities` — List localities
- `GET /api/cuisines` — List cuisines
- `POST /api/recommend` — Get recommendations

**Request body:**

```json
{
  "locality": "koramangala",
  "price_range": 1500,
  "min_rating": 4.5,
  "cuisines": ["North Indian", "Chinese"]
}
```

---

## Deployment (Render)

**Recommended:** Deploy to Render with one click.

1. Connect your repo at [dashboard.render.com](https://dashboard.render.com) → **New +** → **Blueprint**
2. Add **GROQ_API_KEY** to the `zomato-api` service
3. After backend deploys, add **VITE_API_URL** (your backend URL) to `zomato-frontend`
4. Redeploy frontend

See **[docs/RENDER_DEPLOY.md](docs/RENDER_DEPLOY.md)** for the full step-by-step guide.

**Other options:** Railway, Fly.io, Vercel + Render, Docker.

---

## Streamlit Deployment

Deploy as a standalone Streamlit app on [Streamlit Community Cloud](https://share.streamlit.io/):

```bash
cd ai-restaurant-recommender
pip install -r requirements-streamlit.txt
export GROQ_API_KEY=your-key
streamlit run streamlit_app.py
```

See **[docs/STREAMLIT_DEPLOY.md](docs/STREAMLIT_DEPLOY.md)** for full Streamlit Cloud deployment steps.

---

## License

MIT

---

**Made with ❤️ by Dhaval Patel** · Powered by GROQ AI
