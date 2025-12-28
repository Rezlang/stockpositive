# API Reference

Complete API endpoint documentation for the StockPositive v1 API.

## Base URL

```
http://localhost:8000
```

## Authentication

Most endpoints require authentication via JWT Bearer token.

**Header Format**:
```
Authorization: Bearer <access_token>
```

**How to obtain a token**: Use the `/users/login` endpoint.

## User Endpoints

### Register User

Create a new user account.

**Endpoint**: `POST /users/register`

**Authentication**: Not required

**Request Body** (`UserCreate`):
```json
{
  "username": "string",
  "email": "user@example.com",
  "phone_number": "string (optional)",
  "password": "string"
}
```

**Response** (`UserResponse`): `201 Created`
```json
{
  "id": 1,
  "username": "string",
  "email": "user@example.com",
  "phone_number": "string",
  "usergroup_id": 1,
  "is_active": true,
  "created_at": "2025-01-15T10:30:00Z",
  "permissions": {
    "GET.NEWS": null,
    "ADD.FEED": 5,
    "EDIT.FEED": null
  }
}
```

**Errors**:
- `400 Bad Request` - User already exists
- `422 Unprocessable Entity` - Invalid request data

**Implementation**: `routes/userRoutes.py:register_user()`

---

### Login

Authenticate and receive a JWT access token.

**Endpoint**: `POST /users/login`

**Authentication**: Not required

**Request Body** (OAuth2PasswordRequestForm):
```
username=user@example.com
password=your_password
```

**Content-Type**: `application/x-www-form-urlencoded`

**Note**: The field is named `username` but should contain the user's email address.

**Response** (`Token`): `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors**:
- `401 Unauthorized` - Incorrect email or password

**Token Expiration**: Configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 30 minutes)

**Implementation**: `routes/userRoutes.py:login()`

**Example with curl**:
```bash
curl -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=yourpassword"
```

---

### Get Current User

Retrieve the profile of the currently authenticated user.

**Endpoint**: `GET /users/me`

**Authentication**: Required (JWT Bearer token)

**Request**: No body

**Response** (`UserResponse`): `200 OK`
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "phone_number": "+1234567890",
  "usergroup_id": 2,
  "is_active": true,
  "created_at": "2025-01-15T10:30:00Z",
  "permissions": {
    "GET.NEWS": null,
    "LOAD.NEWS": null,
    "ADD.FEED": 10,
    "EDIT.FEED": null,
    "DELETE.FEED": null,
    "GET.FEEDS": null
  }
}
```

**Errors**:
- `401 Unauthorized` - Invalid or missing token
- `400 Bad Request` - Inactive user

**Implementation**: `routes/userRoutes.py:read_users_me()`

---

## News Endpoints

### Load News

Fetch news articles from external sources (NewsData.io) and store them in the database.

**Endpoint**: `GET /news/load-news`

**Authentication**: Required

**Permission**: `LOAD.NEWS` (boolean permission)

**Query Parameters**:
- `source` (string, optional): News source (default: "market")
- `symbols` (array[string], optional): Stock symbols to filter news (e.g., `["AAPL", "GOOGL"]`)

**Response** (`List[NewsArticle]`): `200 OK`
```json
[
  {
    "article_id": "string",
    "title": "string",
    "link": "https://example.com/article",
    "keywords": ["tech", "stocks"],
    "creator": ["Author Name"],
    "video_url": null,
    "description": "Article description...",
    "content": "Full article content...",
    "pubDate": "2025-01-15 10:30:00",
    "pubDateTZ": "UTC",
    "image_url": "https://example.com/image.jpg",
    "source_id": "newsapi",
    "source_priority": 1,
    "source_name": "NewsAPI",
    "source_url": "https://newsapi.org",
    "source_icon": "https://newsapi.org/icon.png",
    "language": "english",
    "country": ["us"],
    "category": ["business"],
    "ai_tag": "technology",
    "sentiment": "positive",
    "sentiment_stats": "{\"positive\": 0.8, \"negative\": 0.1, \"neutral\": 0.1}",
    "ai_region": "US",
    "ai_org": "TechCorp",
    "duplicate": false
  }
]
```

