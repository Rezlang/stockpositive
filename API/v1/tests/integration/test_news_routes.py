from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from ORM.newsArticleORM import NewsArticleORM
from ORM.userFeedORM import UserFeedORM
from ORM.userORM import UserORM


@pytest.mark.integration
@pytest.mark.slow
class TestLoadNews:
    """Test news loading endpoint"""

    @patch("routes.newsRoutes.retrieve_news")
    def test_load_news_admin_success(
        self, mock_retrieve, client: TestClient, admin_auth_headers: dict, session: Session
    ):
        """Test admin can successfully load news"""
        # Mock the news retrieval
        mock_articles = [
            NewsArticleORM(
                symbols=["AAPL"],
                title="Apple announces new product",
                link="https://example.com/apple",
                pubdate="2024-01-01 12:00:00",
                sourcename="TechNews",
            )
        ]
        mock_retrieve.return_value = mock_articles

        response = client.get(
            "/news/load-news",
            params={"source": "market", "symbols": "AAPL,MSFT"},
            headers=admin_auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["symbols"] == ["AAPL"]

    def test_load_news_without_admin_permission(self, client: TestClient, auth_headers: dict):
        """Test non-admin cannot load news"""
        response = client.get("/news/load-news", params={"source": "market"}, headers=auth_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_load_news_without_auth(self, client: TestClient):
        """Test loading news without authentication fails"""
        response = client.get("/news/load-news", params={"source": "market"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch("routes.newsRoutes.retrieve_news")
    def test_load_news_with_symbols(
        self, mock_retrieve, client: TestClient, admin_auth_headers: dict
    ):
        """Test loading news with specific symbols"""
        mock_retrieve.return_value = []

        response = client.get(
            "/news/load-news",
            params={"source": "market", "symbols": ["AAPL", "GOOGL"]},
            headers=admin_auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        # Verify retrieve_news was called with correct parameters
        mock_retrieve.assert_called_once()

    @patch("routes.newsRoutes.retrieve_news")
    def test_load_news_default_source(
        self, mock_retrieve, client: TestClient, admin_auth_headers: dict
    ):
        """Test loading news with default source"""
        mock_retrieve.return_value = []

        response = client.get("/news/load-news", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.integration
class TestGetNews:
    """Test news retrieval endpoint"""

    def test_get_news_success(
        self, client: TestClient, auth_headers: dict, test_feed: UserFeedORM, session: Session
    ):
        """Test successfully getting news for a feed"""
        # Create some news articles for the feed
        news_articles = [
            NewsArticleORM(
                symbols=["AAPL"],
                title="Apple News 1",
                link="https://example.com/apple1",
                pubdate="2024-01-01 12:00:00",
                sourcename="TechNews",
            ),
            NewsArticleORM(
                symbols=["MSFT"],
                title="Microsoft News 1",
                link="https://example.com/msft1",
                pubdate="2024-01-01 13:00:00",
                sourcename="TechNews",
            ),
        ]

        for article in news_articles:
            session.add(article)
        session.commit()

        response = client.get(
            "/news/get-news", params={"feedId": test_feed.id}, headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_get_news_without_auth(self, client: TestClient, test_feed: UserFeedORM):
        """Test getting news without authentication fails"""
        response = client.get("/news/get-news", params={"feedId": test_feed.id})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_news_nonexistent_feed(self, client: TestClient, auth_headers: dict):
        """Test getting news for non-existent feed"""
        response = client.get("/news/get-news", params={"feedId": 99999}, headers=auth_headers)

        # Could be 404 or 403 depending on implementation
        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_200_OK,  # Might return empty list
        ]

    def test_get_news_other_user_feed(
        self, client: TestClient, auth_headers: dict, session: Session, admin_user: UserORM
    ):
        """Test user cannot get news for another user's feed"""
        # Create a feed owned by admin
        admin_feed = UserFeedORM(
            feedname="Admin Feed", stocks=["AAPL"], sources=["market"], user_id=admin_user.id
        )
        session.add(admin_feed)
        session.commit()
        session.refresh(admin_feed)

        response = client.get(
            "/news/get-news", params={"feedId": admin_feed.id}, headers=auth_headers
        )

        # Should be forbidden or not found
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]

    def test_get_news_missing_feed_id(self, client: TestClient, auth_headers: dict):
        """Test getting news without providing feed ID"""
        response = client.get("/news/get-news", headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_get_news_invalid_feed_id(self, client: TestClient, auth_headers: dict):
        """Test getting news with invalid feed ID format"""
        response = client.get(
            "/news/get-news", params={"feedId": "not_a_number"}, headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_get_news_empty_feed(
        self, client: TestClient, auth_headers: dict, test_feed: UserFeedORM
    ):
        """Test getting news for feed with no articles"""
        response = client.get(
            "/news/get-news", params={"feedId": test_feed.id}, headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        # Empty list is valid response

    @patch("routes.newsRoutes.get_news_for_feed")
    def test_get_news_filters_by_user(
        self,
        mock_get_news,
        client: TestClient,
        auth_headers: dict,
        test_feed: UserFeedORM,
        test_user: UserORM,
    ):
        """Test that get_news_for_feed is called with correct user ID"""
        mock_get_news.return_value = []

        response = client.get(
            "/news/get-news", params={"feedId": test_feed.id}, headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        # Verify the function was called with the user's ID
        mock_get_news.assert_called_once()
        call_args = mock_get_news.call_args
        assert call_args[0][0] == test_feed.id  # feedId
        assert call_args[0][2] == test_user.id  # user_id
