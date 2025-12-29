# OAuth Authentication Setup

This document explains the OAuth authentication implementation added to the StockPositive API.

## Overview

The API now supports three authentication methods:
1. **Email/Password** - Traditional registration and login
2. **Google OAuth** - Sign in with Google
3. **Apple OAuth** - Sign in with Apple (placeholder - requires Apple Developer credentials)

## Database Changes

### Updated Tables

#### `users` table
Added new columns:
- `is_superuser` - Boolean flag for admin privileges
- `is_verified` - Boolean flag for email verification status
- `username` - Now nullable (OAuth users may not have a username)
- `hashed_password` - Now nullable (OAuth users don't have passwords)

#### New `oauth_accounts` table
Stores OAuth provider information:
- `id` - Primary key
- `user_id` - Foreign key to users table
- `oauth_name` - Provider name (e.g., "google", "apple")
- `access_token` - OAuth access token
- `expires_at` - Token expiration timestamp
- `refresh_token` - OAuth refresh token (if provided)
- `account_id` - OAuth provider's user ID
- `account_email` - Email from OAuth provider

## API Endpoints

### Email/Password Authentication
- `POST /users/register` - Register new user with email/password
- `POST /users/login` - Login with email/password
- `GET /users/me` - Get current user profile

### Google OAuth
- `GET /users/google/authorize` - Initiates Google OAuth flow
- `GET /users/google/callback` - Handles Google OAuth callback

### Apple OAuth (Commented out - requires setup)
- `GET /users/apple/authorize` - Initiates Apple OAuth flow
- `GET /users/apple/callback` - Handles Apple OAuth callback

## Environment Variables

Add these to your `API/.env` file:

```bash
# Google OAuth Configuration
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret

# Apple OAuth Configuration (Optional)
APPLE_OAUTH_CLIENT_ID=com.yourcompany.yourapp
APPLE_OAUTH_CLIENT_SECRET=your-apple-client-secret
APPLE_TEAM_ID=your-team-id
APPLE_KEY_ID=your-key-id
APPLE_PRIVATE_KEY=your-private-key-content
```

## Setting Up Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Credentials"
4. Click "Create Credentials" > "OAuth 2.0 Client ID"
5. Configure the OAuth consent screen
6. Set authorized redirect URIs:
   - `http://localhost:8000/users/google/callback` (development)
   - `https://yourdomain.com/users/google/callback` (production)
7. Copy the Client ID and Client Secret to your `.env` file

## Setting Up Apple OAuth

Apple OAuth requires:
1. Apple Developer Account ($99/year)
2. App ID and Service ID configuration
3. Private key (.p8 file) from Apple Developer portal
4. Team ID and Key ID

Once you have these:
1. Uncomment the Apple OAuth code in:
   - `services/authService/oauthConfig.py`
   - `routes/userRoutes.py`
2. Add the credentials to your `.env` file
3. Update the redirect URLs in the code

## OAuth Flow

### Google OAuth Flow

1. User clicks "Sign in with Google" button in frontend
2. Frontend redirects to: `GET /users/google/authorize`
3. API redirects user to Google's authorization page
4. User authorizes the app on Google
5. Google redirects back to: `GET /users/google/callback?code=...`
6. API exchanges code for access token
7. API fetches user info from Google
8. API creates or links user account
9. API returns JWT token for subsequent requests

### User Account Creation

When a user signs in with OAuth for the first time:
1. Check if OAuth account exists (by provider + account_id)
2. If not, check if user with that email exists
3. If user exists, link OAuth account to existing user
4. If user doesn't exist, create new user:
   - Email from OAuth provider
   - No username or password
   - Assign to default user group (ID 3)
   - Mark as verified
5. Create OAuth account record
6. Return JWT token

## Testing

### Manual Testing with Google OAuth

You'll need actual Google OAuth credentials to test. Once configured:

1. Start the API server:
```bash
cd API/v1
uvicorn main:app --reload
```

2. Navigate to: `http://localhost:8000/users/google/authorize`
3. Complete the Google sign-in flow
4. You should receive a JWT token in the response

### Testing Email/Password

```bash
# Register a user
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!",
    "phone_number": null
  }'

# Login
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=TestPass123!"
```

## Security Considerations

1. **HTTPS Required** - Use HTTPS in production for all OAuth flows
2. **Secure Token Storage** - Store OAuth tokens securely
3. **Token Refresh** - Implement token refresh logic for long-lived sessions
4. **Redirect URI Validation** - Ensure redirect URIs are properly validated
5. **State Parameter** - httpx-oauth handles CSRF protection with state parameter

## Migration Path

To apply the database changes:

1. Rebuild the database:
```bash
cd DB
python rebuild_db.py
```

2. Or manually run the migration:
```sql
-- Add new columns to users table
ALTER TABLE users
  ALTER COLUMN username DROP NOT NULL,
  ALTER COLUMN hashed_password DROP NOT NULL,
  ADD COLUMN is_superuser BOOLEAN DEFAULT FALSE NOT NULL,
  ADD COLUMN is_verified BOOLEAN DEFAULT FALSE NOT NULL;

-- Create oauth_accounts table (already in 07_oauth_accounts.sql)
```

## Files Changed

- `DB/Scripts/03_users.sql` - Updated users table schema
- `DB/Scripts/07_oauth_accounts.sql` - New OAuth accounts table
- `DB/order.txt` - Added new SQL script to execution order
- `API/v1/ORM/userORM.py` - Updated User ORM model
- `API/v1/ORM/oauthAccountORM.py` - New OAuth Account ORM model
- `API/v1/routes/userRoutes.py` - Added OAuth routes and logic
- `API/v1/services/authService/oauthConfig.py` - OAuth client configuration
- `API/v1/requirements.txt` - Added fastapi-users and httpx-oauth
- `API/.env` - Added OAuth environment variables (template)

## Next Steps

1. Obtain Google OAuth credentials from Google Cloud Console
2. Update `.env` file with actual credentials
3. Rebuild database to apply schema changes
4. Test OAuth flow with real credentials
5. (Optional) Set up Apple OAuth when ready
6. Update frontend to include OAuth sign-in buttons
7. Implement proper error handling and user feedback
8. Add email verification flow
9. Implement token refresh logic