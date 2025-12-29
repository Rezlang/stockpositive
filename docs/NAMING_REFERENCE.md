# Naming Reference Guide

Quick reference for the StockPositive v1 API naming conventions.

## File Naming Convention

**All Python files use camelCase**

### Quick Reference Table

| Category | Pattern | Examples |
|----------|---------|----------|
| ORM Models | `*ORM.py` | `userORM.py`, `userFeedORM.py`, `newsArticleORM.py` |
| Pydantic Models | `camelCase.py` | `user.py`, `userFeed.py`, `newsArticle.py`, `token.py` |
| Routes | `*Routes.py` | `userRoutes.py`, `feedRoutes.py`, `newsRoutes.py` |
| Services | `camelCase.py` | `authService.py`, `permissionCheckers.py`, `retrieveNews.py` |
| Directories | `camelCase/` | `authService/`, `dbService/`, `ORM/`, `models/` |

## Import Patterns

### Module-Style Imports (Preferred)

```python
# Import modules
from models import user, userFeed, newsArticle
from ORM import userORM, userFeedORM
from services import authService, database

# Usage
user_data = user.UserCreate(...)
db_user = userORM.UserORM(...)
token = authService.create_access_token(...)
```

### Direct Imports (Alternative)

```python
# Import specific classes
from models.user import UserCreate, UserResponse
from ORM.userORM import UserORM
from services.authService import create_access_token

# Usage
user_data = UserCreate(...)
db_user = UserORM(...)
token = create_access_token(...)
```

## Directory Structure with camelCase

```
API/v1/
├── main.py
├── models/                    # Pydantic schemas
│   ├── user.py
│   ├── userFeed.py
│   ├── newsArticle.py
│   └── token.py
├── ORM/                       # SQLAlchemy models
│   ├── base.py
│   ├── userORM.py
│   ├── userGroupORM.py
│   ├── permissionORM.py
│   ├── userFeedORM.py
│   └── newsArticleORM.py
├── routes/                    # API endpoints
│   ├── userRoutes.py
│   ├── newsRoutes.py
│   └── feedRoutes.py
└── services/                  # Business logic
    ├── authService/
    │   ├── authService.py
    │   └── permissionCheckers.py
    ├── dbService/
    │   ├── database.py
    │   └── crud/
    │       ├── userCrud.py
    │       ├── newsInsert.py
    │       └── newsGet.py
    └── retrieveNews.py
```

## Code Naming Conventions

| Element | Convention | Examples |
|---------|------------|----------|
| Files | camelCase | `authService.py`, `userORM.py` |
| Directories | camelCase | `authService/`, `dbService/` |
| Classes | PascalCase | `UserORM`, `UserCreate`, `NewsArticle` |
| Functions | snake_case | `get_user_by_email`, `create_access_token` |
| Variables | snake_case | `user_permissions`, `access_token_expires` |
| Constants | UPPER_SNAKE_CASE | `SECRET_KEY`, `ALGORITHM`, `DATABASE_URL` |

## Migration from snake_case

If you see old references, here's the mapping:

| Old (snake_case) | New (camelCase) |
|------------------|-----------------|
| `auth_service/` | `authService/` |
| `auth_service.py` | `authService.py` |
| `permission_checkers.py` | `permissionCheckers.py` |
| `db_service/` | `dbService/` |
| `user_crud.py` | `userCrud.py` |
| `news_insert.py` | `newsInsert.py` |
| `news_get.py` | `newsGet.py` |
| `retrieve_news.py` | `retrieveNews.py` |
| `news_routes.py` | `newsRoutes.py` |

## Best Practices

1. ✅ **DO**: Use camelCase for all Python filenames
2. ✅ **DO**: Use module-style imports (`from models import user`)
3. ✅ **DO**: Keep function/variable names in snake_case
4. ✅ **DO**: Keep class names in PascalCase
5. ❌ **DON'T**: Mix snake_case and camelCase for filenames
6. ❌ **DON'T**: Use different import styles in the same file

## Examples

### Good ✅

```python
# File: routes/userRoutes.py
from fastapi import APIRouter, Depends
from models import user, token
from ORM import userORM
from services import authService, database

@router.post("/register", response_model=user.UserResponse)
def register_user(user_data: user.UserCreate, db = Depends(database.get_db)):
    db_user = userORM.UserORM(
        email=user_data.email,
        hashed_password=authService.get_password_hash(user_data.password)
    )
    db.add(db_user)
    db.commit()
    return db_user
```

### Bad ❌

```python
# File: routes/user_routes.py  # WRONG: snake_case filename
from models.user import UserCreate  # WRONG: Not using module import
from ORM.user_orm import UserORM  # WRONG: File should be userORM.py
from services.auth_service import get_password_hash  # WRONG: Should be authService

# Mixing import styles
```

## Quick Checklist

When creating new files:
- [ ] Filename is camelCase
- [ ] Imports use module style
- [ ] Classes are PascalCase
- [ ] Functions are snake_case
- [ ] Constants are UPPER_SNAKE_CASE
- [ ] Directory names are camelCase

## See Also

- [Full Conventions Guide](conventions.md)
- [Project Structure](structure.md)
- [Architecture Overview](architecture.md)
