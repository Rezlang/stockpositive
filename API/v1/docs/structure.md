# Project Structure

This document describes the organization and layout of the StockPositive v1 API codebase.

## Directory Tree

```
stockpositive/
├── API/
│   ├── .env                    # Environment configuration (not in git)
│   ├── v1/                      # v1 API (current)
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── requirements.txt     # Python dependencies
│   │   ├── docs/                # Documentation (this directory)
│   │   ├── models/              # Pydantic request/response schemas
│   │   │   ├── newsArticle.py
│   │   │   ├── newsResponse.py
│   │   │   ├── token.py
│   │   │   ├── user.py
│   │   │   └── userFeed.py
│   │   ├── ORM/                 # SQLAlchemy database models
│   │   │   ├── base.py
│   │   │   ├── newsArticleORM.py
│   │   │   ├── permissionORM.py
│   │   │   ├── userFeedORM.py
│   │   │   ├── userGroupORM.py
│   │   │   ├── userGroupPermissionORM.py
│   │   │   └── userORM.py
│   │   ├── routes/              # API endpoint routers
│   │   │   ├── feedRoutes.py    # Feed CRUD operations
│   │   │   ├── newsRoutes.py   # News aggregation endpoints
│   │   │   └── userRoutes.py    # User authentication endpoints
│   │   ├── services/            # Business logic
│   │   │   ├── authService/    # Authentication and authorization
│   │   │   │   ├── authService.py        # JWT and password handling
│   │   │   │   └── permissionCheckers.py # Permission enforcement
│   │   │   ├── dbService/      # Database operations
│   │   │   │   ├── crud/        # CRUD operations
│   │   │   │   │   ├── newsGet.py
│   │   │   │   │   ├── news_insert.py
│   │   │   │   │   └── user_crud.py
│   │   │   │   └── database.py  # Database session management
│   │   │   └── retrieve_news.py # External API integration
│   │   └── test/                # Test files
│   │       └── httpTest.py
│   └── chroma_db/               # ChromaDB vector database storage
└── DB/
    ├── Scripts/                 # SQL schema creation scripts
    │   ├── 01_usergroups.sql
    │   ├── 02_permissions.sql
    │   ├── 03_users.sql
    │   ├── 04_usergroup_permissions.sql
    │   ├── 05_userfeeds.sql
    │   └── 06_news.sql
    ├── Insert/                  # SQL data insertion scripts
    ├── order.txt                # Execution order for SQL scripts
    └── rebuild_db.py            # Database initialization script
```

## Entry Points

### API Entry Point
**File**: `API/v1/main.py`

The FastAPI application entry point that:
- Creates the FastAPI app instance
- Registers routers for `/news`, `/users`, and `/feeds` endpoints
- Configures middleware (CORS, etc.)

```python
app = FastAPI()
app.include_router(newsRoutes.router, prefix="/news", tags=["news"])
app.include_router(userRoutes.router, prefix="/users", tags=["users"])
app.include_router(feedRoutes.router, prefix="/feeds", tags=["feeds"])
```

### Database Initialization
**File**: `DB/rebuild_db.py`

Script that:
- Drops and recreates the PostgreSQL database
- Executes SQL scripts in order specified by `DB/order.txt`
- Creates database schema (tables, constraints, indexes)
- Inserts initial data (user groups, permissions, default users)

## Module Purposes

### `models/` - Pydantic Schemas
**Purpose**: Request/response data validation and serialization.

Contains Pydantic models for:
- **Request validation**: Ensure incoming data matches expected types
- **Response serialization**: Convert ORM objects to JSON
- **API documentation**: Auto-generate OpenAPI schemas

**Naming convention**: Domain-based (e.g., `user.py`, `userFeed.py`, `newsArticle.py`)

**Common patterns**:
- `*Create`: Request schema for creating resources
- `*Update`: Request schema for updating resources
- `*Response`: Response schema for returning resources
- `*`: General data models

### `ORM/` - Database Models
**Purpose**: SQLAlchemy ORM models representing database tables.

Features:
- **Relationships**: Define foreign keys and relationships between tables
- **Properties**: Computed attributes (e.g., `user.permissions`)
- **Validation**: Database-level constraints
- **Cascading**: Automatic deletion of related records

**Naming convention**: `*ORM.py` (e.g., `userORM.py`, `userFeedORM.py`)

**Key files**:
- `base.py`: SQLAlchemy declarative base
- `userORM.py`: User table with relationships to groups and feeds
- `userGroupORM.py`: User group table
- `permissionORM.py`: Permission definitions
- `userGroupPermissionORM.py`: Many-to-many relationship between groups and permissions
- `userFeedORM.py`: User feed table
- `newsArticleORM.py`: News article table

### `routes/` - API Endpoints
**Purpose**: HTTP endpoint definitions using FastAPI routers.

Responsibilities:
- Define HTTP methods (GET, POST, PUT, DELETE)
- Specify request/response models
- Enforce authentication and permissions via dependencies
- Delegate business logic to service layer
- Handle HTTP-specific concerns (status codes, headers)

