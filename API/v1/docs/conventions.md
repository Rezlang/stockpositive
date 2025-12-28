# Code Conventions

This document describes the code style, naming patterns, and conventions used in the StockPositive v1 API.

## Naming Conventions

### Python (Backend)

#### Functions and Variables
- **Style**: `snake_case`
- **Examples**: `get_user_by_email`, `create_access_token`, `user_permissions`

```python
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
```

#### Classes
- **Style**: `PascalCase`
- **Examples**: `UserORM`, `UserFeedCreate`, `NewsArticle`

```python
class UserORM(Base):
    __tablename__ = "users"
    ...

class UserFeedCreate(BaseModel):
    feedname: str
    stocks: List[str]
```

#### Constants
- **Style**: `UPPER_SNAKE_CASE`
- **Examples**: `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`

```python
SECRET_KEY = os.getenv("JWT_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
```

### File Naming

**Convention**: All Python files use **camelCase** naming.

#### ORM Models
- **Pattern**: `*ORM.py` (camelCase with ORM suffix)
- **Examples**: `userORM.py`, `userFeedORM.py`, `newsArticleORM.py`, `userGroupORM.py`
- **Purpose**: Clearly indicates database model files
- **Module Import**: `from ORM.userORM import UserORM` or `import ORM.userORM`

#### Pydantic Models
- **Pattern**: `camelCase.py` (domain-based naming)
- **Examples**: `user.py`, `userFeed.py`, `newsArticle.py`, `token.py`
- **Purpose**: Groups related schemas together
- **Module Import**: `from models.user import UserCreate` or `import models.user`

#### Route Files
- **Pattern**: `*Routes.py` (camelCase with Routes suffix)
- **Examples**: `userRoutes.py`, `feedRoutes.py`, `newsRoutes.py`
- **Purpose**: Indicates API endpoint definitions
- **Module Import**: `from routes import userRoutes` or `import routes.userRoutes`

#### Service Files
- **Pattern**: `camelCase.py` or `*Service.py`
- **Examples**: `authService.py`, `permissionCheckers.py`, `retrieveNews.py`, `database.py`
- **Purpose**: Describes the service's purpose
- **Module Import**: `from services.authService import function` or `import services.authService`

**Note**: Avoid snake_case for filenames (e.g., `auth_service.py`). Use camelCase instead (e.g., `authService.py`).

## Code Organization

### Route Organization

Routes are grouped by domain and registered with prefixes:

```python
# main.py
app.include_router(news_routes.router, prefix="/news", tags=["news"])
app.include_router(userRoutes.router, prefix="/users", tags=["users"])
app.include_router(feedRoutes.router, prefix="/feeds", tags=["feeds"])
```

Within each router file:
- Authentication endpoints first
- CRUD operations in order: Create, Read, Update, Delete
- Admin/special endpoints last

### Service Layer Organization

Services are grouped by domain in subdirectories:

```
services/
├── authService/        # Authentication and authorization
│   ├── authService.py
│   └── permissionCheckers.py
├── dbService/          # Database operations
│   ├── database.py
│   └── crud/
└── retrieveNews.py     # External API integration
```

## Error Handling Patterns

### HTTPException Usage

All API errors use FastAPI's `HTTPException`:

```python
from fastapi import HTTPException, status

# 404 Not Found
if not feed:
    raise HTTPException(status_code=404, detail="Feed not found")

# 403 Forbidden
if feed.user_id != current_user.id:
    raise HTTPException(
        status_code=403,
        detail="Not authorized to delete this feed"
    )

# 401 Unauthorized
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect email or password",
    headers={"WWW-Authenticate": "Bearer"},
)
```

### Error Response Format

All errors return JSON with a `detail` field:

```json
{
  "detail": "Error message here"
}
```

## Authentication Patterns

### Dependency Injection with Depends

Authentication uses FastAPI's dependency injection:

```python
from fastapi import Depends
from services.authService.authService import get_current_active_user

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: UserORM = Depends(get_current_active_user)):
    return current_user
```

### OAuth2 Password Flow

Login uses OAuth2PasswordRequestForm:

```python
@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, form_data.username)  # Note: 'username' field
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(...)
```

**Note**: OAuth2PasswordRequestForm uses `username` field, but we treat it as email.

