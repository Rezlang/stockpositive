import pytest
from datetime import timedelta
from jose import jwt
from services.authService.authService import (
    verify_password,
    get_password_hash,
    create_access_token,
    SECRET_KEY,
    ALGORITHM
)


@pytest.mark.unit
class TestPasswordHashing:
    """Test password hashing and verification"""

    def test_get_password_hash_returns_string(self):
        """Test that password hashing returns a string"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_get_password_hash_different_for_same_password(self):
        """Test that hashing same password twice produces different hashes (due to salt)"""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2

    def test_verify_password_with_correct_password(self):
        """Test password verification with correct password"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_with_incorrect_password(self):
        """Test password verification with incorrect password"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_password(self):
        """Test password verification with empty password"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert verify_password("", hashed) is False


@pytest.mark.unit
class TestAccessToken:
    """Test JWT access token creation and validation"""

    def test_create_access_token_returns_string(self):
        """Test that token creation returns a string"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_contains_correct_data(self):
        """Test that created token contains the correct data"""
        email = "test@example.com"
        data = {"sub": email}
        token = create_access_token(data)

        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == email
        assert "exp" in decoded

    def test_create_access_token_with_custom_expiry(self):
        """Test token creation with custom expiration time"""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta=expires_delta)

        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in decoded

    def test_create_access_token_with_additional_claims(self):
        """Test token creation with additional claims"""
        data = {
            "sub": "test@example.com",
            "role": "admin",
            "permissions": ["read", "write"]
        }
        token = create_access_token(data)

        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == "test@example.com"
        assert decoded["role"] == "admin"
        assert decoded["permissions"] == ["read", "write"]

    def test_token_different_for_same_data(self):
        """Test that creating token twice with same data produces different tokens (due to timestamp)"""
        import time
        data = {"sub": "test@example.com"}

        token1 = create_access_token(data)
        time.sleep(1)  # Wait a second to ensure different timestamp
        token2 = create_access_token(data)

        # Tokens should be different due to different exp times
        assert token1 != token2
