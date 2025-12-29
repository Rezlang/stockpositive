# React Native Mobile App Overview

This document describes the architecture and design patterns for the StockPositive React Native mobile application.

## Purpose

The StockPositive mobile app provides a native mobile experience for:
- **Viewing personalized news feeds** based on selected stocks and sources
- **Monitoring stock prices** and market data with interactive charts
- **Managing custom feeds** to track specific stocks and news sources
- **Secure authentication** with JWT tokens
- **Real-time market updates** from the v1 backend API

## Technology Stack

### Core Framework
- **React Native** - Cross-platform mobile framework (iOS & Android)
- **TypeScript** - Type-safe JavaScript
- **Expo** (recommended) - Simplified React Native development and deployment

### Recommended Dependencies

#### Navigation
- **React Navigation 6+** - Navigation library for React Native
- **@react-navigation/native**
- **@react-navigation/stack**
- **@react-navigation/bottom-tabs**

#### State Management
- **Redux Toolkit** (recommended) - Predictable state container
  - OR **Zustand** - Lightweight alternative

#### UI Components
- **React Native Paper** (Material Design)
  - OR **NativeBase** (Component library)
  - OR **React Native Elements**

#### API Communication
- **Axios** - HTTP client for API calls
- **@tanstack/react-query** (optional) - Data fetching and caching

#### Storage
- **@react-native-async-storage/async-storage** - Persistent local storage for tokens

#### Charts
- **React Native Chart Kit** - Stock price visualization
- **Victory Native** - Alternative charting library

#### Forms
- **React Hook Form** - Form validation and management
- **Yup** - Schema validation

## App Architecture

### High-Level Structure

```
Mobile App
    ├─ Navigation
    │   ├─ Auth Stack (Login, Register)
    │   └─ Main Stack
    │       ├─ Tab Navigator
    │       │   ├─ News Feed
    │       │   ├─ Stock Chart
    │       │   └─ Feed Options
    │       └─ Modal Screens
    ├─ State Management (Redux/Zustand)
    │   ├─ Auth State
    │   ├─ User State
    │   ├─ News State
    │   └─ Feeds State
    ├─ API Layer
    │   ├─ Axios Client
    │   ├─ API Services
    │   └─ Interceptors
    └─ Components
        ├─ Screens
        ├─ UI Components
        └─ Shared Components
```

### Directory Structure

```
src/
├── screens/              # Screen components
│   ├── auth/
│   │   ├── LoginScreen.tsx
│   │   └── RegisterScreen.tsx
│   ├── news/
│   │   └── NewsFeedScreen.tsx
│   ├── stocks/
│   │   └── StockChartScreen.tsx
│   └── feeds/
│       └── FeedOptionsScreen.tsx
├── components/           # Reusable UI components
│   ├── common/
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   └── Loading.tsx
│   ├── news/
│   │   ├── NewsCard.tsx
│   │   └── NewsList.tsx
│   └── stocks/
│       └── StockChart.tsx
├── navigation/           # Navigation configuration
│   ├── AuthNavigator.tsx
│   ├── MainNavigator.tsx
│   └── RootNavigator.tsx
├── store/                # Redux/Zustand state
│   ├── slices/
│   │   ├── authSlice.ts
│   │   ├── newsSlice.ts
│   │   └── feedsSlice.ts
│   └── store.ts
├── services/             # API and business logic
│   ├── api/
│   │   ├── client.ts
│   │   ├── authService.ts
│   │   ├── newsService.ts
│   │   └── feedsService.ts
│   └── storage/
│       └── tokenStorage.ts
├── types/                # TypeScript types
│   ├── api.types.ts
│   ├── news.types.ts
│   └── feed.types.ts
├── hooks/                # Custom React hooks
│   ├── useAuth.ts
│   ├── useNews.ts
│   └── useFeeds.ts
├── utils/                # Utility functions
│   ├── validators.ts
│   └── formatters.ts
└── constants/            # App constants
    ├── api.ts
    └── theme.ts
```

## Key Features

### 1. News Feed

**Screen**: `NewsFeedScreen`

**Features**:
- Display list of news articles from user's feeds
- Filter by stock symbols and sources
- Pull-to-refresh for latest news
- Infinite scroll pagination
- Article sentiment indicators
- Open articles in web view or browser

**Components**:
- `NewsList` - FlatList of articles
- `NewsCard` - Individual article display
- `FilterBar` - Filter controls
- `SentimentBadge` - Sentiment indicator

### 2. Stock Charts

**Screen**: `StockChartScreen`

**Features**:
- Interactive price charts (candlestick, line)
- Multiple timeframes (1D, 1W, 1M, 1Y)
- Real-time price updates
- Stock search and selection
- Technical indicators (optional)