**Naming convention**: `*Routes.py` or `*_routes.py`

**Key files**:
- `userRoutes.py`: `/users/*` endpoints (register, login, me)
- `newsRoutes.py`: `/news/*` endpoints (load-news, get-news)
- `feedRoutes.py`: `/feeds/*` endpoints (CRUD operations)

### `services/` - Business Logic
**Purpose**: Reusable business logic and external integrations.

#### `auth_service/` - Authentication & Authorization
- `auth_service.py`: JWT token creation/validation, password hashing
- `permission_checkers.py`: Permission enforcement dependencies

#### `db_service/` - Database Operations
- `database.py`: Database session management, connection configuration
- `crud/`: CRUD operations for each entity
  - `user_crud.py`: User creation and retrieval
  - `news_insert.py`: News article insertion
  - `news_get.py`: News article retrieval

#### External API Integration
- `retrieve_news.py`: NewsData.io API integration

### `test/` - Tests
**Purpose**: Automated tests for API endpoints and business logic.

**Current state**: Limited test coverage with `httpTest.py`

**Tools**: pytest-playwright

## Database Structure (`DB/`)

### `Scripts/` - SQL Schema
**Purpose**: SQL files that create database tables, indexes, and constraints.

**Naming convention**: Numbered for execution order (`01_*.sql`, `02_*.sql`, etc.)

**Files**:
1. `01_usergroups.sql` - User role groups
2. `02_permissions.sql` - Permission definitions
3. `03_users.sql` - User accounts
4. `04_usergroup_permissions.sql` - Group-permission assignments
5. `05_userfeeds.sql` - User feed configurations
6. `06_news.sql` - News articles

### `Insert/` - SQL Data
**Purpose**: SQL files that insert initial/seed data.

Contains default user groups, permissions, and test data.

### `order.txt` - Execution Order
**Purpose**: Specifies the order in which SQL scripts should be executed.

Used by `rebuild_db.py` to ensure proper table creation order (respecting foreign key dependencies).

### `rebuild_db.py` - Database Initialization
**Purpose**: Python script to recreate the database from scratch.

**WARNING**: This script drops all existing data.

Usage:
```bash
cd DB
python rebuild_db.py
```

## Public vs Internal Modules

### Public Modules (API Surface)
These modules define the API contract with clients:
- `routes/`: HTTP endpoints
- `models/`: Request/response schemas
- `main.py`: Application configuration

### Internal Modules (Implementation Details)
These modules are internal implementation:
- `ORM/`: Database models (not exposed directly)
- `services/`: Business logic (called by routes)
- `test/`: Test code

## Import Patterns

### Absolute Imports
All imports use absolute paths from the project root:

```python
# Routes
from models.user import UserCreate, UserResponse
from services.db_service.database import get_db
from ORM.userORM import UserORM

# Services
from services.auth_service.auth_service import create_access_token
```

### Dependency Injection
FastAPI's dependency injection is used extensively:

```python
# Database session
db: Session = Depends(get_db)

# Current user
current_user: UserORM = Depends(get_current_active_user)

# Permissions
dependencies=[require_permissions(["GET.NEWS"])]
```

## Configuration Files

- **`.env`**: Environment variables (API keys, database URL, JWT secret)
- **`requirements.txt`**: Python package dependencies
- **`main.py`**: FastAPI application configuration

## Generated vs Source-Controlled Files

### Source-Controlled
- All `.py` files
- `requirements.txt`
- SQL scripts in `DB/Scripts/` and `DB/Insert/`
- Documentation in `docs/`

### Generated/Not in Git
- `__pycache__/`: Python bytecode
- `.env`: Environment-specific configuration
- `chroma_db/`: ChromaDB database files
- Virtual environment directories

## Module Organization Patterns

### 1. Separation of Concerns
- **Routes**: HTTP layer
- **Services**: Business logic
- **ORM**: Data layer
- **Models**: Data contracts

### 2. Domain-Based Grouping
Files are organized by domain:
- User domain: `userORM.py`, `userRoutes.py`, `user.py`, `user_crud.py`
- Feed domain: `userFeedORM.py`, `feedRoutes.py`, `userFeed.py`
- News domain: `newsArticleORM.py`, `newsRoutes.py`, `newsArticle.py`

### 3. Dependency Direction
```
Routes → Services → ORM/Database
  ↓         ↓
Models    Models
```

Routes depend on services and models, but services don't depend on routes. This enables reuse and testing.

## Adding New Modules

When adding new functionality:

1. **New domain**: Create files in all layers
   - `models/domain.py`
   - `ORM/domainORM.py`
   - `routes/domainRoutes.py`
   - `services/db_service/crud/domain_crud.py`

2. **New external API**: Add to `services/`
   - Follow pattern in `retrieve_news.py`
   - Add API key to `.env`

3. **New database table**: Update `DB/Scripts/`
   - Create SQL file with next number
   - Update `DB/order.txt`
   - Create corresponding ORM model

See [Extending the Backend](backend/extending.md) for detailed instructions.
