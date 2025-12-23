from fastapi import HTTPException, Query
from typing import List, Optional
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import os
import requests
import re
from ORM.newsArticle import NewsArticle
from models.newsResponse import NewsResponse

env_path = Path('../') / '.env'
load_dotenv(dotenv_path=env_path)

NEWS_API_KEY = os.getenv("NEWSDATA_API_KEY")
NEWS_API_URL = "https://newsdata.io/api/1/market"


def normalize_source_name(source_name: str) -> Optional[str]:
    """Remove special characters and convert to uppercase"""
    if not source_name:
        return None
    return re.sub(r'[^a-zA-Z0-9]', '', source_name.upper().strip())


def retrieve_news(
    source: str = "market",
    symbols: Optional[List[str]] = Query(default=None),
):
    params = {
        "apikey": NEWS_API_KEY,
        "q": source,
        "language": "en",
        "sort": "pubdateasc",
    }
    if symbols:
        params["symbol"] = ",".join(symbols)

    try:
        response = requests.get(NEWS_API_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    data = response.json()

    articles: List[NewsArticle] = []
    for item in data.get("results", []):
        pubdate = item.get("pubDate")
        if pubdate and isinstance(pubdate, str):
            try:
                pubdate = datetime.fromisoformat(
                    pubdate.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pubdate = None

        keywords = item.get("keywords")
        if keywords and not isinstance(keywords, list):
            keywords = [keywords.upper()] if keywords else None
        elif keywords:
            keywords = [k.upper() if isinstance(
                k, str) else k for k in keywords]

        creator = item.get("creator")
        if creator and not isinstance(creator, list):
            creator = [creator.upper()] if creator else None
        elif creator:
            creator = [c.upper() if isinstance(c, str) else c for c in creator]

        symbol = item.get("symbol")
        if symbol and not isinstance(symbol, list):
            symbol = [symbol.upper()] if symbol else None
        elif symbol:
            symbol = [s.upper() if isinstance(s, str) else s for s in symbol]

        article = NewsArticle(
            title=item.get("title"),
            description=item.get("description"),
            content=item.get("content"),
            link=item.get("link"),
            imagelink=item.get("image_url"),
            keywords=keywords,
            creator=creator,
            symbol=symbol,
            pubdate=pubdate,
            sourcename=normalize_source_name(
                item.get("source_name")),
            sentiment=item.get("sentiment"),
            aisummary=item.get("ai_summary"),
        )
        articles.append(article)

    return NewsResponse(
        status=data.get("status", "error"),
        total_results=data.get("totalResults", 0),
        results=articles,
    )
