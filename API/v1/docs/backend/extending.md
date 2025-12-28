# Extending the Backend

This guide explains how to add new features to the StockPositive v1 API.

## Adding a New API Endpoint

Follow these steps to add a new endpoint to the API.

### Step 1: Create Route Handler

Add the endpoint to an existing router or create a new one.

**Example**: Add a GET endpoint to retrieve feed details

**File**: `routes/feedRoutes.py`

```python
@router.get("/get_feed/{feed_id}",
            response_model=UserFeedResponse,
            dependencies=[require_permissions(["GET.FEEDS"])])
def get_feed_details(
    feed_id: int,
    current_user: UserORM = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get details of a specific feed"""
    feed = db.get(UserFeedORM, feed_id)
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")
    if feed.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return feed
```

### Step 2: Define Pydantic Models (if needed)

Create request/response models in `models/` directory.

**File**: `models/feedDetails.py` (example)

```python
from pydantic import BaseModel
from typing import List, Optional

class FeedDetailsResponse(BaseModel):
    id: int
    feedname: str
    stocks: List[str]
    sources: List[str]
    article_count: int
    last_updated: str

    class Config:
        from_attributes = True
```

### Step 3: Add Permission Check (if needed)

Use `require_permissions()` or `require_permission_with_max()` as dependencies.

**Boolean Permission**:
```python
dependencies=[require_permissions(["PERMISSION.NAME"])]
```

**Value-Based Permission**:
```python
dependencies=[require_permission_with_max("PERMISSION.NAME", min_value=1)]
```

### Step 4: Implement Business Logic

If complex logic is needed, create a service function in `services/`.

**File**: `services/feedService.py` (example)

```python
from sqlmodel import Session, select
from ORM.userFeedORM import UserFeedORM

def get_feed_statistics(feed_id: int, db: Session) -> dict:
    """Get statistics for a feed"""
    feed = db.get(UserFeedORM, feed_id)
    if not feed:
        return None

    # Calculate statistics
    article_count = calculate_article_count(feed, db)

    return {
        "feed_id": feed_id,
        "article_count": article_count,
        "stocks": feed.stocks,
        "sources": feed.sources
    }
```

### Step 5: Register Router (if new)

If you created a new router file, register it in `main.py`.

**File**: `main.py`

```python
from routes import new_router

app.include_router(new_router.router, prefix="/new", tags=["new"])
```

### Step 6: Test the Endpoint

Use the interactive documentation or pytest.

