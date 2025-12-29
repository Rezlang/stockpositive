# Architecture

This document describes the system architecture of the StockPositive v1 API.

## System Overview

```
┌──────────────────────┐
│  React Native App    │
│  (Mobile Client)     │
└──────────┬───────────┘
           │ HTTPS/REST
           ↓
┌──────────────────────┐
│   FastAPI Backend    │
│     (main.py)        │
│  ┌────────────────┐  │
│  │ Authentication │  │
│  │   (JWT/OAuth)  │  │
│  └────────────────┘  │
│  ┌────────────────┐  │
│  │  Permission    │  │
│  │    System      │  │
│  └────────────────┘  │
│  ┌────────────────┐  │
│  │   Route        │  │
│  │   Handlers     │  │
│  └────────────────┘  │
│  ┌────────────────┐  │
│  │   Services     │  │
│  └────────────────┘  │
└──────────┬───────────┘
           │
     ┌─────┴──────┐
     ↓            ↓
┌─────────┐  ┌────────────┐
│PostgreSQL│  │  ChromaDB  │
│ (Data)   │  │ (Vectors)  │
└─────────┘  └────────────┘
     │
     │ External APIs
     ↓
┌──────────────────────┐
│ - NewsData.io        │
│ - TwelveData         │
│ - yfinance           │
│ - Google Gemini AI   │
│ - Mistral AI         │
└──────────────────────┘
```

## Component Boundaries

### 1. Mobile Application Layer
- **Technology**: React Native with TypeScript
- **Responsibility**: User interface, input validation, state management
- **Communication**: REST API calls to backend with JWT authentication
- **Data**: Local state, AsyncStorage for tokens and user preferences

### 2. API Layer (FastAPI)
- **Entry Point**: `main.py`
- **Responsibility**: Request routing, business logic orchestration, authentication, authorization
- **Components**:
  - **Route Handlers** (`routes/`): HTTP endpoint definitions
  - **Services** (`services/`): Business logic and external API integration
  - **Models** (`models/`): Pydantic request/response schemas
  - **ORM** (`ORM/`): SQLAlchemy database models

### 3. Database Layer
- **PostgreSQL**: Relational data storage (users, feeds, news, permissions)
- **ChromaDB**: Vector database for embeddings (AI-powered features)
- **Access Pattern**: ORM-based queries via SQLAlchemy/SQLModel

### 4. External Services Layer
- **NewsData.io**: Financial news aggregation
- **TwelveData & yfinance**: Stock market data
- **Google Gemini AI**: Text summarization and analysis
- **Mistral AI**: Alternative AI processing

## Authentication Flow

```
1. User Registration/Login
   ┌──────────┐
   │  Mobile  │
   │   App    │
   └────┬─────┘
        │ POST /users/register
        │ POST /users/login (OAuth2PasswordRequestForm)
        ↓
   ┌─────────────┐
   │   FastAPI   │
   │ Verify      │
   │ Credentials │
   └─────┬───────┘
        │ bcrypt password check
        ↓
   ┌────────────┐
   │ Create JWT │
   │ Token      │
   └─────┬──────┘
        │ Return token
        ↓
   ┌──────────┐
   │  Mobile  │
   │  Stores  │
   │  Token   │
   └──────────┘

2. Authenticated Requests
   ┌──────────┐
   │  Mobile  │
   │   App    │
   └────┬─────┘
        │ Authorization: Bearer <token>
        ↓
   ┌──────────────────┐
   │  FastAPI         │
   │  oauth2_scheme   │
   └────┬─────────────┘
        │ Verify JWT signature
        │ Extract user email
        ↓
   ┌──────────────────┐
   │  Query Database  │
   │  for User        │
   └────┬─────────────┘
        │ Return UserORM
        ↓
   ┌──────────────────┐
   │  Check           │
   │  Permissions     │
   └────┬─────────────┘
        │ Execute route handler
        ↓
   ┌──────────┐
   │ Response │
   └──────────┘
```

**Implementation**: `services/authService/authService.py`
- `get_password_hash()`: bcrypt password hashing
- `verify_password()`: Password verification
- `create_access_token()`: JWT token generation with expiration
- `get_current_user()`: JWT validation and user retrieval
- `get_current_active_user()`: Active user verification

## Permission System

The StockPositive API implements a role-based access control (RBAC) system with value-based permissions.

### Architecture

