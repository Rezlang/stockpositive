# State Management

Guide for managing application state with Redux Toolkit in the StockPositive mobile app.

## Redux Toolkit Overview

Redux Toolkit provides a standardized way to write Redux logic with less boilerplate.

**Benefits**:
- Less boilerplate code
- Built-in best practices
- TypeScript support
- Async logic with createAsyncThunk
- Immutable updates with Immer

## Store Configuration

**File**: `src/store/store.ts`

```typescript
import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import newsReducer from './slices/newsSlice';
import feedsReducer from './slices/feedsSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    news: newsReducer,
    feeds: feedsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false, // For AsyncStorage
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

## News Slice

**File**: `src/store/slices/newsSlice.ts`

```typescript
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { getNewsForFeed } from '../../services/api/newsService';
import { NewsArticle } from '../../types/news.types';

interface NewsState {
  articles: NewsArticle[];
  loading: boolean;
  error: string | null;
  selectedFeedId: number | null;
}

const initialState: NewsState = {
  articles: [],
  loading: false,
  error: null,
  selectedFeedId: null,
};

export const fetchNews = createAsyncThunk(
  'news/fetchNews',
  async (feedId: number, { rejectWithValue }) => {
    try {
      const articles = await getNewsForFeed(feedId);
      return { articles, feedId };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch news');
    }
  }
);

const newsSlice = createSlice({
  name: 'news',
  initialState,
  reducers: {
    clearNews: (state) => {
      state.articles = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchNews.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchNews.fulfilled, (state, action) => {
        state.loading = false;
        state.articles = action.payload.articles;
        state.selectedFeedId = action.payload.feedId;
      })
      .addCase(fetchNews.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearNews } = newsSlice.actions;
export default newsSlice.reducer;
```

## Feeds Slice

**File**: `src/store/slices/feedsSlice.ts`

```typescript
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import * as feedsApi from '../../services/api/feedsService';
import { Feed, FeedCreate, FeedUpdate } from '../../types/feed.types';

interface FeedsState {
  feeds: Feed[];
  loading: boolean;
  error: string | null;
}

const initialState: FeedsState = {
  feeds: [],
  loading: false,
  error: null,
};

export const fetchFeeds = createAsyncThunk('feeds/fetchFeeds', async (_, { rejectWithValue }) => {
  try {
    return await feedsApi.getUserFeeds();
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to fetch feeds');
  }
});

export const addFeed = createAsyncThunk(
  'feeds/addFeed',
  async (feedData: FeedCreate, { rejectWithValue }) => {
    try {
      return await feedsApi.createFeed(feedData);
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create feed');
    }
  }
);

export const editFeed = createAsyncThunk(
  'feeds/editFeed',
  async ({ feedId, feedData }: { feedId: number; feedData: FeedUpdate }, { rejectWithValue }) => {
    try {
      return await feedsApi.updateFeed(feedId, feedData);
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update feed');
    }
  }
);

export const removeFeed = createAsyncThunk(
  'feeds/removeFeed',
  async (feedId: number, { rejectWithValue }) => {
    try {
      await feedsApi.deleteFeed(feedId);
      return feedId;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to delete feed');
    }
  }
);

const feedsSlice = createSlice({
  name: 'feeds',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      // Fetch feeds
      .addCase(fetchFeeds.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchFeeds.fulfilled, (state, action) => {
        state.loading = false;
        state.feeds = action.payload;
      })
      .addCase(fetchFeeds.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Add feed
      .addCase(addFeed.fulfilled, (state, action) => {
        state.feeds.push(action.payload);
      })
      // Edit feed
      .addCase(editFeed.fulfilled, (state, action) => {
        const index = state.feeds.findIndex(f => f.id === action.payload.id);
        if (index !== -1) {
          state.feeds[index] = action.payload;
        }
      })
      // Remove feed
      .addCase(removeFeed.fulfilled, (state, action) => {
        state.feeds = state.feeds.filter(f => f.id !== action.payload);
      });
  },
});

export default feedsSlice.reducer;
```

## Custom Hooks

**File**: `src/hooks/useAppDispatch.ts`

```typescript
import { useDispatch } from 'react-redux';
import type { AppDispatch } from '../store/store';

export const useAppDispatch = () => useDispatch<AppDispatch>();
```

**File**: `src/hooks/useAppSelector.ts`

```typescript
import { TypedUseSelectorHook, useSelector } from 'react-redux';
import type { RootState } from '../store/store';

export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
```

## Using State in Components

```typescript
import React, { useEffect } from 'react';
import { View, FlatList } from 'react-native';
import { useAppDispatch, useAppSelector } from '../hooks';
import { fetchNews } from '../store/slices/newsSlice';
import NewsCard from '../components/news/NewsCard';

export default function NewsScreen() {
  const dispatch = useAppDispatch();
  const { articles, loading } = useAppSelector(state => state.news);

  useEffect(() => {
    dispatch(fetchNews(1)); // Feed ID 1
  }, []);

  return (
    <FlatList
      data={articles}
      renderItem={({ item }) => <NewsCard article={item} />}
      refreshing={loading}
      onRefresh={() => dispatch(fetchNews(1))}
    />
  );
}
```

## Best Practices

1. **Use createAsyncThunk** for async operations
2. **Normalize state** when possible
3. **Use selectors** for derived state
4. **Keep state minimal** - don't store computed values
5. **Use TypeScript** for type safety
6. **Handle errors** in extraReducers
7. **Use custom hooks** (useAppDispatch, useAppSelector)

## Alternative: Zustand

For simpler projects, consider Zustand:

```typescript
import create from 'zustand';

interface AuthState {
  user: User | null;
  token: string | null;
  login: (token: string, user: User) => void;
  logout: () => void;
}

const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  login: (token, user) => set({ token, user }),
  logout: () => set({ token: null, user: null }),
}));
```

## Next Steps

- [UI Components](ui-components.md)
- [Navigation](navigation.md)
- [Extending](extending.md)
