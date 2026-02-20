import json
import nltk
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.scraper import scrape_sources_for_category
from app.summarizer import summarize_text, build_insights

app = FastAPI(title="JugNews")

try:
    nltk.data.find('tokenizers/punkt')
except Exception:
    try:
        nltk.download('punkt')
    except Exception:
        pass


@app.get("/api/categories")
def list_categories():
    with open("config/sources.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return {"categories": list(data.keys())}


@app.get("/api/scrape")
def scrape(category: str = "finance", max_articles: int = 5, summary_sentences: int = 3):
    with open("config/sources.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    if category not in data:
        raise HTTPException(status_code=404, detail="Unknown category")
    sources = data[category]
    articles = scrape_sources_for_category(sources, max_articles=max_articles)
    for a in articles:
        a["summary"] = summarize_text(a.get("text", ""), sentence_count=summary_sentences)
        a.pop("text", None)
    insights = build_insights(articles, category=category)
    return {"category": category, "articles": articles, "insights": insights}


@app.get("/api/dashboard")
def dashboard(max_articles_per_category: int = 5, summary_sentences: int = 3):
    with open("config/sources.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    payload = {}
    for category, sources in data.items():
        articles = scrape_sources_for_category(sources, max_articles=max_articles_per_category)
        for article in articles:
            article["summary"] = summarize_text(article.get("text", ""), sentence_count=summary_sentences)
            article.pop("text", None)
        payload[category] = {
            "articles": articles,
            "insights": build_insights(articles, category=category),
        }

    return {"categories": payload}


@app.get("/")
def home():
    return FileResponse("static/index.html")


app.mount("/", StaticFiles(directory="static", html=True), name="static")