```
UserORM
   │
   ├─ usergroup_id (FK)
   │
   ↓
UserGroupORM
   │
   ├─ permission_links (relationship)
   │
   ↓
UserGroupPermissionORM
   │
   ├─ permission_id (FK)
   ├─ permission_value (int)
   │
   ↓
PermissionORM
   │
   ├─ name (str)
   ├─ description (str)
   ├─ perm_max (int | None)
```

### Permission Types

1. **Boolean Permissions** (value-based, no maximum):
   - Example: `GET.NEWS`, `LOAD.NEWS`, `DELETE.FEED`
   - Check: Permission exists and value != 0

2. **Value-Based Permissions** (with maximum):
   - Example: `ADD.FEED` with value = 5 (max 5 feeds)
   - Check: Permission value >= required value
   - Special value `-2`: Unlimited

### Permission Checking

**Implementation**: `services/authService/permissionCheckers.py`

1. **require_permissions()**:
   - Enforces boolean permissions
   - Usage: `dependencies=[require_permissions(["GET.NEWS"])]`
   - Raises HTTP 403 if permission missing or value == 0

2. **require_permission_with_max()**:
   - Enforces value-based permissions
   - Supports static checks and dynamic value getters
   - Usage: `dependencies=[require_permission_with_max("ADD.FEED", value_getter=lambda u: len(u.feeds) + 1)]`
   - Raises HTTP 403 if value insufficient

**Example**:
```python
@router.post("/add_feed",
             dependencies=[require_permission_with_max(
                 "ADD.FEED",
                 value_getter=lambda u: len(u.feeds) + 1
             )])
def add_feed(...):
    # User must have ADD.FEED permission with value >= (current_feeds + 1)
    ...
```

## Data Flow

### News Aggregation Flow

```
1. Load News Request
   Mobile App
      │ GET /news/load-news?source=market&symbols=AAPL,GOOGL
      ↓
   Route Handler (newsRoutes.py)
      │ Check LOAD.NEWS permission
      ↓
   retrieveNews(source, symbols)
      │ Call NewsData.io API
      ↓
   NewsArticleORM objects created
      │
      ↓
   create_news_article() for each
      │ Insert into PostgreSQL
      ↓
   Return news articles

2. Get News for Feed
   Mobile App
      │ GET /news/get-news?feedId=1
      ↓
   Route Handler (newsRoutes.py)
      │ Check GET.NEWS permission
      ↓
   get_news_for_feed(feedId, db)
      │ Query PostgreSQL for feed
      │ Filter news by feed.stocks and feed.sources
      ↓
   Return filtered news articles
```

**Key Files**:
- `routes/newsRoutes.py`: API endpoints
- `services/retrieveNews.py`: External API integration
- `services/dbService/crud/newsInsert.py`: News creation
- `services/dbService/crud/newsGet.py`: News retrieval

### Feed Management Flow

```
Create Feed:
   Mobile App → POST /feeds/add_feed
   ├─ Check ADD.FEED permission (with value check)
   ├─ Create UserFeedORM
   ├─ Insert into PostgreSQL
   └─ Return feed

Get User Feeds:
   Mobile App → GET /feeds/get_feeds
   ├─ Check GET.FEEDS permission
   ├─ current_user.feeds (ORM relationship)
   └─ Return feeds

Edit Feed:
   Mobile App → PUT /feeds/edit_feed/{feed_id}
   ├─ Check EDIT.FEED permission
   ├─ Verify user owns feed
   ├─ Update UserFeedORM
   └─ Return updated feed

Delete Feed:
   Mobile App → DELETE /feeds/delete_feed/{feed_id}
   ├─ Check DELETE.FEED permission
   ├─ Verify user owns feed
   ├─ Delete UserFeedORM
   └─ Return 204 No Content
```

**Key Files**:
- `routes/feedRoutes.py`: Feed CRUD operations
- `ORM/userFeedORM.py`: Feed database model

## External Integrations

### NewsData.io
- **Purpose**: Financial news aggregation
- **Configuration**: `NEWSDATA_API_KEY` in `.env`
- **Usage**: `services/retrieveNews.py`
- **Data**: News articles with metadata (title, description, source, sentiment)

### TwelveData & yfinance
- **Purpose**: Stock market data (prices, historical data)
- **Configuration**: `TWELVEDATA_KEY` in `.env`
- **Usage**: Stock price retrieval and charting
- **Data**: OHLCV data, real-time prices

### Google Gemini AI
- **Purpose**: AI-powered text summarization and analysis
- **Configuration**: `GEMINI_API_KEY` in `.env`
- **Usage**: News article summarization, sentiment analysis
- **Data**: Text embeddings, summaries

