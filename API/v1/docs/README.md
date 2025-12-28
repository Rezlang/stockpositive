# StockPositive v1 API

A financial news aggregation and stock monitoring REST API built with FastAPI and PostgreSQL.

## Overview

StockPositive v1 provides a backend API for:
- **Personalized News Feeds**: Aggregate financial news from multiple sources based on user-selected stocks and sources
- **Stock Monitoring**: Track stock prices and market data using TwelveData and Yahoo Finance APIs
- **Role-Based Access Control (RBAC)**: Fine-grained permission system with user groups and value-based permissions
- **AI-Powered Summarization**: News article analysis and summarization using Google Gemini and Mistral AI
- **User Management**: Secure authentication with JWT tokens

## Architecture

```
React Native Mobile App
          ↓
    FastAPI REST API (v1)
          ↓
┌─────────┴─────────┐
│                   │
PostgreSQL      ChromaDB
   (Data)      (Vectors)
          ↓
External APIs:
- NewsData.io (News)
- TwelveData (Stock Data)
- yfinance (Stock Data)
- Google Gemini AI
- Mistral AI
```

## Technology Stack

- **Framework**: FastAPI 0.126.0+
- **Database**: PostgreSQL with SQLAlchemy 2.0.45+
- **ORM**: SQLModel 0.0.27+
- **Vector DB**: ChromaDB 1.3.5+ for embeddings
- **Authentication**: JWT with python-jose and passlib[bcrypt]
- **External APIs**:
  - NewsData.io for financial news
  - TwelveData 1.2.25+ for stock data
  - yfinance 0.2.66+ for stock data
  - Google Generative AI (Gemini) for AI processing
  - Mistral AI 1.9.11+ for AI processing

## Prerequisites

- Python 3.10+
- PostgreSQL 13+ (running and accessible)
- API keys for external services:
  - NewsData.io API key
  - TwelveData API key
  - Google Gemini API key
  - Mistral AI API key

## Quick Start

### 1. Install Dependencies

```bash
cd API/v1
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the `API/` directory:

```env
# External API Keys
GEMINI_API_KEY=your_gemini_api_key
MISTRAL_API_KEY=your_mistral_api_key
TWELVEDATA_KEY=your_twelvedata_api_key
NEWSDATA_API_KEY=your_newsdata_api_key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/stockpositive

# JWT Authentication
JWT_KEY=your_secret_jwt_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Initialize Database

```bash
cd ../../DB
python rebuild_db.py
```

This script will:
- Drop and recreate the database
- Execute all SQL schema files from `DB/Scripts/`
- Insert initial data from `DB/Insert/`
- Create default user groups and permissions

### 4. Run the API

```bash
cd ../API/v1
uvicorn main:app --reload
```

The API will be available at:
- API: [http://localhost:8000](http://localhost:8000)
- Interactive Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## API Endpoints

### Authentication
- `POST /users/register` - Register a new user
- `POST /users/login` - Login and receive JWT token
- `GET /users/me` - Get current user profile (requires authentication)

### News
- `GET /news/load-news` - Load market news from external sources (requires `LOAD.NEWS` permission)
- `GET /news/get-news` - Get news for a specific feed (requires `GET.NEWS` permission)

### Feeds
- `POST /feeds/add_feed` - Create a new feed (requires `ADD.FEED` permission)
- `GET /feeds/get_feeds` - Get user's feeds (requires `GET.FEEDS` permission)
- `PUT /feeds/edit_feed/{feed_id}` - Edit a feed (requires `EDIT.FEED` permission)
- `DELETE /feeds/delete_feed/{feed_id}` - Delete a feed (requires `DELETE.FEED` permission)
- `GET /feeds/get_all_feeds` - Get all feeds (admin only, requires `ADMIN.GET.FEEDS` permission)

## Documentation

### Core Documentation
- [Architecture](architecture.md) - System architecture and design
- [Structure](structure.md) - Project layout and organization
- [Conventions](conventions.md) - Code style and naming patterns
- [Configuration](configuration.md) - Environment setup and configuration
- [Testing and Tooling](testing-and-tooling.md) - Development tools and testing

### Backend Documentation
- [Backend Overview](backend/overview.md) - Backend architecture and patterns
- [API Reference](backend/api.md) - Complete API endpoint documentation
- [Data Layer](backend/data.md) - Database schema and ORM models
- [Extending the Backend](backend/extending.md) - How to add new features

### Mobile Documentation
- [Mobile Overview](mobile/overview.md) - React Native app architecture
- [Setup](mobile/setup.md) - React Native project setup
- [Authentication](mobile/authentication.md) - JWT authentication implementation
- [API Integration](mobile/api-integration.md) - Connecting to the backend
- [State Management](mobile/state-management.md) - State management best practices
- [UI Components](mobile/ui-components.md) - Component architecture
- [Navigation](mobile/navigation.md) - React Navigation patterns
- [Extending the Mobile App](mobile/extending.md) - How to add new features

## Project Structure

```
API/v1/
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
├── models/              # Pydantic request/response models
├── ORM/                 # SQLAlchemy database models
├── routes/              # API endpoint routers
│   ├── userRoutes.py
│   ├── newsRoutes.py
│   └── feedRoutes.py
├── services/            # Business logic
│   ├── authService/    # Authentication and permissions
│   ├── dbService/      # Database operations
│   └── retrieveNews.py # External API integration
└── test/                # Test files

DB/
├── Scripts/             # SQL schema creation scripts
├── Insert/              # SQL data insertion scripts
├── order.txt            # Execution order for scripts
└── rebuild_db.py        # Database initialization script
```

## Development

### Running Tests

```bash
cd API/v1
pytest
```

### Interactive API Documentation

FastAPI provides automatic interactive API documentation:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Database Management

To rebuild the database (WARNING: This will delete all data):

```bash
cd DB
python rebuild_db.py
```

## Security

- All passwords are hashed using bcrypt
- JWT tokens are signed with HS256 algorithm
- Sensitive API keys are stored in environment variables
- Role-based access control (RBAC) enforces permissions on all protected endpoints

## License

[Your License Here]

## Support

For issues, questions, or contributions, please refer to the project repository.
