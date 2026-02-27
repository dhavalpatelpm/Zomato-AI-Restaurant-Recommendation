# Deploy on Streamlit Cloud

Deploy the Zomato AI Restaurant Recommender as a Streamlit app.

## Prerequisites

- GitHub account
- [Streamlit Community Cloud](https://share.streamlit.io/) account
- **GROQ API Key** (for LLM recommendations)

## Deployment Steps

1. **Push your code to GitHub** (if not already done)

2. **Go to [share.streamlit.io](https://share.streamlit.io/)** and sign in with GitHub

3. **Click "New app"** and select your repository

4. **Configure the app:**
   - **Repository:** `your-username/Zomato-AI-Restaurant-Recommendation`
   - **Branch:** `main`
   - **Main file path:** `ai-restaurant-recommender/streamlit_app.py`
   - **Advanced settings:**
     - **Working directory:** `ai-restaurant-recommender`
     - **Python version:** 3.9 or higher
     - **Requirements file:** `ai-restaurant-recommender/requirements-streamlit.txt` (or leave default if it detects it)

5. **Add secrets** (click "Advanced settings" → "Secrets"):
   ```toml
   GROQ_API_KEY = "your-groq-api-key-here"
   ```

6. **Click "Deploy"** — the app will build and launch (first run may take a few minutes to load the dataset)

## Local Run

```bash
cd ai-restaurant-recommender
pip install -r requirements-streamlit.txt
export GROQ_API_KEY=your-key-here
streamlit run streamlit_app.py
```

## Notes

- First load fetches and processes the Zomato dataset; subsequent requests are faster.
- The app uses the same backend logic as the FastAPI/React version (filtering, LLM, ranking).
- If the LLM fails, the app falls back to rule-based recommendations.
