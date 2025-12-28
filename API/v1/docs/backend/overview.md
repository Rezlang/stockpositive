# Backend Overview

This document provides an overview of the StockPositive v1 backend architecture and implementation patterns.

## Purpose

The StockPositive v1 backend is a RESTful API that provides:
- **User authentication and authorization** with JWT tokens
- **Role-based access control (RBAC)** with value-based permissions
- **News aggregation** from external financial news APIs
- **Stock data retrieval** from market data providers
- **User feed management** for personalized news and stock tracking
- **AI-powered features** using Google Gemini and Mistral AI

## Technology Stack

### Framework
**FastAPI** - Modern, fast web framework for building APIs with Python 3.10+

Features used:
- Automatic OpenAPI documentation
- Pydantic data validation
- Dependency injection
- OAuth2 with JWT authentication
- Type hints and auto-completion

### Database
**PostgreSQL** - Relational database for persistent data storage
**SQLAlchemy/SQLModel** - ORM for database operations
**ChromaDB** - Vector database for AI embeddings (limited usage)

### External Services
- **NewsData.io** - Financial news aggregation
- **TwelveData** - Stock market data
- **yfinance** - Yahoo Finance stock data
- **Google Gemini AI** - Text summarization and analysis
- **Mistral AI** - Alternative AI processing

## Application Structure

### Entry Point

**File**: `main.py`

```python
from fastapi import FastAPI
from routes import newsRoutes, userRoutes, feedRoutes

app = FastAPI()

app.include_router(newsRoutes.router, prefix="/news", tags=["news"])
app.include_router(userRoutes.router, prefix="/users", tags=["users"])
app.include_router(feedRoutes.router, prefix="/feeds", tags=["feeds"])
```

The application is minimal and focused - routers are registered with prefixes and tags for organized API documentation.

## Router Organization

The API is organized into three main routers:

### 1. News Router (`/news/*`)

**File**: `routes/newsRoutes.py`

**Endpoints**:
- `GET /news/load-news` - Load news from external sources
- `GET /news/get-news` - Get news for a specific feed

**Permissions**:
- `LOAD.NEWS` - Required to load news from external APIs
- `GET.NEWS` - Required to retrieve news for feeds

**Responsibilities**:
- Call external news APIs (NewsData.io)
- Store news articles in database
- Filter news by feed configuration (stocks, sources)

### 2. User Router (`/users/*`)

**File**: `routes/userRoutes.py`

**Endpoints**:
- `POST /users/register` - Create new user account
- `POST /users/login` - Authenticate and receive JWT token
- `GET /users/me` - Get current user profile

**Permissions**:
- No permissions required for registration
- No permissions required for login
- Authentication required for `/me`

**Responsibilities**:
- User registration with password hashing
- JWT token generation on login
- Current user retrieval

### 3. Feed Router (`/feeds/*`)

**File**: `routes/feedRoutes.py`

**Endpoints**:
- `POST /feeds/add_feed` - Create new feed
- `GET /feeds/get_feeds` - Get user's feeds
- `PUT /feeds/edit_feed/{feed_id}` - Update feed
- `DELETE /feeds/delete_feed/{feed_id}` - Delete feed
- `GET /feeds/get_all_feeds` - Get all feeds (admin only)

**Permissions**:
- `ADD.FEED` - Create feed (with value check for max feeds)
- `GET.FEEDS` - Retrieve user's feeds
- `EDIT.FEED` - Update existing feed
- `DELETE.FEED` - Delete feed
- `ADMIN.GET.FEEDS` - View all feeds across all users

**Responsibilities**:
- CRUD operations for user feeds
- Ownership verification (users can only modify their own feeds)
- Permission enforcement with value-based limits

## Service Layer

Business logic is organized in the `services/` directory:

### Authentication Service (`services/authService/`)

**Files**:
- `authService.py` - JWT token creation/validation, password hashing
- `permissionCheckers.py` - Permission enforcement dependencies

**Responsibilities**:
- Password hashing with bcrypt
- Password verification
- JWT token creation with expiration
- JWT token validation
- User extraction from tokens
- Permission checking logic

**Key Functions**:
```python
get_password_hash(password: str) -> str
verify_password(plain: str, hashed: str) -> bool
create_access_token(data: dict, expires_delta: timedelta) -> str
get_current_user(token: str, session: Session) -> UserORM
get_current_active_user(current_user: UserORM) -> UserORM
```

### Database Service (`services/dbService/`)

**Files**:
- `database.py` - Database session management and configuration
- `crud/userCrud.py` - User CRUD operations
- `crud/newsInsert.py` - News article creation
- `crud/newsGet.py` - News retrieval and filtering

**Responsibilities**:
- Database engine creation
- Session lifecycle management
- CRUD operations for each entity
- Query building and execution

**Key Functions**:
```python
get_db() -> Generator[Session]  # Dependency injection
create_user(db: Session, user: UserCreate) -> UserORM
get_user_by_email(db: Session, email: str) -> UserORM
create_news_article(article: NewsArticleORM, db: Session)
get_news_for_feed(feed_id: int, db: Session) -> List[NewsArticle]
```

### External API Integration

**File**: `services/retrieveNews.py`

**Responsibilities**:
- Call NewsData.io API
- Parse and transform news data
- Create NewsArticleORM objects
- Handle API errors and rate limits

## Database Session Management

**Pattern**: Dependency injection with automatic session lifecycle

**Implementation**: `services/dbService/database.py`

```python
from sqlmodel import Session, create_engine

engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=True)

def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
```

**Usage in routes**:
```python
from fastapi import Depends
from services.dbService.database import get_db

@router.post("/add_feed")
def add_feed(db: Session = Depends(get_db)):
    # Session is automatically provided and closed
    ...
```

