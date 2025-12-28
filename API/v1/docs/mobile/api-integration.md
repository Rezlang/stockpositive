# API Integration

Guide for integrating the mobile app with the StockPositive v1 backend API.

## API Client Setup

### Base Configuration

**File**: `src/services/api/client.ts`

```typescript
import axios from 'axios';
import { getToken } from '../storage/tokenStorage';
import { store } from '../../store/store';
import { clearAuth } from '../../store/slices/authSlice';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add JWT token
apiClient.interceptors.request.use(
  async (config) => {
    const token = await getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - Handle errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      store.dispatch(clearAuth());
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

## News Service

**File**: `src/services/api/newsService.ts`

```typescript
import apiClient from './client';
import { NewsArticle } from '../../types/news.types';

export const loadNews = async (source: string = 'market', symbols?: string[]): Promise<NewsArticle[]> => {
  const params = new URLSearchParams();
  params.append('source', source);
  if (symbols) {
    symbols.forEach(symbol => params.append('symbols', symbol));
  }
  
  const response = await apiClient.get<NewsArticle[]>(`/news/load-news?${params}`);
  return response.data;
};

export const getNewsForFeed = async (feedId: number): Promise<NewsArticle[]> => {
  const response = await apiClient.get<NewsArticle[]>(`/news/get-news?feedId=${feedId}`);
  return response.data;
};
```

## Feeds Service

**File**: `src/services/api/feedsService.ts`

```typescript
import apiClient from './client';
import { Feed, FeedCreate, FeedUpdate } from '../../types/feed.types';

export const getUserFeeds = async (): Promise<Feed[]> => {
  const response = await apiClient.get<Feed[]>('/feeds/get_feeds');
  return response.data;
};

export const createFeed = async (feedData: FeedCreate): Promise<Feed> => {
  const response = await apiClient.post<Feed>('/feeds/add_feed', feedData);
  return response.data;
};

export const updateFeed = async (feedId: number, feedData: FeedUpdate): Promise<Feed> => {
  const response = await apiClient.put<Feed>(`/feeds/edit_feed/${feedId}`, feedData);
  return response.data;
};

export const deleteFeed = async (feedId: number): Promise<void> => {
  await apiClient.delete(`/feeds/delete_feed/${feedId}`);
};
```

## Error Handling

### API Error Handler

**File**: `src/utils/apiErrors.ts`

```typescript
import { AxiosError } from 'axios';

export const handleApiError = (error: unknown): string => {
  if (error instanceof AxiosError) {
    if (error.response) {
      return error.response.data?.detail || 'An error occurred';
    }
    if (error.request) {
      return 'No response from server';
    }
  }
  return 'An unexpected error occurred';
};
```

### Usage in Components

```typescript
try {
  await dispatch(someApiCall()).unwrap();
} catch (error) {
  Alert.alert('Error', handleApiError(error));
}
```

## TypeScript Types

### News Types

**File**: `src/types/news.types.ts`

```typescript
export interface NewsArticle {
  article_id: string;
  title: string;
  description: string;
  link: string;
  pubDate: string;
  source_name: string;
  sentiment?: string;
  image_url?: string;
  keywords?: string[];
}
```

### Feed Types

**File**: `src/types/feed.types.ts`

```typescript
export interface Feed {
  id: number;
  user_id: number;
  feedname: string;
  stocks: string[];
  sources: string[];
  created_at: string;
}

export interface FeedCreate {
  feedname: string;
  stocks: string[];
  sources: string[];
}

export interface FeedUpdate {
  feedname?: string;
  stocks?: string[];
  sources?: string[];
}
```

## Loading States

Handle loading states in components:

```typescript
const [loading, setLoading] = useState(false);

const fetchData = async () => {
  setLoading(true);
  try {
    const data = await getNewsForFeed(feedId);
    // Handle data
  } catch (error) {
    Alert.alert('Error', handleApiError(error));
  } finally {
    setLoading(false);
  }
};
```

## Best Practices

1. **Always handle errors** with try/catch
2. **Show loading states** to users
3. **Validate data** before sending to API
4. **Use TypeScript types** for type safety
5. **Implement retry logic** for failed requests
6. **Cache API responses** when appropriate
7. **Handle offline scenarios**
8. **Use request cancellation** for search inputs

## Next Steps

- [State Management](state-management.md)
- [UI Components](ui-components.md)
- [Extending](extending.md)
