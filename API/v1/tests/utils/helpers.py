"""
Test utility functions and helpers
"""

from typing import Optional

from sqlmodel import Session

from ORM.newsArticleORM import NewsArticleORM
from ORM.permissionORM import PermissionORM
from ORM.userFeedORM import UserFeedORM
from ORM.userGroupORM import UserGroupORM
from ORM.userGroupPermissionORM import UserGroupPermissionORM
from ORM.userORM import UserORM
from services.authService.authService import create_access_token, get_password_hash


def create_user_with_permissions(
    session: Session,
    email: str,
    password: str,
    permissions: list[dict[str, any]],
    group_name: str | None = None,
) -> UserORM:
    """
    Create a user with specific permissions.

    Args:
        session: Database session
        email: User email
        password: User password (will be hashed)
        permissions: List of permission dicts with 'name' and optional 'max_value'
        group_name: Optional custom group name

    Returns:
        Created UserORM instance

    Example:
        user = create_user_with_permissions(
            session,
            "test@example.com",
            "password123",
            [
                {"name": "GET.NEWS"},
                {"name": "ADD.FEED", "max_value": 10}
            ]
        )
    """
    # Create user group
    if group_name is None:
        group_name = f"group_{email}"

    user_group = UserGroupORM(name=group_name)
    session.add(user_group)
    session.commit()
    session.refresh(user_group)

    # Create permissions
    for perm_data in permissions:
        perm = PermissionORM(name=perm_data["name"])
        session.add(perm)
    session.commit()

    # Link permissions to user group
    for perm_data in permissions:
        perm = session.query(PermissionORM).filter(PermissionORM.name == perm_data["name"]).first()
        if perm:
            perm_value = perm_data.get("max_value")
            ugp = UserGroupPermissionORM(
                usergroup_id=user_group.id, permission_id=perm.id, permission_value=perm_value
            )
            session.add(ugp)
    session.commit()

    # Create user
    username = email.split("@")[0]  # Generate username from email
    user = UserORM(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        usergroup_id=user_group.id,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def create_test_feed(
    session: Session,
    owner: UserORM,
    feedname: str = "Test Feed",
    stocks: list[str] | None = None,
    sources: list[str] | None = None,
) -> UserFeedORM:
    """
    Create a test feed for a user.

    Args:
        session: Database session
        owner: User who owns the feed
        feedname: Name of the feed
        stocks: List of stock symbols
        sources: List of news sources

    Returns:
        Created UserFeedORM instance
    """
    if stocks is None:
        stocks = ["AAPL", "MSFT"]
    if sources is None:
        sources = ["market"]

    feed = UserFeedORM(feedname=feedname, stocks=stocks, sources=sources, user_id=owner.id)
    session.add(feed)
    session.commit()
    session.refresh(feed)

    return feed


def create_test_news_article(
    session: Session,
    symbol: str = "AAPL",
    title: str = "Test Article",
    link: str | None = None,
    pubdate: str = "2024-01-01 12:00:00",
    sourcename: str = "TestSource",
) -> NewsArticleORM:
    """
    Create a test news article.

    Args:
        session: Database session
        symbol: Stock symbol
        title: Article title
        link: Article URL
        pubdate: Publication date
        sourcename: Source name

    Returns:
        Created NewsArticleORM instance
    """
    if link is None:
        link = f"https://example.com/{symbol.lower()}"

    article = NewsArticleORM(
        symbol=symbol, title=title, link=link, pubdate=pubdate, sourcename=sourcename
    )
    session.add(article)
    session.commit()
    session.refresh(article)

    return article


def get_auth_headers(user: UserORM) -> dict[str, str]:
    """
    Generate authentication headers for a user.

    Args:
        user: User to generate token for

    Returns:
        Dictionary with Authorization header
    """
    access_token = create_access_token(data={"sub": user.email})
    return {"Authorization": f"Bearer {access_token}"}


def assert_valid_response_structure(response_data: dict, expected_fields: list[str]):
    """
    Assert that a response contains expected fields.

    Args:
        response_data: Response JSON data
        expected_fields: List of field names that should be present
    """
    for field in expected_fields:
        assert field in response_data, f"Expected field '{field}' not found in response"


def create_multiple_feeds(
    session: Session, owner: UserORM, count: int, base_name: str = "Feed"
) -> list[UserFeedORM]:
    """
    Create multiple test feeds for a user.

    Args:
        session: Database session
        owner: User who owns the feeds
        count: Number of feeds to create
        base_name: Base name for feeds (will be numbered)

    Returns:
        List of created UserFeedORM instances
    """
    feeds = []
    for i in range(count):
        feed = create_test_feed(
            session,
            owner,
            feedname=f"{base_name} {i + 1}",
            stocks=[f"STOCK{i}"],
            sources=["market"],
        )
        feeds.append(feed)

    return feeds


def create_multiple_news_articles(
    session: Session, symbols: list[str], count_per_symbol: int = 1
) -> list[NewsArticleORM]:
    """
    Create multiple news articles for different symbols.

    Args:
        session: Database session
        symbols: List of stock symbols
        count_per_symbol: Number of articles to create per symbol

    Returns:
        List of created NewsArticleORM instances
    """
    articles = []
    for symbol in symbols:
        for i in range(count_per_symbol):
            article = create_test_news_article(
                session,
                symbol=symbol,
                title=f"{symbol} News {i + 1}",
                pubdate=f"2024-01-{(i + 1):02d} 12:00:00",
            )
            articles.append(article)

    return articles
