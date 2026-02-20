# JugNews Pulse - Local News and Signals Dashboard

Quick local app that aggregates topic-focused sources, summarizes articles, and surfaces simple insights in a lightweight HTML/CSS UI.

## What this version includes

- Category feeds for:
  - `finance`
  - `world`
  - `epstein-files`
  - `aliens`
  - `social-professional`
- RSS-first ingestion (faster and more stable than scraping homepage HTML).
- Extractive summaries (TextRank via Sumy).
- Simple insights:
  - article count
  - source count
  - top keywords
  - headline ticker mentions
- Dashboard UI with:
  - stream navigation
  - category refresh
  - all-category snapshot

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

NLTK tokenizer setup:

```python
import nltk
nltk.download("punkt")
```

Run:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`.

## Deploy frontend on GitHub Pages

GitHub Pages can host the static UI in `static/`, but it cannot run the FastAPI backend.

This repo includes `.github/workflows/deploy-pages.yml`, which deploys `static/` to Pages on pushes to `main`.

After pushing:

1. In GitHub, go to `Settings -> Pages`.
2. Set `Source` to `GitHub Actions`.
3. Wait for the `Deploy GitHub Pages` workflow to finish.

If your API is hosted separately, set its origin in `static/config.js`:

```js
window.JUGNEWS_API_BASE = "https://your-api.example.com";
```

If `JUGNEWS_API_BASE` is empty, the UI uses the same origin (works for local FastAPI serving).

## Notes on social/professional platforms

`LinkedIn`, `Facebook`, and `Instagram` are intentionally implemented as connector stubs.

Reason:
- Direct scraping is brittle and commonly violates terms/platform rules.
- Official APIs + OAuth are the reliable path.

Extension path:
1. Add API client modules under `app/` for each platform.
2. Exchange OAuth tokens and store them securely.
3. Convert API responses to the app article shape:
   - `title`
   - `text`
   - `url`
   - `source`
   - `published`
4. Replace `social_stub` entries in `config/sources.json` with real connector types.
