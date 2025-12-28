import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlmodel import Session
from ORM.userORM import UserORM
from ORM.userFeedORM import UserFeedORM


@pytest.mark.integration
class TestAddFeed:
    """Test feed creation endpoint"""

    def test_add_feed_success(self, client: TestClient, auth_headers: dict, test_user: UserORM):
        """Test successfully adding a new feed"""
        feed_data = {
            "feedname": "Tech Stocks",
            "stocks": ["AAPL", "GOOGL", "MSFT"],
            "sources": ["market"]
        }

        response = client.post("/feeds/add_feed", json=feed_data, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["feedname"] == feed_data["feedname"]
        assert data["stocks"] == feed_data["stocks"]
        assert data["sources"] == feed_data["sources"]
        assert "id" in data
        assert data["user_id"] == test_user.id

    def test_add_feed_without_auth(self, client: TestClient):
        """Test adding feed without authentication fails"""
        feed_data = {
            "feedname": "Tech Stocks",
            "stocks": ["AAPL"],
            "sources": ["market"]
        }

        response = client.post("/feeds/add_feed", json=feed_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_add_feed_exceeds_limit(self, client: TestClient, auth_headers: dict, session: Session, test_user: UserORM):
        """Test adding feed when user has reached their limit"""
        # Create feeds up to the limit (test_user has max 5 feeds)
        for i in range(5):
            feed = UserFeedORM(
                feedname=f"Feed {i}",
                stocks=["AAPL"],
                sources=["market"],
                user_id=test_user.id
            )
            session.add(feed)
        session.commit()

        # Try to add one more
        feed_data = {
            "feedname": "Extra Feed",
            "stocks": ["AAPL"],
            "sources": ["market"]
        }

        response = client.post("/feeds/add_feed", json=feed_data, headers=auth_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_add_feed_invalid_data(self, client: TestClient, auth_headers: dict):
        """Test adding feed with invalid data"""
        feed_data = {
            "feedname": "",  # Empty name
            "stocks": [],
            "sources": []
        }

        response = client.post("/feeds/add_feed", json=feed_data, headers=auth_headers)

        # Could be 422 for validation error
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            status.HTTP_400_BAD_REQUEST
        ]

    def test_add_feed_missing_fields(self, client: TestClient, auth_headers: dict):
        """Test adding feed with missing required fields"""
        response = client.post("/feeds/add_feed", json={}, headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.integration
class TestGetFeeds:
    """Test feed retrieval endpoints"""

    def test_get_user_feeds(self, client: TestClient, auth_headers: dict, test_feed: UserFeedORM):
        """Test getting feeds for current user"""
        response = client.get("/feeds/get_feeds", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(feed["id"] == test_feed.id for feed in data)

    def test_get_feeds_without_auth(self, client: TestClient):
        """Test getting feeds without authentication fails"""
        response = client.get("/feeds/get_feeds")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_feeds_empty_list(self, client: TestClient, auth_headers: dict):
        """Test getting feeds when user has no feeds"""
        response = client.get("/feeds/get_feeds", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        # User might have test_feed or not depending on fixture usage
        data = response.json()
        assert isinstance(data, list)

    def test_get_all_feeds_admin(self, client: TestClient, admin_auth_headers: dict, test_feed: UserFeedORM):
        """Test admin can get all feeds from all users"""
        response = client.get("/feeds/get_all_feeds", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_get_all_feeds_non_admin(self, client: TestClient, auth_headers: dict):
        """Test non-admin cannot get all feeds"""
        response = client.get("/feeds/get_all_feeds", headers=auth_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.integration
class TestEditFeed:
    """Test feed editing endpoint"""

    def test_edit_feed_success(self, client: TestClient, auth_headers: dict, test_feed: UserFeedORM):
        """Test successfully editing a feed"""
        update_data = {
            "feedname": "Updated Feed Name",
            "stocks": ["AAPL", "TSLA"],
            "sources": ["market", "crypto"]
        }

        response = client.put(f"/feeds/edit_feed/{test_feed.id}", json=update_data, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["feedname"] == update_data["feedname"]
        assert data["stocks"] == update_data["stocks"]
        assert data["sources"] == update_data["sources"]

    def test_edit_feed_partial_update(self, client: TestClient, auth_headers: dict, test_feed: UserFeedORM):
        """Test partial update of a feed"""
        update_data = {
            "feedname": "New Name Only"
        }

        response = client.put(f"/feeds/edit_feed/{test_feed.id}", json=update_data, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["feedname"] == update_data["feedname"]
        # Original stocks and sources should remain
        assert data["stocks"] == test_feed.stocks
        assert data["sources"] == test_feed.sources

    def test_edit_nonexistent_feed(self, client: TestClient, auth_headers: dict):
        """Test editing a feed that doesn't exist"""
        update_data = {
            "feedname": "New Name"
        }

        response = client.put("/feeds/edit_feed/99999", json=update_data, headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_edit_feed_without_auth(self, client: TestClient, test_feed: UserFeedORM):
        """Test editing feed without authentication fails"""
        update_data = {
            "feedname": "New Name"
        }

        response = client.put(f"/feeds/edit_feed/{test_feed.id}", json=update_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_edit_other_user_feed(self, client: TestClient, auth_headers: dict, session: Session, admin_user: UserORM):
        """Test user cannot edit another user's feed"""
        # Create a feed owned by admin
        admin_feed = UserFeedORM(
            feedname="Admin Feed",
            stocks=["AAPL"],
            sources=["market"],
            user_id=admin_user.id
        )
        session.add(admin_feed)
        session.commit()
        session.refresh(admin_feed)

        update_data = {
            "feedname": "Hacked Name"
        }

        response = client.put(f"/feeds/edit_feed/{admin_feed.id}", json=update_data, headers=auth_headers)

        # Should be forbidden or not found
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]


@pytest.mark.integration
class TestDeleteFeed:
    """Test feed deletion endpoint"""

    def test_delete_feed_success(self, client: TestClient, auth_headers: dict, test_feed: UserFeedORM):
        """Test successfully deleting a feed"""
        response = client.delete(f"/feeds/delete_feed/{test_feed.id}", headers=auth_headers)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify feed is deleted
        get_response = client.get("/feeds/get_feeds", headers=auth_headers)
        feeds = get_response.json()
        assert not any(feed["id"] == test_feed.id for feed in feeds)

    def test_delete_nonexistent_feed(self, client: TestClient, auth_headers: dict):
        """Test deleting a feed that doesn't exist"""
        response = client.delete("/feeds/delete_feed/99999", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_feed_without_auth(self, client: TestClient, test_feed: UserFeedORM):
        """Test deleting feed without authentication fails"""
        response = client.delete(f"/feeds/delete_feed/{test_feed.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_other_user_feed(self, client: TestClient, auth_headers: dict, session: Session, admin_user: UserORM):
        """Test user cannot delete another user's feed"""
        # Create a feed owned by admin
        admin_feed = UserFeedORM(
            feedname="Admin Feed",
            stocks=["AAPL"],
            sources=["market"],
            user_id=admin_user.id
        )
        session.add(admin_feed)
        session.commit()
        session.refresh(admin_feed)

        response = client.delete(f"/feeds/delete_feed/{admin_feed.id}", headers=auth_headers)

        # Should be forbidden or not found
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
