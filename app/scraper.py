from __future__ import annotations

from typing import Dict, List, Any
import re

import feedparser
import requests
from bs4 import BeautifulSoup
from newspaper import Article

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)


def _extract_text_from_html(url: str, timeout: int = 10) -> str:
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": USER_AGENT})
        if resp.status_code >= 400:
            return ""
        soup = BeautifulSoup(resp.text, "html.parser")
        paragraphs = [p.get_text(" ", strip=True) for p in soup.select("article p, p")]
        cleaned = " ".join(p for p in paragraphs if len(p.split()) > 6)
        return re.sub(r"\s+", " ", cleaned).strip()[:20000]
    except Exception:
        return ""


def scrape_url(url: str, source_name: str = "") -> Dict[str, Any]:
    try:
        article = Article(url)
        article.download()
        article.parse()
        text = (article.text or "").strip()
        if not text:
            text = _extract_text_from_html(url)
        return {
            "title": article.title or url,
            "text": text,
            "url": url,
            "source": source_name or url,
        }
    except Exception:
        fallback_text = _extract_text_from_html(url)
        return {
            "title": url,
            "text": fallback_text,
            "url": url,
            "source": source_name or url,
        }


def _entry_to_article(entry: Any, source_name: str) -> Dict[str, Any]:
    summary = (
        getattr(entry, "summary", "")
        or getattr(entry, "description", "")
        or getattr(entry, "title", "")
    )
    summary_text = BeautifulSoup(summary, "html.parser").get_text(" ", strip=True)
    return {
        "title": getattr(entry, "title", "") or "Untitled",
        "text": summary_text,
        "url": getattr(entry, "link", "") or "",
        "source": source_name,
        "published": getattr(entry, "published", "") or getattr(entry, "updated", ""),
    }


def _scrape_rss_source(source: Dict[str, Any], per_source_limit: int) -> List[Dict[str, Any]]:
    feed = feedparser.parse(source["url"])
    items: List[Dict[str, Any]] = []
    for entry in feed.entries[:per_source_limit]:
        items.append(_entry_to_article(entry, source.get("name", source["url"])))
    return items


def _social_stub_items(source: Dict[str, Any]) -> List[Dict[str, Any]]:
    name = source.get("name", "Social Feed")
    return [
        {
            "title": f"{name} connector not configured",
            "text": (
                f"{name} is listed as a source, but direct scraping is disabled. "
                f"Use the official {name} API + OAuth and map recent posts/updates here."
            ),
            "url": source.get("url", ""),
            "source": name,
            "published": "",
            "stub": True,
        }
    ]


def scrape_sources_for_category(sources: List[Any], max_articles: int = 8) -> List[Dict[str, Any]]:
    if not sources:
        return []

    normalized_sources: List[Dict[str, Any]] = []
    for raw in sources:
        if isinstance(raw, str):
            normalized_sources.append({"name": raw, "type": "web", "url": raw})
        elif isinstance(raw, dict):
            normalized_sources.append(raw)

    per_source = max(1, max_articles // max(1, len(normalized_sources)))
    results: List[Dict[str, Any]] = []

    for source in normalized_sources:
        source_type = source.get("type", "web")

        if source_type == "rss":
            results.extend(_scrape_rss_source(source, per_source_limit=per_source + 1))
        elif source_type == "social_stub":
            results.extend(_social_stub_items(source))
        else:
            results.append(scrape_url(source.get("url", ""), source_name=source.get("name", "")))

        if len(results) >= max_articles:
            break

    return results[:max_articles]
