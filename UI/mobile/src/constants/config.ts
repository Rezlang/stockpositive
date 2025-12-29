// App configuration constants

export const API_CONFIG = {
  // Update this with your actual API URL
  BASE_URL: 'http://localhost:8000',
  TIMEOUT: 10000,
} as const;

export const STORAGE_KEYS = {
  THEME: '@stockpositive/theme',
  AUTH_TOKEN: '@stockpositive/auth_token',
  ACTIVE_FEED_ID: '@stockpositive/active_feed_id',
} as const;

// Available news sources (can be fetched from API if endpoint exists)
export const NEWS_SOURCES = [
  { id: 'market', name: 'Market News', icon: 'trending-up' },
  { id: 'bloomberg', name: 'Bloomberg', icon: 'newspaper' },
  { id: 'reuters', name: 'Reuters', icon: 'globe' },
  { id: 'wsj', name: 'Wall Street Journal', icon: 'document-text' },
  { id: 'cnbc', name: 'CNBC', icon: 'tv' },
  { id: 'yahoo', name: 'Yahoo Finance', icon: 'logo-yahoo' },
] as const;

// Popular stock symbols for quick selection
export const POPULAR_STOCKS = [
  'AAPL',
  'GOOGL',
  'MSFT',
  'AMZN',
  'TSLA',
  'META',
  'NVDA',
  'JPM',
  'V',
  'JNJ',
] as const;
