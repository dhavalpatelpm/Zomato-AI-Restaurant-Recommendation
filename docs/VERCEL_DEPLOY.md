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
