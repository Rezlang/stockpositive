import logging
import re

from sqlmodel import Session, select

from ORM.newsArticleORM import NewsArticleORM
from ORM.userFeedORM import UserFeedORM


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def normalize_source_name(source_name: str) -> str | None:
    if not source_name:
        return None
    return re.sub(r"[^a-zA-Z0-9]", "", source_name.upper().strip())


def get_news_for_feed(feed_id: int, db: Session, current_user_id: int) -> list[NewsArticleORM]:
    from services.dbService.repositories import OwnedResourceRepository

    logger.info(f"Fetching news for feed_id={feed_id}, user_id={current_user_id}")

    feed_repo = OwnedResourceRepository(UserFeedORM, db, current_user_id)
    feed = feed_repo.get_owned_by_id_or_404(feed_id)

    results: list[NewsArticleORM] = []

    symbols = feed.stocks or []
    sources = feed.sources or []

    logger.info(f"Feed symbols: {symbols}")
    logger.info(f"Feed sources (raw): {sources}")

    normalized_sources = []
    if sources:
        normalized_sources = [normalize_source_name(s) for s in sources]
        logger.info(f"Normalized sources: {normalized_sources}")

    for symbol in symbols:
        logger.info(f"Querying news for symbol: {symbol}")

        statement = select(NewsArticleORM).where(NewsArticleORM.symbols.contains([symbol]))

        # Count articles after symbol filter
        pre_source_count = len(db.exec(statement).all())
        logger.info(f"Articles after symbol filter ({symbol}): {pre_source_count}")

        if normalized_sources:
            statement = statement.where(NewsArticleORM.sourcename.in_(normalized_sources))
            post_source_count = len(db.exec(statement).all())
            logger.info(f"Articles after source filter ({symbol}): {post_source_count}")

        articles = db.exec(statement.order_by(NewsArticleORM.pubdate.desc()).limit(10)).all()

        logger.info(f"Articles returned for symbol {symbol}: {len(articles)}")

        if articles:
            logger.info(
                f"Sample article titles for {symbol}: {[a.title for a in articles[:3]]}"
            )

        results.extend(articles)

    logger.info(f"Total articles returned: {len(results)}")

    return results