**Components**:
- `StockChart` - Chart visualization
- `StockSelector` - Stock search/select
- `TimeframeSelector` - Timeframe buttons
- `PriceDisplay` - Current price and change

### 3. Feed Management

**Screen**: `FeedOptionsScreen`

**Features**:
- Create new feeds
- Edit existing feeds
- Delete feeds
- Select stocks and sources
- View feed statistics

**Components**:
- `FeedList` - List of user's feeds
- `FeedForm` - Create/edit feed form
- `StockPicker` - Multi-select stock picker
- `SourcePicker` - News source selector

### 4. Authentication

**Screens**: `LoginScreen`, `RegisterScreen`

**Features**:
- Email/password authentication
- JWT token storage
- Auto-login with saved token
- Secure token handling
- Logout functionality

**Components**:
- `AuthForm` - Login/register form
- `InputField` - Text input with validation
- `PasswordInput` - Password field with visibility toggle

## State Management

### Redux Toolkit Approach

**Store Structure**:
```typescript
{
  auth: {
    user: User | null,
    token: string | null,
    isAuthenticated: boolean,
    loading: boolean
  },
  news: {
    articles: NewsArticle[],
    loading: boolean,
    error: string | null,
    page: number,
    hasMore: boolean
  },
  feeds: {
    feeds: Feed[],
    selectedFeed: Feed | null,
    loading: boolean,
    error: string | null
  }
}
```

### Zustand Alternative

**Simpler state management**:
```typescript
const useAuthStore = create((set) => ({
  user: null,
  token: null,
  login: (token, user) => set({ token, user }),
  logout: () => set({ token: null, user: null })
}));
```

## Navigation Structure

### Auth Stack

```
AuthStack
├─ Login Screen
└─ Register Screen
```

### Main Stack (After Login)

```
Main Stack
└─ Tab Navigator (Bottom Tabs)
    ├─ News Tab → News Feed Screen
    ├─ Charts Tab → Stock Chart Screen
    └─ Feeds Tab → Feed Options Screen
```

## Data Flow

### Typical User Flow

```
1. App Launch
   ↓
2. Check for stored token (AsyncStorage)
   ├─ Token exists → Load user data → Main Stack
   └─ No token → Auth Stack

3. User Login
   ↓
4. POST /users/login → Receive JWT token
   ↓
5. Store token in AsyncStorage
   ↓
6. Navigate to Main Stack

7. View News Feed
   ↓
8. GET /news/get-news?feedId=1 (with JWT)
   ↓
9. Display news articles

10. Create Feed
    ↓
11. POST /feeds/add_feed (with JWT)
    ↓
12. Update local state
    ↓
13. Refresh feed list
```

## API Integration

### Axios Configuration

**Base setup**:
```typescript
const apiClient = axios.create({
  baseURL: 'http://your-api-url.com',
  timeout: 10000,
});

// Request interceptor (add JWT token)
apiClient.interceptors.request.use((config) => {
  const token = await getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor (handle errors)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired, logout user
      logout();
    }
    return Promise.reject(error);
  }
);
```

## Performance Considerations

- **FlatList virtualization** for large news lists
- **Image caching** with react-native-fast-image
- **Memoization** with useMemo and useCallback
- **Code splitting** with lazy loading
- **Debounced search** for stock/news search
- **Optimistic updates** for better UX

## Offline Support

- **Cache news articles** locally
- **Queue API calls** when offline
- **Sync when back online**
- **Show offline indicator**

## Security

- **Secure token storage** with AsyncStorage or Keychain
- **HTTPS only** for API calls
- **Input validation** on forms
- **Sanitize user input** before API calls
- **Handle token expiration** gracefully

## Platform-Specific Considerations

### iOS
- Safe area handling with SafeAreaView
- iOS-specific navigation patterns
- App Store submission requirements

### Android
- Android permissions (if needed)
- Back button handling
- Google Play Store requirements

## Development Workflow

1. **Setup**: `npx create-expo-app stockpositive-mobile`
2. **Install dependencies**: `npm install`
3. **Configure API**: Update base URL in API client
4. **Run**: `npx expo start`
5. **Test on device**: Scan QR code with Expo Go
6. **Build**: `eas build` (Expo) or native builds

## Next Steps

See the following documentation for detailed implementation:
- [Setup Guide](setup.md) - Project setup and dependencies
- [Authentication](authentication.md) - JWT authentication implementation
- [API Integration](api-integration.md) - Connecting to the backend
- [State Management](state-management.md) - Redux Toolkit patterns
- [UI Components](ui-components.md) - Component architecture
- [Navigation](navigation.md) - Navigation setup
- [Extending](extending.md) - Adding new features