### Mistral AI
- **Purpose**: Alternative AI processing
- **Configuration**: `MISTRAL_API_KEY` in `.env`
- **Usage**: Text analysis and generation
- **Data**: AI-generated content

## Key Abstractions

### 1. ORM Models (`ORM/`)
- **Purpose**: Database table representations
- **Pattern**: SQLAlchemy declarative models
- **Naming**: `*ORM.py` (e.g., `userORM.py`, `userFeedORM.py`)
- **Features**: Relationships, properties, cascading deletes

**Example**: `userORM.py`
```python
class UserORM(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    usergroup_id = Column(Integer, ForeignKey("usergroups.id"))
    usergroup = relationship("UserGroupORM", backref="users")
    feeds = relationship("UserFeedORM", cascade="all, delete-orphan")

    @property
    def permissions(self) -> dict[str, int | None]:
        return {
            link.permission.name: link.permission_value
            for link in self.usergroup.permission_links
        }
```

### 2. Pydantic Models (`models/`)
- **Purpose**: Request/response schema validation
- **Pattern**: Pydantic BaseModel
- **Types**: Create, Update, Response models
- **Features**: Type validation, serialization, documentation

**Example**: `models/userFeed.py`
```python
class UserFeedCreate(BaseModel):
    feedname: str
    stocks: List[str]
    sources: List[str]

class UserFeedResponse(BaseModel):
    id: int
    feedname: str
    stocks: List[str]
    sources: List[str]
```

### 3. Service Layer (`services/`)
- **Purpose**: Business logic and external API integration
- **Organization**:
  - `authService/`: Authentication and permissions
  - `dbService/`: Database operations (CRUD)
  - `retrieveNews.py`: External API calls
- **Pattern**: Utility functions grouped by domain

### 4. Route Handlers (`routes/`)
- **Purpose**: HTTP endpoint definitions
- **Pattern**: FastAPI APIRouter
- **Responsibilities**:
  - Request validation (Pydantic)
  - Permission enforcement (dependencies)
  - Service orchestration
  - Response formatting

**Example**: `routes/feedRoutes.py`
```python
@router.post("/add_feed",
             response_model=UserFeedResponse,
             dependencies=[require_permission_with_max("ADD.FEED", ...)])
def add_feed(feed_data: UserFeedCreate, current_user: UserORM, db: Session):
    new_feed = UserFeedORM(user_id=current_user.id, **feed_data.dict())
    db.add(new_feed)
    db.commit()
    return new_feed
```

## Database Session Management

**Implementation**: `services/dbService/database.py`

- **Pattern**: Dependency injection via `get_db()`
- **Lifecycle**: Session per request
- **Usage**: `db: Session = Depends(get_db)`
- **Cleanup**: Automatic session close after request

## CORS and Middleware

**Configuration**: `main.py`

- CORS middleware for cross-origin requests from mobile app
- Request logging middleware (if configured)
- Exception handling middleware

## Error Handling Strategy

- **Pattern**: HTTPException with status codes
- **Status Codes**:
  - `401 UNAUTHORIZED`: Invalid/missing JWT token
  - `403 FORBIDDEN`: Insufficient permissions
  - `404 NOT FOUND`: Resource not found
  - `422 UNPROCESSABLE ENTITY`: Invalid request data (Pydantic validation)
- **Response Format**: `{"detail": "Error message"}`

**Example**:
```python
if not feed:
    raise HTTPException(status_code=404, detail="Feed not found")
if feed.user_id != current_user.id:
    raise HTTPException(status_code=403, detail="Not authorized")
```

## ChromaDB Vector Database

**Purpose**: Storage and retrieval of text embeddings for AI-powered features.

**Note**: ChromaDB integration details are not fully visible in the current codebase. The `chroma_db/` directory exists but usage patterns are unclear. This may be used for:
- News article similarity search
- Semantic news retrieval
- AI-powered feed recommendations

**Configuration**: Implementation details to be determined from `chroma_db/` directory contents.

## Scalability Considerations

- **Stateless API**: JWT authentication enables horizontal scaling
- **Database Connection Pool**: SQLAlchemy manages connection pooling
- **Async Support**: FastAPI supports async route handlers (not currently used)
- **Caching**: No caching layer observed (potential future enhancement)

## Security

- **Password Hashing**: bcrypt with salt
- **JWT Tokens**: HS256 algorithm, configurable expiration
- **API Keys**: Environment variables, never committed to code
- **Permission Enforcement**: Dependency injection ensures all protected routes check permissions
- **Database Injection**: SQLAlchemy ORM prevents SQL injection