**Errors**:
- `401 Unauthorized` - Not authenticated
- `403 Forbidden` - Missing `LOAD.NEWS` permission
- `500 Internal Server Error` - External API failure

**Implementation**: `routes/news_routes.py:load_market_news()`

**Example**:
```bash
curl -X GET "http://localhost:8000/news/load-news?source=market&symbols=AAPL&symbols=GOOGL" \
  -H "Authorization: Bearer <token>"
```

---

### Get News for Feed

Retrieve news articles filtered by a specific feed's configuration (stocks and sources).

**Endpoint**: `GET /news/get-news`

**Authentication**: Required

**Permission**: `GET.NEWS` (boolean permission)

**Query Parameters**:
- `feedId` (integer, required): Feed ID to get news for

**Response** (`List[NewsArticle]`): `200 OK`
```json
[
  {
    "article_id": "abc123",
    "title": "Apple announces new product",
    "description": "Apple Inc. unveiled...",
    ...
  },
  {
    "article_id": "def456",
    "title": "Tech stocks rally",
    "description": "Technology stocks surged...",
    ...
  }
]
```

**Errors**:
- `401 Unauthorized` - Not authenticated
- `403 Forbidden` - Missing `GET.NEWS` permission
- `404 Not Found` - Feed not found

**Implementation**: `routes/news_routes.py:get_market_news()`

**Example**:
```bash
curl -X GET "http://localhost:8000/news/get-news?feedId=1" \
  -H "Authorization: Bearer <token>"
```

---

## Feed Endpoints

### Create Feed

Create a new personalized feed for the authenticated user.

**Endpoint**: `POST /feeds/add_feed`

**Authentication**: Required

**Permission**: `ADD.FEED` (value-based permission)
- The permission value must be >= the user's current number of feeds + 1
- Use `-2` for unlimited feeds

**Request Body** (`UserFeedCreate`):
```json
{
  "feedname": "My Tech Feed",
  "stocks": ["AAPL", "GOOGL", "MSFT"],
  "sources": ["NewsAPI", "Bloomberg"]
}
```

**Response** (`UserFeedResponse`): `200 OK`
```json
{
  "id": 1,
  "user_id": 5,
  "feedname": "My Tech Feed",
  "stocks": ["AAPL", "GOOGL", "MSFT"],
  "sources": ["NewsAPI", "Bloomberg"],
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Errors**:
- `401 Unauthorized` - Not authenticated
- `403 Forbidden` - Permission value insufficient (e.g., user has reached max feeds)
- `422 Unprocessable Entity` - Invalid request data

**Implementation**: `routes/feedRoutes.py:add_feed()`

**Example**:
```bash
curl -X POST "http://localhost:8000/feeds/add_feed" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "feedname": "My Tech Feed",
    "stocks": ["AAPL", "GOOGL"],
    "sources": ["NewsAPI"]
  }'
