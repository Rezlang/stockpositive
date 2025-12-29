# Configuration

This document describes how to configure the StockPositive v1 API for different environments.

## Environment Variables

All sensitive configuration is stored in environment variables via a `.env` file located in the `API/` directory.

### Required Variables

#### External API Keys

```env
# Google Gemini AI API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Mistral AI API Key
MISTRAL_API_KEY=your_mistral_api_key_here

# TwelveData Stock Data API Key
TWELVEDATA_KEY=your_twelvedata_api_key_here

# NewsData.io News API Key
NEWSDATA_API_KEY=your_newsdata_api_key_here
```

**How to obtain**:
- **Google Gemini**: [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Mistral AI**: [Mistral AI Console](https://console.mistral.ai/)
- **TwelveData**: [TwelveData](https://twelvedata.com/)
- **NewsData.io**: [NewsData.io](https://newsdata.io/)

#### Database Configuration

```env
# PostgreSQL connection string
# Format: postgresql://username:password@host:port/database_name
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/stockpositive
```

**Components**:
- `username`: PostgreSQL user (default: `postgres`)
- `password`: PostgreSQL password
- `host`: Database server host (default: `localhost`)
- `port`: PostgreSQL port (default: `5432`)
- `database_name`: Database name (default: `stockpositive`)

#### JWT Authentication

```env
# Secret key for signing JWT tokens (use a strong random string)
JWT_KEY=your_secret_jwt_key_here_min_32_chars

# JWT algorithm (optional, default: HS256)
ALGORITHM=HS256

# JWT token expiration in minutes (optional, default: 30)
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Generating a secure JWT_KEY**:
```bash
# Generate a random 32-byte key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Optional Variables

These variables have defaults and can be omitted:

```env
# JWT algorithm (default: HS256)
ALGORITHM=HS256

# Access token expiration time in minutes (default: 30)
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Example `.env` File

```env
# External APIs
GEMINI_API_KEY=AIzaSy...
MISTRAL_API_KEY=msk_...
TWELVEDATA_KEY=abc123...
NEWSDATA_API_KEY=pub_...

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/stockpositive

# JWT
JWT_KEY=your-secret-key-at-least-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Configuration Loading

### Environment File Location

The `.env` file is loaded from the `API/` directory:

**Location**: `API/.env` (relative to project root)

### Loading Process

Configuration is loaded using `python-dotenv`:

```python
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()  # Load from current directory
env_path = Path('../') / '.env'  # Also check parent directory
load_dotenv(dotenv_path=env_path)

# Access variables
SECRET_KEY = os.getenv("JWT_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")  # Default if not set
```

**Implementation**: `services/authService/authService.py`

### Validation

Critical environment variables are validated on startup:

```python
if not SECRET_KEY:
    raise ValueError("SECRET_KEY must be set in environment variables")
```

This ensures the application won't start with missing critical configuration.

## Database Configuration

### PostgreSQL Setup

#### Installation

**macOS**:
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows**:
Download and install from [PostgreSQL official site](https://www.postgresql.org/download/windows/)

#### Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE stockpositive;

# Create user (optional)
CREATE USER stockapp WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE stockpositive TO stockapp;

# Exit
\q
```

#### Connection String Format

```
postgresql://[user]:[password]@[host]:[port]/[database]?[parameters]
```

Examples:
```env
# Local development
DATABASE_URL=postgresql://postgres:password@localhost:5432/stockpositive

# With custom user
DATABASE_URL=postgresql://stockapp:mypassword@localhost:5432/stockpositive

# Remote database
DATABASE_URL=postgresql://user:pass@db.example.com:5432/stockpositive

# With SSL
DATABASE_URL=postgresql://user:pass@db.example.com:5432/stockpositive?sslmode=require
```

### Database Initialization

After configuring the database connection, initialize the schema:

```bash
cd DB
python rebuild_db.py
```

This script:
1. Drops existing database (if it exists)
2. Creates new database
3. Executes all SQL scripts from `DB/Scripts/` in order
4. Inserts initial data from `DB/Insert/`

**WARNING**: This destroys all existing data. Use only for development or initial setup.

### Connection Pooling

SQLAlchemy handles connection pooling automatically:

```python
# services/dbService/database.py
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

**Default pool settings**:
- Pool size: 5 connections
- Max overflow: 10 connections
- Pool recycle: 3600 seconds

To customize:
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600
)
```

## ChromaDB Configuration

**Location**: `API/chroma_db/`

ChromaDB stores vector embeddings for AI-powered features.

**Note**: ChromaDB configuration details are not fully specified in the current codebase. Default configuration is used.

**Typical usage**:
```python
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("news_embeddings")
```

## CORS Configuration

Configure CORS middleware in `main.py` for cross-origin requests from mobile apps:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production recommendation**:
```python
allow_origins=[
    "https://yourmobileapp.com",
    "https://app.yourdomain.com"
]
```

## Development vs Production

### Development Configuration

```env
# Development
DATABASE_URL=postgresql://postgres:dev_password@localhost:5432/stockpositive_dev
JWT_KEY=development-key-not-for-production
ACCESS_TOKEN_EXPIRE_MINUTES=60  # Longer for development
```

```python
# main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

### Production Configuration

```env
# Production
DATABASE_URL=postgresql://stockapp:strong_password@prod-db.internal:5432/stockpositive
JWT_KEY=very-long-random-production-secret-key-min-64-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
```

```bash
# Use gunicorn or uvicorn workers
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Production checklist**:
- [ ] Use strong, random JWT_KEY (64+ characters)
- [ ] Restrict CORS origins to known domains
- [ ] Use HTTPS for all connections
- [ ] Set appropriate token expiration times
- [ ] Use environment-specific database credentials
- [ ] Enable database SSL connections
- [ ] Configure proper logging
- [ ] Set up monitoring and error tracking

## API Server Configuration

### Running the Server

**Development** (with auto-reload):
```bash
cd API/v1
uvicorn main:app --reload
```

**Production**:
```bash
cd API/v1
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Server Options

```bash
uvicorn main:app \
  --host 0.0.0.0 \        # Bind to all interfaces
  --port 8000 \           # Port number
  --reload \              # Auto-reload on code changes (dev only)
  --workers 4 \           # Number of worker processes (prod)
  --log-level info \      # Logging level
  --access-log            # Enable access logging
```

### Environment-Specific Settings

Create separate `.env` files:

```
API/
├── .env                 # Development (default)
├── .env.production      # Production
├── .env.staging         # Staging
└── .env.test            # Testing
```

Load specific environment:
```bash
# Development (default)
python main.py

# Production
ENV_FILE=.env.production python main.py

# Staging
ENV_FILE=.env.staging python main.py
```

## Secrets Management

### Development
- Store secrets in `.env` file
- **Never** commit `.env` to git
- Share `.env.example` with placeholder values

### Production
Consider using a secrets management service:
- **AWS Secrets Manager**
- **HashiCorp Vault**
- **Azure Key Vault**
- **Google Secret Manager**

Example with AWS Secrets Manager:
```python
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

secrets = get_secret('stockpositive/production')
DATABASE_URL = secrets['DATABASE_URL']
JWT_KEY = secrets['JWT_KEY']
```

## Configuration Best Practices

1. **Never hardcode secrets** in source code
2. **Use strong random keys** for JWT (64+ characters)
3. **Rotate API keys** regularly
4. **Use different credentials** for each environment
5. **Validate configuration** on startup
6. **Document all variables** in `.env.example`
7. **Use SSL/TLS** for database connections in production
8. **Limit token expiration** to minimize security risk
9. **Monitor API key usage** to detect unauthorized access
10. **Backup database** regularly

## `.env.example` Template

Create `API/.env.example` with placeholder values:

```env
# External API Keys
GEMINI_API_KEY=your_gemini_api_key
MISTRAL_API_KEY=your_mistral_api_key
TWELVEDATA_KEY=your_twelvedata_key
NEWSDATA_API_KEY=your_newsdata_key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/stockpositive

# JWT Authentication
JWT_KEY=your_secret_jwt_key_min_32_chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Troubleshooting

### Database Connection Issues

**Error**: `could not connect to server`
- Ensure PostgreSQL is running: `pg_ctl status` or `brew services list`
- Check database URL format
- Verify database exists: `psql -U postgres -l`

**Error**: `FATAL: password authentication failed`
- Check username and password in DATABASE_URL
- Reset password: `ALTER USER postgres PASSWORD 'newpassword';`

### Missing Environment Variables

**Error**: `ValueError: SECRET_KEY must be set`
- Create `.env` file in `API/` directory
- Add required variables
- Restart the application

### API Key Issues

**Error**: `401 Unauthorized` from external APIs
- Verify API key is correct and active
- Check API key has sufficient quota/credits
- Ensure API key is not expired

### Port Already in Use

**Error**: `Address already in use`
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn main:app --port 8001
```
