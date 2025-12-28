# Data Layer

This document describes the database schema, ORM models, and data access patterns for the StockPositive v1 API.

## Database Schema

### Tables Overview

The database consists of six main tables:

1. **users** - User accounts
2. **usergroups** - User role groups
3. **permissions** - Permission definitions
4. **usergroup_permissions** - Many-to-many relationship between groups and permissions
5. **userfeeds** - User's custom news feeds
6. **news** - News articles

### Entity Relationship Diagram

```
usergroups
    ↑ (1:N)
    │
users ←──────────────┐
    │ (1:N)          │
    ↓                │
userfeeds            │
                     │
permissions          │
    ↑ (N:M)          │
    │                │
usergroup_permissions┘
```

## Table Schemas

### `users`

**Purpose**: Store user account information

**Schema**:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    usergroup_id INTEGER NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone_number VARCHAR(20),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_users_usergroup
        FOREIGN KEY (usergroup_id)
        REFERENCES usergroups(id)
        ON DELETE RESTRICT
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

**Fields**:
- `id`: Auto-incrementing primary key
- `usergroup_id`: Foreign key to usergroups table (required)
- `username`: Unique username (max 50 chars)
- `email`: Unique email address (max 255 chars)
- `phone_number`: Optional phone number
- `hashed_password`: Bcrypt-hashed password
- `is_active`: Account active status (default: true)
- `created_at`: Account creation timestamp

**Indexes**: username, email (for fast lookups)

**File**: `DB/Scripts/03_users.sql`

### `usergroups`

**Purpose**: Define user role groups

**Schema**:
```sql
CREATE TABLE usergroups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);
```

**Fields**:
- `id`: Primary key
- `name`: Group name (e.g., "Basic", "Premium", "Admin")

**File**: `DB/Scripts/01_usergroups.sql`

### `permissions`

**Purpose**: Define available permissions

**Schema**:
```sql
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    perm_max INTEGER
);
```

**Fields**:
- `id`: Primary key
- `name`: Permission name (e.g., "GET.NEWS", "ADD.FEED")
- `description`: Human-readable description
- `perm_max`: Maximum value for value-based permissions (NULL for boolean permissions)

**Permission Types**:
- **Boolean**: `perm_max` is NULL, permission is on/off
- **Value-based**: `perm_max` defines maximum allowed value (e.g., max feeds)

**File**: `DB/Scripts/02_permissions.sql`

### `usergroup_permissions`

**Purpose**: Assign permissions to user groups with values

**Schema**:
```sql
CREATE TABLE usergroup_permissions (
    id SERIAL PRIMARY KEY,
    usergroup_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    permission_value INTEGER,
    CONSTRAINT fk_ugp_usergroup
        FOREIGN KEY (usergroup_id)
        REFERENCES usergroups(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_ugp_permission
        FOREIGN KEY (permission_id)
        REFERENCES permissions(id)
        ON DELETE CASCADE,
    UNIQUE (usergroup_id, permission_id)
);
```

**Fields**:
- `id`: Primary key
- `usergroup_id`: Foreign key to usergroups
- `permission_id`: Foreign key to permissions
- `permission_value`: Value for the permission
  - `NULL` or `-1`: Boolean permission (on/off)
  - `> 0`: Maximum allowed value (e.g., 5 feeds)
  - `-2`: Unlimited

**File**: `DB/Scripts/04_usergroup_permissions.sql`

### `userfeeds`

**Purpose**: Store user's custom news feeds

**Schema**:
```sql
CREATE TABLE userfeeds (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    feedname VARCHAR(100) NOT NULL,
    stocks TEXT[] NOT NULL,
    sources TEXT[] NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_userfeeds_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);
```

**Fields**:
- `id`: Primary key
- `user_id`: Foreign key to users (cascade delete)
- `feedname`: Name of the feed
- `stocks`: Array of stock symbols (e.g., `{"AAPL", "GOOGL"}`)
- `sources`: Array of news sources (e.g., `{"NewsAPI", "Bloomberg"}`)
- `created_at`: Feed creation timestamp

**Cascade Delete**: When user is deleted, all their feeds are deleted

**File**: `DB/Scripts/05_userfeeds.sql`

### `news`

**Purpose**: Store news articles

**Schema Details**: See `DB/Scripts/06_news.sql`

**Key Fields**:
- `article_id`: Unique article identifier
- `title`: Article title
- `description`: Article summary
- `content`: Full article text
- `pubDate`: Publication date
- `source_id`: News source identifier
- `sentiment`: Sentiment analysis result
- `keywords`: Article keywords
- And many more fields for comprehensive news data

**File**: `DB/Scripts/06_news.sql`

## ORM Models

### UserORM

**File**: `ORM/userORM.py`

**Class**: `UserORM`

**Table**: `users`

**Relationships**:
```python
usergroup = relationship("UserGroupORM", backref="users")
feeds = relationship("UserFeedORM", back_populates="user", cascade="all, delete-orphan")
```

**Computed Property**:
```python
@property
def permissions(self) -> dict[str, int | None]:
    """Returns user's permissions as dict {permission_name: value}"""
    if not self.usergroup:
        return {}
    return {
        link.permission.name: link.permission_value
        for link in self.usergroup.permission_links
    }
```

**Usage**:
```python
user = session.get(UserORM, user_id)
print(user.permissions)  # {"GET.NEWS": None, "ADD.FEED": 5}
print(user.feeds)  # List of UserFeedORM objects
```

### UserGroupORM

**File**: `ORM/userGroupORM.py`

**Class**: `UserGroupORM`

**Table**: `usergroups`