## Permission Checking Patterns

### Boolean Permissions

Use `require_permissions()` for simple permission checks:

```python
from services.authService.permissionCheckers import require_permissions

@router.get("/load-news",
            dependencies=[require_permissions(["LOAD.NEWS"])])
def load_market_news(...):
    ...
```

### Value-Based Permissions

Use `require_permission_with_max()` for permissions with limits:

```python
from services.authService.permissionCheckers import require_permission_with_max

# Static value check
@router.post("/write-feed",
             dependencies=[require_permission_with_max("WRITE.FEED", min_value=1)])
def write_feed(...):
    ...

# Dynamic value check
@router.post("/add_feed",
             dependencies=[require_permission_with_max(
                 "ADD.FEED",
                 value_getter=lambda u: len(u.feeds) + 1
             )])
def add_feed(...):
    ...
```

## Database Conventions

### ORM Models

#### Table Names
- **Style**: Lowercase plural
- **Examples**: `users`, `usergroups`, `userfeeds`, `permissions`

```python
class UserORM(Base):
    __tablename__ = "users"
```

#### Relationships
- Use `relationship()` for related entities
- Specify `back_populates` for bidirectional relationships
- Use `cascade` for deletion behavior

```python
class UserORM(Base):
    usergroup = relationship("UserGroupORM", backref="users")
    feeds = relationship("UserFeedORM", back_populates="user", cascade="all, delete-orphan")

class UserFeedORM(Base):
    user = relationship("UserORM", back_populates="feeds")
```

#### Properties
- Use `@property` for computed attributes
- Return appropriate types (dict, list, etc.)

```python
@property
def permissions(self) -> dict[str, int | None]:
    if not self.usergroup:
        return {}
    return {
        link.permission.name: link.permission_value
        for link in self.usergroup.permission_links
    }
```

### SQL Scripts

#### File Naming
- **Pattern**: `##_descriptive_name.sql` (numbered for execution order)
- **Examples**: `01_usergroups.sql`, `02_permissions.sql`, `03_users.sql`

#### Execution Order
- Order specified in `DB/order.txt`
- Respects foreign key dependencies
- Schema files in `DB/Scripts/`
- Data insertion files in `DB/Insert/`

## Pydantic Model Patterns

### Model Types

#### Create Models
- Contain only fields needed for creation
- Exclude auto-generated fields (id, created_at)

```python
class UserFeedCreate(BaseModel):
    feedname: str
    stocks: List[str]
    sources: List[str]
```

#### Update Models
- All fields optional (use `Optional[...]`)
- Only update provided fields

```python
class UserFeedUpdate(BaseModel):
    feedname: Optional[str] = None
    stocks: Optional[List[str]] = None
    sources: Optional[List[str]] = None
```

#### Response Models
- Include all fields to be returned
- Match ORM model structure
- Use `model_validate(orm_obj, from_attributes=True)` for conversion

```python
class UserFeedResponse(BaseModel):
    id: int
    feedname: str
    stocks: List[str]
    sources: List[str]
    user_id: int
```

## Type Hints

All function signatures include type hints:

```python
def verify_password(plain_password: str, hashed_password: str) -> bool:
    ...

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    ...

def get_current_user(token: str, session: Session) -> UserORM:
    ...
```

## Documentation Patterns

### Docstrings

Use docstrings for route handlers:

```python
@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    return create_user(db, user)

@router.get("/get_feeds", response_model=List[UserFeedResponse])
def get_user_feeds(current_user: UserORM = Depends(get_current_active_user)):
    """
    Get all feeds for the current user.
    """
    return current_user.feeds
```

### OpenAPI Tags

Routes are grouped with tags for API documentation:

```python
app.include_router(news_routes.router, prefix="/news", tags=["news"])
app.include_router(userRoutes.router, prefix="/users", tags=["users"])
app.include_router(feedRoutes.router, prefix="/feeds", tags=["feeds"])
```

## Import Organization

### Import Order
1. Standard library
2. Third-party packages
3. FastAPI imports
4. Local imports (models, ORM, services)

### Module-Style Imports

**Convention**: Use module-style imports for better organization and clarity.