```

---

### Get User Feeds

Retrieve all feeds belonging to the authenticated user.

**Endpoint**: `GET /feeds/get_feeds`

**Authentication**: Required

**Permission**: `GET.FEEDS` (boolean permission)

**Request**: No parameters

**Response** (`List[UserFeedResponse]`): `200 OK`
```json
[
  {
    "id": 1,
    "user_id": 5,
    "feedname": "My Tech Feed",
    "stocks": ["AAPL", "GOOGL"],
    "sources": ["NewsAPI"],
    "created_at": "2025-01-15T10:30:00Z"
  },
  {
    "id": 2,
    "user_id": 5,
    "feedname": "Finance News",
    "stocks": ["JPM", "GS"],
    "sources": ["Bloomberg"],
    "created_at": "2025-01-16T08:00:00Z"
  }
]
```

**Errors**:
- `401 Unauthorized` - Not authenticated
- `403 Forbidden` - Missing `GET.FEEDS` permission

**Implementation**: `routes/feedRoutes.py:get_user_feeds()`

---

### Update Feed

Update an existing feed's configuration.

**Endpoint**: `PUT /feeds/edit_feed/{feed_id}`

**Authentication**: Required

**Permission**: `EDIT.FEED` (boolean permission)

**Path Parameters**:
- `feed_id` (integer): ID of feed to update

**Request Body** (`UserFeedUpdate`):
```json
{
  "feedname": "Updated Feed Name (optional)",
  "stocks": ["AAPL", "TSLA"] (optional)",
  "sources": ["NewsAPI", "Reuters"] (optional)"
}
```

**Note**: All fields are optional - only provided fields will be updated.

**Response** (`UserFeedResponse`): `200 OK`
```json
{
  "id": 1,
  "user_id": 5,
  "feedname": "Updated Feed Name",
  "stocks": ["AAPL", "TSLA"],
  "sources": ["NewsAPI", "Reuters"],
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Errors**:
- `401 Unauthorized` - Not authenticated
- `403 Forbidden` - Not authorized to edit this feed (ownership check)
- `404 Not Found` - Feed not found
- `422 Unprocessable Entity` - Invalid request data

**Ownership Verification**: Users can only edit their own feeds.

**Implementation**: `routes/feedRoutes.py:edit_feed()`

**Example**:
```bash
curl -X PUT "http://localhost:8000/feeds/edit_feed/1" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"feedname": "New Name", "stocks": ["AAPL"]}'
```

---

### Delete Feed

Delete a feed.

**Endpoint**: `DELETE /feeds/delete_feed/{feed_id}`

**Authentication**: Required

**Permission**: `DELETE.FEED` (boolean permission)

**Path Parameters**:
- `feed_id` (integer): ID of feed to delete

**Request**: No body

**Response**: `204 No Content`

**Errors**:
- `401 Unauthorized` - Not authenticated
- `403 Forbidden` - Not authorized to delete this feed (ownership check)
- `404 Not Found` - Feed not found

**Ownership Verification**: Users can only delete their own feeds.

**Implementation**: `routes/feedRoutes.py:delete_feed()`

**Example**:
```bash
curl -X DELETE "http://localhost:8000/feeds/delete_feed/1" \
  -H "Authorization: Bearer <token>"
```

---

### Get All Feeds (Admin)

Retrieve all feeds from all users. Admin-only endpoint.

**Endpoint**: `GET /feeds/get_all_feeds`

**Authentication**: Required

**Permission**: `ADMIN.GET.FEEDS` (boolean permission)

**Request**: No parameters

**Response** (`List[UserFeedResponse]`): `200 OK`
```json
[
  {
    "id": 1,
    "user_id": 5,
    "feedname": "User 5's Feed",
    "stocks": ["AAPL"],
    "sources": ["NewsAPI"],
    "created_at": "2025-01-15T10:30:00Z"
  },
  {
    "id": 2,
    "user_id": 8,
    "feedname": "User 8's Feed",
    "stocks": ["GOOGL"],
    "sources": ["Bloomberg"],
    "created_at": "2025-01-16T08:00:00Z"
  }
]
```

**Errors**:
- `401 Unauthorized` - Not authenticated
- `403 Forbidden` - Missing `ADMIN.GET.FEEDS` permission

**Implementation**: `routes/feedRoutes.py:get_all_feeds()`

---

## Error Response Format

All errors return a consistent JSON format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Common HTTP Status Codes

- **200 OK** - Successful GET request
- **201 Created** - Successful resource creation (POST)
- **204 No Content** - Successful deletion
- **400 Bad Request** - Invalid request or user error
- **401 Unauthorized** - Missing or invalid authentication token
- **403 Forbidden** - Insufficient permissions
- **404 Not Found** - Resource not found
- **422 Unprocessable Entity** - Pydantic validation error
- **500 Internal Server Error** - Server error

## Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

These interfaces allow you to:
- Try endpoints directly in the browser
- View request/response schemas
- Test authentication
- Explore all available endpoints

## Rate Limiting

**Current state**: No rate limiting implemented

**Recommendation**: Implement rate limiting for production to prevent abuse.

## API Versioning

**Current approach**: Directory-based (`/v1/`)

Future API versions would be added as `/v2/`, allowing multiple versions to run simultaneously.