**Relationships**:
```python
permission_links = relationship("UserGroupPermissionORM", back_populates="usergroup")
```

### PermissionORM

**File**: `ORM/permissionORM.py`

**Class**: `PermissionORM`

**Table**: `permissions`

### UserGroupPermissionORM

**File**: `ORM/userGroupPermissionORM.py`

**Class**: `UserGroupPermissionORM`

**Table**: `usergroup_permissions`

**Relationships**:
```python
usergroup = relationship("UserGroupORM", back_populates="permission_links")
permission = relationship("PermissionORM")
```

### UserFeedORM

**File**: `ORM/userFeedORM.py`

**Class**: `UserFeedORM`

**Table**: `userfeeds`

**Relationships**:
```python
user = relationship("UserORM", back_populates="feeds")
```

### NewsArticleORM

**File**: `ORM/newsArticleORM.py`

**Class**: `NewsArticleORM`

**Table**: `news`

## Data Access Patterns

### CRUD Operations

CRUD operations are organized in `services/dbService/crud/`:

#### User CRUD

**File**: `services/dbService/crud/userCrud.py`

**Functions**:
```python
def create_user(db: Session, user: UserCreate) -> UserORM:
    """Create a new user with hashed password"""
    ...

def get_user_by_email(db: Session, email: str) -> UserORM:
    """Retrieve user by email"""
    ...
```

#### News CRUD

**Files**:
- `services/dbService/crud/newsInsert.py` - Create news articles
- `services/dbService/crud/newsGet.py` - Retrieve news

**Functions**:
```python
def create_news_article(article: NewsArticleORM, db: Session):
    """Insert news article into database"""
    ...

def get_news_for_feed(feed_id: int, db: Session) -> List[NewsArticle]:
    """Get news filtered by feed's stocks and sources"""
    ...
```

### Query Patterns

#### Simple Queries

```python
# Get by primary key
user = db.get(UserORM, user_id)

# Get by attribute
statement = select(UserORM).where(UserORM.email == email)
user = db.exec(statement).first()

# Get all
feeds = db.exec(select(UserFeedORM)).all()
```

#### Queries with Relationships

```python
# Load user with feeds
user = db.get(UserORM, user_id)
feeds = user.feeds  # Relationship automatically loaded

# Access nested relationships
for link in user.usergroup.permission_links:
    print(link.permission.name, link.permission_value)
```

#### Filtered Queries

```python
# Filter news by feed configuration
statement = select(NewsArticleORM).where(
    NewsArticleORM.source_id.in_(feed.sources)
)
news = db.exec(statement).all()
```

### Transactions

All database operations use transactions:

```python
# Create
new_feed = UserFeedORM(**data)
db.add(new_feed)
db.commit()
db.refresh(new_feed)  # Get auto-generated fields

# Update
feed.feedname = "Updated Name"
db.add(feed)  # SQLAlchemy tracks changes
db.commit()
db.refresh(feed)

# Delete
db.delete(feed)
db.commit()
```

## Database Initialization

**Script**: `DB/rebuild_db.py`

**Purpose**: Initialize database from scratch

**Process**:
1. Drop existing database (if exists)
2. Create new database
3. Execute SQL scripts from `DB/Scripts/` in order
4. Execute SQL data scripts from `DB/Insert/`

**Execution Order**: Defined in `DB/order.txt`

**Usage**:
```bash
cd DB
python rebuild_db.py
```

**WARNING**: This deletes all existing data.

## Constraints and Validation

### Database-Level Constraints

- **UNIQUE**: username, email, permission names
- **NOT NULL**: Required fields
- **FOREIGN KEY**: Referential integrity
- **CASCADE DELETE**: userfeeds deleted when user deleted
- **RESTRICT**: Cannot delete usergroup if users exist

### Application-Level Validation

Pydantic models validate data before database operations:

```python
class UserCreate(BaseModel):
    username: str
    email: EmailStr  # Validates email format
    password: str

class UserFeedCreate(BaseModel):
    feedname: str
    stocks: List[str]  # Must be a list
    sources: List[str]
```

## Indexes

Performance indexes for common queries:

- `users`: username, email
- Additional indexes as needed

## Migrations

**Current Approach**: SQL scripts in `DB/Scripts/`

**Alternative**: Alembic (installed but not used)

**Workflow**:
1. Modify SQL scripts
2. Run `rebuild_db.py` to apply changes (development)
3. For production, manually apply schema changes

## Data Integrity

### Cascading Deletes

- Deleting user → Deletes all their feeds
- Deleting usergroup_permission → No effect on users (just removes permission)

### Orphan Prevention

SQLAlchemy `cascade="all, delete-orphan"` prevents orphaned feeds.

## Performance Considerations

- **Connection Pooling**: SQLAlchemy manages connection pool
- **Indexes**: On frequently queried columns (email, username)
- **Lazy Loading**: Relationships loaded on access
- **Batch Operations**: Use bulk inserts for large datasets

## Best Practices

1. **Always use ORM**: Don't write raw SQL (prevents injection)
2. **Use sessions properly**: Via `Depends(get_db)`
3. **Commit transactions**: Always call `db.commit()` after changes
4. **Refresh after commit**: Get auto-generated fields with `db.refresh()`
5. **Handle errors**: Use try/except for database errors
6. **Validate input**: Use Pydantic before database operations
7. **Use relationships**: Let SQLAlchemy handle joins
8. **Index frequently queried columns**: Improve query performance

## Database Connection

**Configuration**: `services/dbService/database.py`

```python
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=True)
```

**Options**:
- `pool_pre_ping=True`: Test connections before use
- `echo=True`: Log all SQL queries (development)

**Session Factory**:
```python
def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
```