**Preferred Pattern**:
```python
# Module imports (PREFERRED)
from models import user, userFeed, newsArticle
from ORM import userORM, userFeedORM
from services import authService, database

# Usage
user_data = user.UserCreate(...)
db_user = userORM.UserORM(...)
token = authService.create_access_token(...)
```

**Alternative Pattern** (when importing specific classes):
```python
# Direct class imports (when needed)
from models.user import UserCreate, UserResponse
from ORM.userORM import UserORM
from services.authService import create_access_token
```

### Complete Import Example

```python
# Standard library
from datetime import timedelta
from typing import List, Optional

# Third-party
from sqlmodel import Session
from fastapi import APIRouter, Depends, HTTPException, status

# FastAPI
from fastapi.security import OAuth2PasswordRequestForm

# Local - Module style (PREFERRED)
from models import user, token
from ORM import userORM
from services import database, authService

# Usage in code
def register_user(user_data: user.UserCreate, db: Session = Depends(database.get_db)):
    """Register a new user"""
    db_user = userORM.UserORM(
        username=user_data.username,
        email=user_data.email,
        hashed_password=authService.get_password_hash(user_data.password)
    )
    db.add(db_user)
    db.commit()
    return user.UserResponse.model_validate(db_user, from_attributes=True)
```

### Why Module-Style Imports?

1. **Clarity**: Clear which module each class comes from
2. **Namespace**: Avoids naming conflicts (e.g., `user.UserCreate` vs `userFeed.UserFeedCreate`)
3. **Consistency**: All modules imported the same way
4. **Refactoring**: Easier to see dependencies
5. **Type Safety**: Better IDE autocomplete and type checking

### Import Guidelines

- **DO**: `from models import user, newsArticle`
- **DO**: `from ORM import userORM, userFeedORM`
- **DO**: Use `ORM.base`, `models.newsArticle` patterns
- **DON'T**: Mix import styles within the same file
- **DON'T**: Use `from models.user import *` (wildcard imports)
- **DON'T**: Use relative imports like `from ..models import user`

## Logging Patterns

Minimal logging is currently implemented. Debug print statements are used:

```python
print("Permissions:", current_user.permissions)
```

**Note**: Consider implementing proper logging with Python's `logging` module for production.

## Security Practices

### Password Handling
- **Never** store plaintext passwords
- Always use `get_password_hash()` before storing
- Use `verify_password()` for authentication

```python
# When creating user
hashed_password = get_password_hash(user.password)

# When authenticating
if not verify_password(form_data.password, user.hashed_password):
    raise HTTPException(...)
```

### API Keys
- Store in `.env` file
- Load with `python-dotenv`
- Never commit to git

```python
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv("JWT_KEY")
```

### JWT Tokens
- Include expiration (`exp` claim)
- Sign with secret key
- Validate on every protected request

## Database Transaction Patterns

### Manual Transaction Management

```python
# Create
db.add(new_feed)
db.commit()
db.refresh(new_feed)  # Get auto-generated fields

# Update
db.add(feed)  # SQLAlchemy tracks changes
db.commit()
db.refresh(feed)

# Delete
db.delete(feed)
db.commit()
```

### Session Lifecycle
- Sessions provided via `Depends(get_db)`
- Automatically closed after request
- No manual session management needed

## API Versioning

**Current approach**: Directory-based versioning (`v1/`)

Future versions would be added as `v2/`, `v3/`, etc., allowing multiple versions to run simultaneously.

## Common Anti-Patterns to Avoid

1. **Don't** return ORM objects directly from routes (use Pydantic response models)
2. **Don't** put business logic in route handlers (use service layer)
3. **Don't** hardcode configuration values (use environment variables)
4. **Don't** skip permission checks on protected endpoints
5. **Don't** forget to validate user ownership before modifying resources

## Consistency Checklist

When adding new code:
- [ ] Use **camelCase** for all Python filenames
- [ ] Follow snake_case for functions/variables
- [ ] Follow PascalCase for classes
- [ ] Use module-style imports (`from models import user`)
- [ ] Add type hints to all functions
- [ ] Use HTTPException for errors
- [ ] Add docstrings to route handlers
- [ ] Use dependency injection for auth and db
- [ ] Validate request data with Pydantic
- [ ] Check permissions on protected routes
- [ ] Use appropriate HTTP status codes
- [ ] Follow import organization order
