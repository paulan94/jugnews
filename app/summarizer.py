from __future__ import annotations

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer
import re
from collections import Counter
from typing import Dict, List

STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "to",
    "of",
    "in",
    "on",
    "for",
    "with",
    "from",
    "at",
    "by",
    "is",
    "are",
    "was",
    "were",
    "be",
    "as",
    "that",
    "this",
    "it",
    "its",
    "new",
    "after",
    "over",
    "into",
    "about",
    "news",
    "says",
}

def summarize_text(text: str, sentence_count: int = 3) -> str:
    if not text or len(text.split()) < 40:
        return (text or "")[:800]
    try:
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = TextRankSummarizer()
        sentences = summarizer(parser.document, sentence_count)
        return " ".join(str(s) for s in sentences)
    except Exception:
        return (text or "")[:800]


def build_insights(articles: List[Dict], category: str) -> Dict:
    corpus_chunks = []
    for article in articles:
        corpus_chunks.append(article.get("title", ""))
        corpus_chunks.append(article.get("summary", "") or article.get("text", ""))
    corpus = " ".join(corpus_chunks)

    words = re.findall(r"\b[a-zA-Z]{4,}\b", corpus.lower())
    keywords = [w for w in words if w not in STOPWORDS]
    top_keywords = [word for word, _ in Counter(keywords).most_common(8)]

    headlines = [a.get("title", "") for a in articles if a.get("title")]
    ticker_candidates = re.findall(r"\b[A-Z]{1,5}\b", " ".join(headlines))
    blocked = {"THE", "AND", "WITH", "FROM", "US", "UAP", "UFO", "NASA", "BBC", "AP"}
    tickers = [t for t in ticker_candidates if t not in blocked]
    top_tickers = [t for t, _ in Counter(tickers).most_common(6)]

    source_count = len({a.get("source", "") for a in articles if a.get("source")})
    article_count = len(articles)

    return {
        "category": category,
        "article_count": article_count,
        "source_count": source_count,
        "top_keywords": top_keywords,
        "mentioned_tickers": top_tickers,
    }
