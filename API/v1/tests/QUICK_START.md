# Testing Quick Start Guide

## Prerequisites

**PostgreSQL Required**: Tests use a PostgreSQL database (not SQLite) due to ARRAY column types.

## Quick Setup

```bash
# 1. Create test database (one-time setup)
createdb stockpositive_test

# 2. Optional: Set custom database URL
export TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:5432/stockpositive_test"

# 3. Install dependencies
cd API/v1
pip install -r requirements.txt
```

## Run Tests

### All tests
```bash
pytest
```

### With verbose output
```bash
pytest -v
```

### Only unit tests (fast)
```bash
pytest -m unit
```

### Only integration tests
```bash
pytest -m integration
```

### Specific test file
```bash
pytest tests/unit/test_auth_service.py
```

### With coverage report
```bash
pytest --cov=. --cov-report=term-missing
```

## Common Test Commands

| Command | Description |
|---------|-------------|
| `pytest` | Run all tests |
| `pytest -v` | Verbose output |
| `pytest -x` | Stop on first failure |
| `pytest -k "test_name"` | Run tests matching pattern |
| `pytest --lf` | Run last failed tests |
| `pytest --ff` | Run failures first |
| `pytest -m unit` | Run only unit tests |
| `pytest -m integration` | Run only integration tests |
| `pytest --cov` | Run with coverage report |

## Test Structure

```
tests/
├── conftest.py              # Fixtures (users, database, auth)
├── pytest.ini               # Pytest configuration
├── unit/                    # Unit tests (fast, isolated)
│   ├── test_auth_service.py
│   └── test_permission_checkers.py
├── integration/             # API endpoint tests
│   ├── test_user_routes.py
│   ├── test_feed_routes.py
│   └── test_news_routes.py
└── utils/
    └── helpers.py           # Test helper functions
```

## Available Fixtures

- `client` - FastAPI test client
- `session` - Database session
- `test_user` - User with basic permissions
- `admin_user` - User with admin permissions
- `auth_headers` - Auth headers for test user
- `admin_auth_headers` - Auth headers for admin
- `test_feed` - Sample feed

## Writing Your First Test

```python
import pytest
from fastapi import status

@pytest.mark.integration
class TestMyFeature:
    def test_endpoint_success(self, client, auth_headers):
        response = client.get("/my-endpoint", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_endpoint_unauthorized(self, client):
        response = client.get("/my-endpoint")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

## Next Steps

Read the full [README.md](README.md) for detailed documentation on:
- Fixtures and utilities
- Mocking external services
- Best practices
- Troubleshooting
