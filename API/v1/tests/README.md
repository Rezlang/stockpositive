# Testing Module

Comprehensive testing suite for the StockPositive API v1.

## Overview

This testing module provides full coverage for the API including:
- Unit tests for core services
- Integration tests for API endpoints
- Test fixtures and utilities
- Mocking and database setup

## Project Structure

```
tests/
├── conftest.py                    # Pytest fixtures and configuration
├── unit/                          # Unit tests
│   ├── test_auth_service.py      # Authentication service tests
│   └── test_permission_checkers.py # Permission checker tests
├── integration/                   # Integration tests
│   ├── test_user_routes.py       # User endpoint tests
│   ├── test_feed_routes.py       # Feed endpoint tests
│   └── test_news_routes.py       # News endpoint tests
└── utils/                         # Test utilities
    └── helpers.py                 # Helper functions
```

## Setup

### Prerequisites

**PostgreSQL Database Required**: This project uses PostgreSQL-specific features (like ARRAY columns), so you need a PostgreSQL test database.

1. **Install PostgreSQL** (if not already installed):
   ```bash
   # macOS
   brew install postgresql
   brew services start postgresql

   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   sudo service postgresql start
   ```

2. **Create a test database**:
   ```bash
   # Connect to PostgreSQL
   psql postgres

   # Create test database
   CREATE DATABASE stockpositive_test;

   # Create user (if needed)
   CREATE USER postgres WITH PASSWORD 'postgres';
   GRANT ALL PRIVILEGES ON DATABASE stockpositive_test TO postgres;

   # Exit
   \q
   ```

3. **Install testing dependencies**:
   ```bash
   pip install pytest pytest-asyncio httpx pytest-cov
   ```

All dependencies are already included in the main `requirements.txt` file.

### Environment Variables

Configure your test database connection (optional - defaults shown below):

```bash
export TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:5432/stockpositive_test"
```

Also ensure you have a `.env` file configured with:
- `JWT_KEY`: Secret key for JWT tokens
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)

For testing, you can use test-specific values that don't need to match production.

## Running Tests

### Run All Tests

```bash
cd API/v1
pytest
```

### Run Specific Test Categories

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests for a specific module
pytest tests/unit/test_auth_service.py

# Run a specific test class
pytest tests/integration/test_user_routes.py::TestUserRegistration

# Run a specific test
pytest tests/unit/test_auth_service.py::TestPasswordHashing::test_verify_password_with_correct_password
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Coverage Report

```bash
pytest --cov=. --cov-report=html
```

### Skip Slow Tests

```bash
pytest -m "not slow"
```

## Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (API endpoints)
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.requires_db` - Tests requiring database connection

## Fixtures

### Database Fixtures

- `engine` - SQLite in-memory database engine
- `session` - Database session for tests
- `client` - FastAPI test client with database override

### User Fixtures

- `test_user` - Standard user with basic permissions
- `admin_user` - Admin user with full permissions
- `auth_headers` - Authentication headers for test user
- `admin_auth_headers` - Authentication headers for admin user

### Data Fixtures

- `test_feed` - Sample feed for testing

### Example Usage

```python
def test_example(client: TestClient, auth_headers: dict, test_user: UserORM):
    response = client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == test_user.email
```

## Writing New Tests

### Unit Test Example

```python
import pytest
from services.my_service import my_function

@pytest.mark.unit
class TestMyService:
    def test_my_function_success(self):
        result = my_function("input")
        assert result == "expected_output"

    def test_my_function_error(self):
        with pytest.raises(ValueError):
            my_function("invalid_input")
```

### Integration Test Example

```python
import pytest
from fastapi import status

@pytest.mark.integration
class TestMyEndpoint:
    def test_endpoint_success(self, client, auth_headers):
        response = client.get("/my-endpoint", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert "expected_field" in response.json()

    def test_endpoint_unauthorized(self, client):
        response = client.get("/my-endpoint")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

## Test Utilities

The `tests/utils/helpers.py` module provides helpful functions:

### create_user_with_permissions
Create a user with specific permissions for testing.

```python
from tests.utils.helpers import create_user_with_permissions

user = create_user_with_permissions(
    session,
    "test@example.com",
    "password123",
    [
        {"name": "GET.NEWS"},
        {"name": "ADD.FEED", "max_value": 10}
    ]
)
```

### create_test_feed
Create a test feed for a user.

```python
from tests.utils.helpers import create_test_feed

feed = create_test_feed(
    session,
    owner=test_user,
    feedname="My Feed",
    stocks=["AAPL", "GOOGL"],
    sources=["market"]
)
```

### get_auth_headers
Generate authentication headers for any user.

```python
from tests.utils.helpers import get_auth_headers

headers = get_auth_headers(my_user)
response = client.get("/protected-endpoint", headers=headers)
```

## Mocking External Services

For tests that interact with external services (like news retrieval), use mocking:

```python
from unittest.mock import patch

@patch('routes.newsRoutes.retrieve_news')
def test_load_news(mock_retrieve, client, admin_auth_headers):
    mock_retrieve.return_value = [mock_article]
    response = client.get("/news/load-news", headers=admin_auth_headers)
    assert response.status_code == 200
```

## Database Testing

Tests use a PostgreSQL test database that is:
- Created fresh for each test (tables are created and dropped)
- Isolated from production data
- Fully compatible with PostgreSQL-specific features (ARRAY types, etc.)
- Automatically cleaned up after each test

The database schema is identical to production, ensuring tests accurately reflect real behavior.

**Important**: Make sure the `stockpositive_test` database exists before running tests. The test suite will create and drop tables automatically, but the database itself must exist.

## Best Practices

1. **Isolation**: Each test should be independent and not rely on other tests
2. **Clarity**: Use descriptive test names that explain what is being tested
3. **Coverage**: Test both success cases and error cases
4. **Fixtures**: Use fixtures to avoid code duplication
5. **Mocking**: Mock external services to keep tests fast and reliable
6. **Assertions**: Make specific assertions about expected behavior
7. **Cleanup**: Tests automatically clean up, but avoid side effects when possible

## Continuous Integration

These tests are designed to run in CI/CD pipelines. They:
- Run without external dependencies
- Use in-memory database
- Complete quickly
- Provide clear failure messages

## Troubleshooting

### Import Errors

If you encounter import errors, ensure you're running pytest from the `API/v1` directory:

```bash
cd API/v1
pytest
```

### Database Errors

If you see database-related errors, check that:
- SQLModel is properly installed
- All ORM models are imported in `conftest.py`
- The in-memory database is being created correctly

### Authentication Errors

For authentication test failures:
- Verify `JWT_KEY` is set in environment variables
- Check that password hashing is working correctly
- Ensure tokens are being generated with correct format

## Contributing

When adding new features:

1. Write unit tests for new service functions
2. Write integration tests for new endpoints
3. Update fixtures if new test data is needed
4. Add test utilities for common operations
5. Update this README with new patterns or utilities

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLModel Testing](https://sqlmodel.tiangolo.com/tutorial/testing/)