**Interactive Testing**:
1. Start server: `uvicorn main:app --reload`
2. Open [http://localhost:8000/docs](http://localhost:8000/docs)
3. Try the new endpoint

**Automated Testing**:

**File**: `test/test_feeds.py`

```python
def test_get_feed_details(client, auth_headers):
    # Create a feed first
    response = client.post(
        "/feeds/add_feed",
        headers=auth_headers,
        json={"feedname": "Test", "stocks": ["AAPL"], "sources": ["NewsAPI"]}
    )
    feed_id = response.json()["id"]

    # Get feed details
    response = client.get(
        f"/feeds/get_feed/{feed_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["feedname"] == "Test"
```

---

## Adding a Database Table

### Step 1: Create SQL Schema

Create a numbered SQL file in `DB/Scripts/`.

**File**: `DB/Scripts/07_create_feed_analytics.sql`

```sql
CREATE TABLE feed_analytics (
    id SERIAL PRIMARY KEY,
    feed_id INTEGER NOT NULL,
    view_count INTEGER DEFAULT 0,
    last_viewed TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_analytics_feed
        FOREIGN KEY (feed_id)
        REFERENCES userfeeds(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_feed_analytics_feed_id ON feed_analytics(feed_id);
```

### Step 2: Update Execution Order

Add the new script to `DB/order.txt`.

**File**: `DB/order.txt`

```
01_usergroups.sql
02_permissions.sql
03_users.sql
04_usergroup_permissions.sql
05_userfeeds.sql
06_news.sql
07_create_feed_analytics.sql
```

### Step 3: Create ORM Model

Create SQLAlchemy model in `ORM/` directory.

**File**: `ORM/feedAnalyticsORM.py`

```python
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class FeedAnalyticsORM(Base):
    __tablename__ = "feed_analytics"

    id = Column(Integer, primary_key=True)
    feed_id = Column(Integer, ForeignKey("userfeeds.id"), nullable=False)
    view_count = Column(Integer, default=0)
    last_viewed = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    feed = relationship("UserFeedORM", backref="analytics")
```

### Step 4: Create Pydantic Models

Create request/response schemas in `models/`.

**File**: `models/feedAnalytics.py`

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FeedAnalyticsCreate(BaseModel):
    feed_id: int
    view_count: int = 0

class FeedAnalyticsResponse(BaseModel):
    id: int
    feed_id: int
    view_count: int
    last_viewed: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
```

### Step 5: Add CRUD Operations

Create CRUD functions in `services/dbService/crud/`.

**File**: `services/dbService/crud/analyticsCrud.py`

```python
from sqlmodel import Session, select
from ORM.feedAnalyticsORM import FeedAnalyticsORM
from models.feedAnalytics import FeedAnalyticsCreate

def create_analytics(db: Session, analytics: FeedAnalyticsCreate) -> FeedAnalyticsORM:
    db_analytics = FeedAnalyticsORM(**analytics.dict())
    db.add(db_analytics)
    db.commit()
    db.refresh(db_analytics)
    return db_analytics

def get_analytics_by_feed(db: Session, feed_id: int) -> FeedAnalyticsORM:
    statement = select(FeedAnalyticsORM).where(FeedAnalyticsORM.feed_id == feed_id)
    return db.exec(statement).first()

def increment_view_count(db: Session, feed_id: int):
    analytics = get_analytics_by_feed(db, feed_id)
    if analytics:
        analytics.view_count += 1
        analytics.last_viewed = datetime.now(timezone.utc)
        db.add(analytics)
        db.commit()
```

### Step 6: Rebuild Database

Run the database initialization script.

```bash
cd DB
python rebuild_db.py
```

**WARNING**: This deletes all existing data.

---

## Adding External API Integration

### Step 1: Add API Key to `.env`

**File**: `API/.env`

```env
NEW_API_KEY=your_api_key_here
```

### Step 2: Install Required Package

Add to `requirements.txt` and install.

**File**: `API/v1/requirements.txt`

```
new-api-package>=1.0.0
```

```bash
pip install new-api-package
```

### Step 3: Create Service Function

Follow the pattern in `services/retrieveNews.py`.

**File**: `services/newApiService.py`

```python
import os
from dotenv import load_dotenv
from typing import List
from new_api_package import NewAPIClient

load_dotenv()
API_KEY = os.getenv("NEW_API_KEY")

if not API_KEY:
    raise ValueError("NEW_API_KEY must be set in environment variables")

client = NewAPIClient(api_key=API_KEY)

def fetch_data_from_api(param: str) -> List[dict]:
    """Fetch data from external API"""
    try:
        response = client.get_data(param)
        return transform_response(response)
    except Exception as e:
        print(f"Error fetching data: {e}")
        raise

def transform_response(response: dict) -> List[dict]:
    """Transform API response to internal format"""
    return [
        {
            "id": item["id"],
            "name": item["name"],
            # ... transform fields
        }
        for item in response.get("items", [])
    ]
```

### Step 4: Use in Route Handler

Call the service function from a route.

```python
from services.newApiService import fetch_data_from_api

@router.get("/external-data")
def get_external_data(query: str):
    """Get data from external API"""
    data = fetch_data_from_api(query)
    return data
```

### Step 5: Handle API Errors

Add error handling for API failures.

```python
from fastapi import HTTPException

try:
    data = fetch_data_from_api(query)
except Exception as e:
    raise HTTPException(
        status_code=503,
        detail=f"External API unavailable: {str(e)}"
    )
```

---

## Adding a New Permission

### Step 1: Insert Permission into Database

Add to `DB/Insert/` directory or insert manually.

**SQL**:
```sql
INSERT INTO permissions (name, description, perm_max) VALUES
('NEW.PERMISSION', 'Description of permission', NULL);  -- NULL for boolean
-- OR
('VALUE.PERMISSION', 'Description of value permission', 10);  -- 10 for max value
```

### Step 2: Assign to User Groups

Link permission to groups via `usergroup_permissions`.

**SQL**:
```sql
-- Assign boolean permission to group 2
INSERT INTO usergroup_permissions (usergroup_id, permission_id, permission_value) VALUES
(2, (SELECT id FROM permissions WHERE name = 'NEW.PERMISSION'), NULL);

-- Assign value-based permission (max 5) to group 2
INSERT INTO usergroup_permissions (usergroup_id, permission_id, permission_value) VALUES
(2, (SELECT id FROM permissions WHERE name = 'VALUE.PERMISSION'), 5);
```

### Step 3: Use Permission in Routes

Add permission check to route dependencies.

**Boolean Permission**:
```python
@router.get("/protected",
            dependencies=[require_permissions(["NEW.PERMISSION"])])
def protected_endpoint():
    ...
```

**Value-Based Permission**:
```python
@router.post("/limited",
             dependencies=[require_permission_with_max(
                 "VALUE.PERMISSION",
                 value_getter=lambda u: calculate_current_value(u)
             )])
def limited_endpoint():
    ...
```

---

## Common Patterns and Anti-Patterns

### Do's

✅ **Use dependency injection** for database sessions and auth
```python
def my_endpoint(db: Session = Depends(get_db), current_user: UserORM = Depends(get_current_active_user)):
    ...
```

✅ **Validate with Pydantic** before database operations
```python
@router.post("/create", response_model=ResponseModel)
def create(data: CreateModel, db: Session = Depends(get_db)):
    ...
```

✅ **Check ownership** before modifying user resources
```python
if resource.user_id != current_user.id:
    raise HTTPException(status_code=403, detail="Not authorized")
```

✅ **Use ORM relationships** instead of manual joins
```python
user = db.get(UserORM, user_id)
feeds = user.feeds  # Use relationship
```

✅ **Commit and refresh** after database changes
```python
db.add(new_obj)
db.commit()
db.refresh(new_obj)
```

### Don'ts

❌ **Don't return ORM objects directly** (use Pydantic response models)
```python
# Bad
return db.get(UserORM, user_id)

# Good
return UserResponse.model_validate(db.get(UserORM, user_id), from_attributes=True)
```

❌ **Don't put business logic in routes** (use service layer)
```python
# Bad
@router.get("/complex")
def complex_endpoint():
    # 50 lines of business logic here
    ...

# Good
@router.get("/complex")
def complex_endpoint():
    result = complex_service_function()
    return result
```

❌ **Don't skip permission checks** on protected resources
```python
# Bad
@router.delete("/feed/{feed_id}")
def delete_feed(feed_id: int):
    ...

# Good
@router.delete("/feed/{feed_id}",
               dependencies=[require_permissions(["DELETE.FEED"])])
def delete_feed(feed_id: int):
    ...
```

❌ **Don't hardcode configuration** (use environment variables)
```python
# Bad
API_KEY = "hardcoded_key_123"

# Good
API_KEY = os.getenv("API_KEY")
```

---

## Testing New Features

### Unit Tests

Test individual functions in isolation.

```python
def test_service_function():
    result = my_service_function(param)
    assert result == expected_value
```

### Integration Tests

Test endpoints with database.

```python
def test_create_endpoint(client, test_db):
    response = client.post("/create", json={"data": "value"})
    assert response.status_code == 201
    assert "id" in response.json()
```

### Permission Tests

Test permission enforcement.

```python
def test_unauthorized_access(client):
    response = client.get("/protected")  # No auth
    assert response.status_code == 401

def test_forbidden_access(client, basic_user_token):
    response = client.get("/admin-only", headers={"Authorization": f"Bearer {basic_user_token}"})
    assert response.status_code == 403
```

---

## Deployment Checklist

Before deploying new features:

- [ ] Write tests for new endpoints
- [ ] Test permission checks
- [ ] Validate request/response models
- [ ] Check error handling
- [ ] Update API documentation
- [ ] Test database migrations
- [ ] Verify environment variables
- [ ] Check for security vulnerabilities
- [ ] Test with production-like data
- [ ] Review code for best practices

---

## Getting Help

- **FastAPI Docs**: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- **SQLAlchemy Docs**: [https://docs.sqlalchemy.org/](https://docs.sqlalchemy.org/)
- **Pydantic Docs**: [https://docs.pydantic.dev/](https://docs.pydantic.dev/)
- **Interactive API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
