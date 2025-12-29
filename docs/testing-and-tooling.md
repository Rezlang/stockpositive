# Testing and Tooling

This document describes the development tools, testing frameworks, and workflows for the StockPositive v1 API.

## Testing

### Test Framework

**Framework**: pytest with pytest-playwright

**Test Location**: `API/v1/test/`

**Current State**: Limited test coverage. Main test file is `httpTest.py`.

### Running Tests

```bash
cd API/v1
pytest
```

**Run specific test file**:
```bash
pytest test/httpTest.py
```

**Run with verbose output**:
```bash
pytest -v
```

**Run with coverage**:
```bash
pytest --cov=. --cov-report=html
```

### Test Structure

Tests are organized in the `test/` directory:

```
test/
├── httpTest.py          # HTTP endpoint tests
├── test_auth.py         # Authentication tests (add)
├── test_permissions.py  # Permission system tests (add)
└── test_feeds.py        # Feed CRUD tests (add)
```

### Writing Tests

Example test structure:

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_register_user():
    response = client.post(
        "/users/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 201
    assert "id" in response.json()

def test_login():
    response = client.post(
        "/users/login",
        data={
            "username": "test@example.com",  # OAuth2 uses 'username' field
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### Test Database

For testing, use a separate test database:

```env
# .env.test
DATABASE_URL=postgresql://postgres:password@localhost:5432/stockpositive_test
```

**Setup test database**:
```bash
psql -U postgres -c "CREATE DATABASE stockpositive_test;"
cd DB
DATABASE_URL=postgresql://postgres:password@localhost:5432/stockpositive_test python rebuild_db.py
```

### Pytest Fixtures

Create reusable fixtures for common test setup:

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    # Register and login
    client.post("/users/register", json={
        "username": "testuser",
        "email": "test@test.com",
        "password": "test123"
    })
    response = client.post("/users/login", data={
        "username": "test@test.com",
        "password": "test123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_user(client):
    response = client.post("/users/register", json={
        "username": "testuser",
        "email": "test@test.com",
        "password": "test123"
    })
    return response.json()
```

## Development Tools

### Package Management

**Tool**: pip with `requirements.txt`

**Install dependencies**:
```bash
cd API/v1
pip install -r requirements.txt
```

**Add new dependency**:
```bash
pip install package_name
pip freeze > requirements.txt  # Update requirements
```

**Virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Interactive API Documentation

FastAPI provides automatic interactive API documentation:

#### Swagger UI
**URL**: [http://localhost:8000/docs](http://localhost:8000/docs)

Features:
- Try out endpoints directly in the browser
- View request/response schemas
- Test authentication
- See all available endpoints

#### ReDoc
**URL**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

Features:
- Alternative documentation UI
- Better for reading and exploring
- Clean, organized layout

### Development Server

**Tool**: Uvicorn (ASGI server)

**Start server with auto-reload**:
```bash
cd API/v1
uvicorn main:app --reload
```

**Server options**:
```bash
uvicorn main:app \
  --reload \              # Auto-reload on code changes
  --host 0.0.0.0 \       # Bind to all interfaces
  --port 8000 \          # Port number
  --log-level debug      # Logging verbosity
```

**Alternative**: Using Python directly
```python
# main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

Then:
```bash
python main.py
```

### Database Tools

#### SQLAlchemy

**Purpose**: ORM for database operations

**Key features**:
- Object-relational mapping
- Database migrations (via Alembic, though not actively used)
- Query building
- Connection pooling

**Usage**: All database operations use SQLAlchemy/SQLModel

#### SQL Scripts

**Purpose**: Database schema management

**Location**: `DB/Scripts/`

**Execution**:
```bash
cd DB
python rebuild_db.py  # Executes all scripts in order
```

**Manual execution**:
```bash
psql -U postgres -d stockpositive -f Scripts/01_usergroups.sql
psql -U postgres -d stockpositive -f Scripts/02_permissions.sql
# ... etc
```

#### psql (PostgreSQL CLI)

**Connect to database**:
```bash
psql -U postgres -d stockpositive
```

**Useful commands**:
```sql
-- List tables
\dt

-- Describe table
\d users

-- View all users
SELECT * FROM users;

-- View permissions
SELECT * FROM permissions;

-- Check user permissions
SELECT u.email, ug.name as usergroup, p.name as permission, ugp.permission_value
FROM users u
JOIN usergroups ug ON u.usergroup_id = ug.id
JOIN usergroup_permissions ugp ON ug.id = ugp.usergroup_id
JOIN permissions p ON ugp.permission_id = p.id
WHERE u.email = 'test@example.com';

-- Exit
\q
```

### Security Tools

#### passlib[bcrypt]

**Purpose**: Password hashing

**Usage**:
```python
import bcrypt

# Hash password
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

# Verify password
bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
```

#### python-jose[cryptography]

**Purpose**: JWT token creation and validation

**Usage**:
```python
from jose import jwt

# Create token
token = jwt.encode({"sub": "user@example.com"}, SECRET_KEY, algorithm="HS256")

# Decode token
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
```

### Development Workflow

1. **Start database**:
   ```bash
   brew services start postgresql  # macOS
   sudo systemctl start postgresql # Linux
   ```

2. **Activate virtual environment**:
   ```bash
   source venv/bin/activate
   ```

3. **Start development server**:
   ```bash
   cd API/v1
   uvicorn main:app --reload
   ```

4. **Test endpoints**:
   - Open [http://localhost:8000/docs](http://localhost:8000/docs)
   - Use Swagger UI to test endpoints
   - Or use curl/Postman

5. **Make changes**:
   - Edit code
   - Server auto-reloads
   - Test in browser

6. **Run tests**:
   ```bash
   pytest
   ```

## Database Migrations

**Tool**: Alembic (installed but not actively used)

**Current approach**: SQL scripts in `DB/Scripts/`

**Why SQL scripts**:
- Simpler for small projects
- Full control over schema
- Easy to review changes
- Clear execution order

**To use Alembic** (optional):

1. **Initialize Alembic**:
   ```bash
   cd API/v1
   alembic init alembic
   ```

2. **Configure**:
   Edit `alembic/env.py` to use your database URL

3. **Create migration**:
   ```bash
   alembic revision --autogenerate -m "Add new table"
   ```

4. **Apply migration**:
   ```bash
   alembic upgrade head
   ```

## Linting and Code Quality

**Note**: No linting configuration is currently in place.

**Recommended tools**:

### Black (Code Formatter)
```bash
pip install black
black API/v1/
```

### flake8 (Linter)
```bash
pip install flake8
flake8 API/v1/
```

### mypy (Type Checker)
```bash
pip install mypy
mypy API/v1/
```

### Configuration

Create `pyproject.toml`:
```toml
[tool.black]
line-length = 100
target-version = ['py310']

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false

[tool.pytest.ini_options]
testpaths = ["test"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

## CI/CD

**Current state**: No CI/CD pipeline configured

**Recommended setup**:

### GitHub Actions

Create `.github/workflows/test.yml`:
```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        cd API/v1
        pip install -r requirements.txt

    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
      run: |
        cd API/v1
        pytest
```

## Debugging

### Python Debugger (pdb)

Add breakpoints in code:
```python
import pdb; pdb.set_trace()
```

Or use debugpy for VS Code:
```python
import debugpy
debugpy.listen(5678)
debugpy.wait_for_client()
```

### Logging

Add logging for debugging:
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

### Print Debugging

Current approach uses print statements:
```python
print("Permissions:", current_user.permissions)
```

**Recommendation**: Replace with proper logging in production.

## Performance Testing

### Load Testing with Locust

Install:
```bash
pip install locust
```

Create `locustfile.py`:
```python
from locust import HttpUser, task, between

class StockPositiveUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Login
        response = self.client.post("/users/login", data={
            "username": "test@example.com",
            "password": "password"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task
    def get_feeds(self):
        self.client.get("/feeds/get_feeds", headers=self.headers)

    @task(3)
    def get_news(self):
        self.client.get("/news/get-news?feedId=1", headers=self.headers)
```

Run:
```bash
locust -f locustfile.py
```

Open [http://localhost:8089](http://localhost:8089) to configure and run load tests.

## Development Best Practices

1. **Use virtual environments** to isolate dependencies
2. **Run tests before committing** code
3. **Use auto-reload** during development
4. **Check API docs** for endpoint behavior
5. **Use separate test database** to avoid data corruption
6. **Write tests for new features**
7. **Use type hints** for better IDE support
8. **Document complex logic** with comments
9. **Review SQL scripts** before execution
10. **Keep requirements.txt** up to date

## Useful Commands Reference

```bash
# Development server
uvicorn main:app --reload

# Run tests
pytest
pytest -v  # Verbose
pytest --cov  # With coverage

# Database
psql -U postgres -d stockpositive  # Connect to DB
python DB/rebuild_db.py  # Rebuild database

# Dependencies
pip install -r requirements.txt  # Install
pip freeze > requirements.txt  # Update

# Virtual environment
python -m venv venv  # Create
source venv/bin/activate  # Activate (Linux/macOS)
venv\Scripts\activate  # Activate (Windows)
deactivate  # Deactivate
```
