import logging
import random
from datetime import datetime

from sqlalchemy.orm import Session
from sqlmodel import or_, select

from models.newsArticle import NewsArticle
from models.newsResponse import PaginatedNewsResponse
from ORM.newsArticleORM import NewsArticleORM
from ORM.userFeedORM import UserFeedORM
from services.dbService.crud.newsInsert import create_news_article
from services.retrieveNews import normalize_source_name, retrieve_news


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

PAGE_SIZE = 10
MAX_SYMBOLS_PER_API_CALL = 5
MAX_SOURCES_PER_API_CALL = 5
MAX_API_BATCHES = 2

# Mapping from domain URLs to normalized source names (as stored in DB)
# The API returns source_name which gets normalized via normalize_source_name()
DOMAIN_TO_SOURCE_NAME = {
    "finance.yahoo.com": "YAHOOFINANCE",
    "bloomberg.com": "BLOOMBERG",
    "reuters.com": "REUTERS",
    "cnbc.com": "CNBC",
    "fool.com": "FOOLCOM",
    "coinmarketcap.com": "COINMARKETCAP",
    "binance.com": "BINANCE",
    "investing.com": "INVESTINGCOM",
}


def _query_articles(
    db: Session,
    symbols: list[str],
    sources: list[str],
    before_date: datetime | None,
    limit: int,
) -> list[NewsArticleORM]:
    """
    Query articles with optional symbol and source filtering.
    - Empty symbols list means "all stocks" (no stock filter applied)
    - Empty sources list means "all sources" (no source filter applied)
    Applies date cursor if provided.
    Returns articles ordered by pubdate DESC.
    """
    statement = select(NewsArticleORM)

    # Apply symbol filter only if symbols are specified
    # Empty list = "all stocks" (whitelist all)
    if symbols:
        symbol_conditions = [NewsArticleORM.symbols.contains([s]) for s in symbols]
        statement = statement.where(or_(*symbol_conditions))

    # Apply source filter only if sources are specified
    # Empty list = "all sources" (whitelist all)
    if sources:
        db_source_names = [
            DOMAIN_TO_SOURCE_NAME.get(s.lower(), normalize_source_name(s)) for s in sources
        ]
        statement = statement.where(NewsArticleORM.sourcename.in_(db_source_names))

    # Apply cursor pagination (get articles OLDER than before_date)
    if before_date:
        statement = statement.where(NewsArticleORM.pubdate < before_date)

    # Order by newest first, then by ID for deterministic ordering when pubdates match
    statement = statement.order_by(
        NewsArticleORM.pubdate.desc(),
        NewsArticleORM.id.desc(),
    ).limit(limit)

    return list(db.exec(statement).all())


def _create_random_batches(
    symbols: list[str], sources: list[str]
) -> list[tuple[list[str], list[str]]]:
    """
    Create up to MAX_API_BATCHES batches with random distribution of symbols and sources.
    Each batch has at most MAX_SYMBOLS_PER_API_CALL symbols and MAX_SOURCES_PER_API_CALL sources.
    """
    if not symbols and not sources:
        return []

    # Shuffle for random distribution
    shuffled_symbols = symbols.copy()
    shuffled_sources = sources.copy()
    random.shuffle(shuffled_symbols)
    random.shuffle(shuffled_sources)

    # If everything fits in one call, return single batch
    if (
        len(shuffled_symbols) <= MAX_SYMBOLS_PER_API_CALL
        and len(shuffled_sources) <= MAX_SOURCES_PER_API_CALL
    ):
        return [(shuffled_symbols, shuffled_sources)]

    # Split into 2 batches
    batches = []
    for i in range(MAX_API_BATCHES):
        sym_start = i * MAX_SYMBOLS_PER_API_CALL
        sym_end = sym_start + MAX_SYMBOLS_PER_API_CALL
        src_start = i * MAX_SOURCES_PER_API_CALL
        src_end = src_start + MAX_SOURCES_PER_API_CALL

        batch_symbols = shuffled_symbols[sym_start:sym_end]
        batch_sources = shuffled_sources[src_start:src_end]

        # Only add batch if it has at least symbols or sources
        if batch_symbols or batch_sources:
            batches.append((batch_symbols, batch_sources))

    return batches


