# SaaSquatch Leads - Python Flask Backend (Vercel Deployment)

This directory is ready to be deployed standalone on **Vercel** as a Python Serverless Function.

## Files Structure for Vercel
- `index.py`: Vercel WSGI Serverless entrypoint exporting `app`.
- `scraper_server.py`: Main Flask application with `/`, `/api/health`, `/api/search_leads`, `/api/generate_email`.
- `search_engine.py`: Live search engine module discovering company domains.
- `website_scraper.py`: Real-time contact & company intelligence scraper.
- `requirements.txt`: Python package dependencies.
- `templates/index.html`: Responsive HTML status landing page served at root `/`.
- `vercel.json`: Vercel Python routing configuration.

---

## How to Deploy to Vercel

### Option 1: Via Vercel CLI
```bash
cd backend
vercel
```

### Option 2: Via Vercel Web Dashboard (GitHub)
1. Import your repository into [Vercel](https://vercel.com/new).
2. Set **Root Directory** to `backend`.
3. Framework Preset: **Other**.
4. Click **Deploy**.

---

## Live Endpoints Once Deployed
- **Dashboard & Docs (HTML)**: `https://<your-project>.vercel.app/`
- **Health Check**: `https://<your-project>.vercel.app/api/health`
- **Search Leads**: `POST https://<your-project>.vercel.app/api/search_leads`
- **Make Mail AI**: `POST https://<your-project>.vercel.app/api/generate_email`
