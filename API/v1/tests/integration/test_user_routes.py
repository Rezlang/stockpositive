import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from ORM.userORM import UserORM


@pytest.mark.integration
class TestUserRegistration:
    """Test user registration endpoint"""

    def test_register_new_user_success(self, client: TestClient, session: Session):
        """Test successful user registration"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "phone_number": "+1234567890",
            "password": "SecurePassword123!",
        }

        response = client.post("/users/register", json=user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "id" in data
        assert "hashed_password" not in data  # Should not expose password

    def test_register_duplicate_email(self, client: TestClient, test_user: UserORM):
        """Test registration with existing email fails"""
        user_data = {
            "username": "anotheruser",
            "email": test_user.email,
            "phone_number": "+9876543210",
            "password": "AnotherPassword123!",
        }

        response = client.post("/users/register", json=user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email format"""
        user_data = {
            "username": "testuser123",
            "email": "notanemail",
            "phone_number": "+1234567890",
            "password": "SecurePassword123!",
        }

        response = client.post("/users/register", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_register_weak_password(self, client: TestClient):
        """Test registration with weak password"""
        user_data = {
            "username": "weakuser",
            "email": "newuser@example.com",
            "phone_number": "+1234567890",
            "password": "123",
        }

        response = client.post("/users/register", json=user_data)

        # Depending on password validation rules, this might be 422 or 400
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            status.HTTP_400_BAD_REQUEST,
        ]

    def test_register_missing_fields(self, client: TestClient):
        """Test registration with missing required fields"""
        response = client.post("/users/register", json={})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.integration
class TestUserLogin:
    """Test user login endpoint"""

    def test_login_success(self, client: TestClient, test_user: UserORM):
        """Test successful login"""
        login_data = {
            "username": test_user.email,  # OAuth2 uses 'username' field
            "password": "testpassword123",
        }

        response = client.post("/users/login", data=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    def test_login_wrong_password(self, client: TestClient, test_user: UserORM):
        """Test login with incorrect password"""
        login_data = {"username": test_user.email, "password": "wrongpassword"}

        response = client.post("/users/login", data=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user"""
        login_data = {"username": "nonexistent@example.com", "password": "somepassword"}

        response = client.post("/users/login", data=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_missing_credentials(self, client: TestClient):
        """Test login with missing credentials"""
        response = client.post("/users/login", data={})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_login_empty_password(self, client: TestClient, test_user: UserORM):
        """Test login with empty password"""
        login_data = {"username": test_user.email, "password": ""}

        response = client.post("/users/login", data=login_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.integration
class TestUserProfile:
    """Test user profile endpoint"""

    def test_get_current_user_profile(
        self, client: TestClient, auth_headers: dict, test_user: UserORM
    ):
        """Test retrieving current user profile with valid token"""
        response = client.get("/users/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["id"] == test_user.id
        assert "hashed_password" not in data

    def test_get_profile_without_auth(self, client: TestClient):
        """Test retrieving profile without authentication fails"""
        response = client.get("/users/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_profile_with_invalid_token(self, client: TestClient):
        """Test retrieving profile with invalid token"""
        headers = {"Authorization": "Bearer invalidtoken"}
        response = client.get("/users/me", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_profile_with_expired_token(self, client: TestClient):
        """Test retrieving profile with malformed bearer token"""
        headers = {"Authorization": "Bearer"}
        response = client.get("/users/me", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_profile_admin_user(
        self, client: TestClient, admin_auth_headers: dict, admin_user: UserORM
    ):
        """Test retrieving admin user profile"""
        response = client.get("/users/me", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == admin_user.email
        assert data["id"] == admin_user.id
