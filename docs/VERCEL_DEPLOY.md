# Deploy Frontend to Vercel

Quick guide to deploy the React frontend on Vercel.

---

## Prerequisites

- Backend deployed (e.g. Render) with a public URL
- GitHub repo connected to Vercel

---

## Steps

1. Go to [vercel.com](https://vercel.com) → **Add New** → **Project**
2. Import `Zomato-AI-Restaurant-Recommendation`
3. **Root Directory**: `frontend` (click Edit, set to `frontend`)
4. **Environment Variable**: Add `VITE_API_URL` = `https://your-backend.onrender.com` (no trailing slash)
5. Click **Deploy**

---

## After Deploy

- Ensure your backend allows CORS from `*.vercel.app`
- Test the app at your Vercel URL

---

## Troubleshooting

### "0 Localities" / "Retry loading localities" / Data won't load

**Cause:** Frontend can't reach the backend API.

**Fix:**
1. **Deploy backend first** – Use [Render](https://render.com) (see `docs/RENDER_DEPLOY.md`). Add `GROQ_API_KEY` to the backend service.
2. **Set `VITE_API_URL` in Vercel:**
   - Project → **Settings** → **Environment Variables**
   - Add: `VITE_API_URL` = `https://your-backend-url.onrender.com` (no trailing slash)
3. **Redeploy** – Trigger a new deployment so the build picks up the variable.
4. **Verify** – Backend must be running and reachable. Test `https://your-backend.onrender.com/health` in a browser.