**Features**:
- `pool_pre_ping=True` - Test connections before use
- `echo=True` - Log all SQL queries (development)
- Automatic session cleanup
- Connection pooling

## Middleware and CORS

**Current state**: Minimal middleware configuration in `main.py`

**Recommended CORS setup**:
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

## Error Handling Strategy

### HTTPException Pattern

All errors use FastAPI's `HTTPException`:

```python
from fastapi import HTTPException, status

# 404 Not Found
if not feed:
    raise HTTPException(status_code=404, detail="Feed not found")

# 403 Forbidden
if feed.user_id != current_user.id:
    raise HTTPException(status_code=403, detail="Not authorized")

# 401 Unauthorized
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
```

### Common Status Codes

- **200 OK** - Successful GET request
- **201 Created** - Successful POST (resource created)
- **204 No Content** - Successful DELETE
- **400 Bad Request** - Invalid request data (Pydantic validation)
- **401 Unauthorized** - Missing or invalid authentication
- **403 Forbidden** - Insufficient permissions
- **404 Not Found** - Resource not found
- **422 Unprocessable Entity** - Validation error (automatic)

### Automatic Validation Errors

Pydantic automatically returns 422 for invalid request data:

```python
# Request body validation
@router.post("/add_feed", response_model=UserFeedResponse)
def add_feed(feed_data: UserFeedCreate, ...):
    # Pydantic validates feed_data automatically
    # Returns 422 if validation fails
    ...
```

## Request/Response Flow

### Typical Request Flow

```
1. HTTP Request arrives
   ↓
2. FastAPI routing matches endpoint
   ↓
3. Dependency injection runs
   ├─ get_db() creates database session
   ├─ get_current_user() validates JWT token
   ├─ require_permissions() checks permissions
   └─ (Other dependencies)
   ↓
4. Pydantic validates request body
   ↓
5. Route handler executes
   ├─ Calls service functions
   ├─ Performs database operations
   └─ Prepares response data
   ↓
6. Pydantic validates response
   ↓
7. FastAPI serializes to JSON
   ↓
8. HTTP Response returned
   ↓
9. Dependencies cleaned up
   └─ Database session closed
```

### Example: Creating a Feed

```
POST /feeds/add_feed
Authorization: Bearer <token>
Body: {"feedname": "Tech News", "stocks": ["AAPL"], "sources": ["NewsAPI"]}

1. FastAPI routes to add_feed()
2. get_db() creates session
3. get_current_active_user() extracts user from token
4. require_permission_with_max() checks ADD.FEED permission
5. Pydantic validates UserFeedCreate
6. Route handler creates UserFeedORM
7. Database insert via session.add() + session.commit()
8. Pydantic converts to UserFeedResponse
9. JSON response returned
10. Session automatically closed
```

## Dependency Injection Pattern

FastAPI's dependency injection is used extensively:

```python
from fastapi import Depends

# Database session
db: Session = Depends(get_db)

# Current authenticated user
current_user: UserORM = Depends(get_current_active_user)

# Permission checks (as dependencies)
@router.get("/protected", dependencies=[require_permissions(["SOME.PERMISSION"])])
```

**Benefits**:
- Clean separation of concerns
- Easy testing (mock dependencies)
- Reusable logic
- Automatic cleanup

## Performance Considerations

### Connection Pooling

SQLAlchemy handles connection pooling:
- Default pool size: 5
- Max overflow: 10
- Pool recycle: 3600 seconds

### Async Support

FastAPI supports async route handlers (not currently used):

```python
# Sync (current)
@router.get("/feeds")
def get_feeds(...):
    ...

# Async (potential optimization)
@router.get("/feeds")
async def get_feeds(...):
    async with AsyncSession(engine) as session:
        ...
```

### Caching

No caching layer is currently implemented. Potential improvements:
- Redis for frequently accessed data
- In-memory cache for permissions
- HTTP caching headers

## Scalability

The API is designed for horizontal scaling:
- **Stateless**: JWT authentication (no server-side sessions)
- **Connection pooling**: Efficient database usage
- **Minimal coupling**: Independent route handlers
- **Dependency injection**: Easy to add middleware/services

## Security Features

- **Password hashing**: bcrypt with salt
- **JWT tokens**: HS256 algorithm, configurable expiration
- **Permission enforcement**: Dependency injection ensures checks
- **SQL injection protection**: ORM prevents injection attacks
- **Input validation**: Pydantic validates all input
- **API key protection**: Environment variables

## Monitoring and Logging

**Current state**: Minimal logging

- SQL queries logged with `echo=True` (development)
- Debug print statements in code
- No structured logging framework

**Recommendations**:
- Implement Python `logging` module
- Add request/response logging middleware
- Use structured logging (JSON format)
- Integrate with monitoring services (Sentry, DataDog, etc.)

## Development Workflow

1. **Start server**: `uvicorn main:app --reload`
2. **Access docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
3. **Make changes**: Files auto-reload
4. **Test**: Use Swagger UI or pytest
5. **Debug**: Check terminal for SQL queries and print statements

## Next Steps for Backend Enhancement

1. **Add comprehensive tests** - Increase test coverage
2. **Implement proper logging** - Replace print with logging
3. **Add caching layer** - Redis for performance
4. **Async database operations** - Use AsyncSession
5. **API rate limiting** - Prevent abuse
6. **Request validation middleware** - Additional security
7. **Health check endpoint** - Monitor API status
8. **Metrics collection** - Track performance
9. **Database migrations** - Use Alembic
10. **API versioning** - Support multiple API versions

See [Extending the Backend](extending.md) for instructions on adding new features.