def _fetch_and_store_articles(
    db: Session,
    symbols: list[str],
    sources: list[str],
) -> int:
    """
    Fetch articles from NewsData.io API for the given symbols and sources.
    Handles batching for >5 symbols/sources (API limit).
    Stores new articles in DB.
    Returns count of new articles stored.

    If symbols is empty, fetches general market news (no symbol filter).
    If sources is empty, fetches from all sources (no source filter).
    """
    # If no symbols, fetch general market news
    if not symbols:
        batches = [([], sources)]
    else:
        batches = _create_random_batches(symbols, sources)
    total_stored = 0

    for batch_symbols, batch_sources in batches:
        try:
            print(f"Fetching news for symbols={batch_symbols}, sources={batch_sources}")

            # Call retrieve_news with symbols only - don't filter by domainurl at API level
            # The API's domainurl filter is too restrictive when combined with symbols
            # We'll filter by source when reading from DB instead
            articles = retrieve_news(
                source="market",
                symbols=batch_symbols if batch_symbols else None,
                domainurls=None,  # Don't filter by source at API level
            )
            print(f"API returned {len(articles)} articles")

            for article in articles:
                # Check if article already exists (by link to avoid duplicates)
                existing = db.exec(
                    select(NewsArticleORM).where(NewsArticleORM.link == article.link)
                ).first()

                if not existing:
                    create_news_article(article, db)
                    total_stored += 1

            print(f"Stored {total_stored} new articles from batch")

        except Exception as e:
            # Log error but continue with next batch
            print(f"Failed to fetch news for batch symbols={batch_symbols}: {e}")
            continue

    return total_stored


def _deduplicate_by_id(articles: list[NewsArticleORM]) -> list[NewsArticleORM]:
    """Remove duplicate articles by ID, preserving order."""
    seen_ids = set()
    deduplicated = []
    for article in articles:
        if article.id not in seen_ids:
            seen_ids.add(article.id)
            deduplicated.append(article)
    return deduplicated


def get_news_for_feed(
    feedId: int,
    db: Session,
    currentUserId: int,
    beforeDate: datetime | None = None,
) -> PaginatedNewsResponse:
    from services.dbService.repositories import OwnedResourceRepository

    logger.info(
        f"Fetching news for feedId={feedId}, userId={currentUserId}, beforeDate={beforeDate}"
    )

    # 1. Get the feed (with ownership check)
    feedRepo = OwnedResourceRepository(UserFeedORM, db, currentUserId)
    feed = feedRepo.get_owned_by_id_or_404(feedId)

    symbols = feed.stocks or []
    sources = feed.sources or []

    logger.info(f"Feed symbols: {symbols}, sources: {sources}")

    # 2. Query DB for 2 * PAGE_SIZE articles (to check if we have enough remaining)
    # Empty symbols = all stocks, empty sources = all sources
    articles = _query_articles(db, symbols, sources, beforeDate, limit=2 * PAGE_SIZE)

    # 4. Deduplicate by article ID
    deduplicated = _deduplicate_by_id(articles)

    # 5. If < PAGE_SIZE articles, fetch from API immediately before responding
    if len(deduplicated) < PAGE_SIZE:
        print(f"Only {len(deduplicated)} articles found, fetching more from API...")
        stored = _fetch_and_store_articles(db, symbols, sources)
        print(f"Stored {stored} new articles from API")

        # Re-query after fetching
        articles = _query_articles(db, symbols, sources, beforeDate, limit=2 * PAGE_SIZE)
        deduplicated = _deduplicate_by_id(articles)

    # 6. Take first PAGE_SIZE articles for response
    responseArticles = deduplicated[:PAGE_SIZE]
    remainingArticles = deduplicated[PAGE_SIZE:]

    # 7. Build response with cursor
    hasMore = len(remainingArticles) > 0
    nextCursor = responseArticles[-1].pubdate if responseArticles and hasMore else None

    result = PaginatedNewsResponse(
        articles=[NewsArticle.model_validate(a, from_attributes=True) for a in responseArticles],
        next_cursor=nextCursor,
        has_more=hasMore,
        total_returned=len(responseArticles),
    )

    # 8. If < PAGE_SIZE remaining after returning first batch, fetch more (synchronous, after building response)
    needBackgroundFetch = len(remainingArticles) < PAGE_SIZE and len(responseArticles) == PAGE_SIZE
    if needBackgroundFetch:
        logger.info(
            f"Only {len(remainingArticles)} articles remaining, fetching more for next request..."
        )
        _fetch_and_store_articles(db, symbols, sources)

    logger.info(f"Returning {len(responseArticles)} articles, hasMore={hasMore}")

    return result
