# Deploy to Render

Step-by-step guide to deploy Zomato AI Restaurant Recommendation on Render.

---

## Prerequisites

- GitHub repo: [https://github.com/dhavalpatelpm/Zomato-AI-Restaurant-Recommendation](https://github.com/dhavalpatelpm/Zomato-AI-Restaurant-Recommendation)
- [GROQ API key](https://console.groq.com/)
- [Render account](https://render.com) (free)

---

## Step 1: Deploy Backend First

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **New +** → **Blueprint**
3. Connect your GitHub repo: `dhavalpatelpm/Zomato-AI-Restaurant-Recommendation`
4. Render will detect `render.yaml` and show both services
5. Before deploying, add environment variable for **zomato-api**:
   - **GROQ_API_KEY** → Paste your Groq API key
6. Click **Apply** to create both services

**Note:** The backend (zomato-api) will deploy first. It may take 2–5 minutes (dataset download). The first request can be slow due to cold start.

---

## Step 2: Get Backend URL

1. After deployment, open the **zomato-api** service
2. Copy the URL (e.g. `https://zomato-api-xxxx.onrender.com`)

---

## Step 3: Configure Frontend

1. Open the **zomato-frontend** service in Render
2. Go to **Environment**
3. Add/update **VITE_API_URL**:
   - Value: `https://zomato-api-xxxx.onrender.com` (your backend URL, no trailing slash)
4. Trigger a **Manual Deploy** (frontend must rebuild with the correct API URL)

---

## Step 4: Verify

1. Open your frontend URL (e.g. `https://zomato-frontend.onrender.com`)
2. Select locality, price range, cuisines, and rating
3. Click **Get Recommendations**
4. Confirm recommendations load

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "No localities available" | Backend may be spinning up. Wait 1–2 min and refresh. |
| CORS errors | Backend has `allow_origins=["*"]` – should work. Check backend logs. |
| 502 Bad Gateway | Backend crashed or timed out. Check logs for `GROQ_API_KEY` or dataset errors. |
| Slow first request | Free tier sleeps after ~15 min idle. First request wakes it (30–60 sec). |

---

## Custom Domains (Optional)

- **Backend:** Render Dashboard → zomato-api → Settings → Custom Domain
- **Frontend:** Render Dashboard → zomato-frontend → Settings → Custom Domain
- If you add a custom domain to frontend, set `VITE_API_URL` to your backend's custom domain and redeploy.
