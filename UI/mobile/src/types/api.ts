// API Request/Response Types

// Generic API response wrapper
export interface ApiResponse<T> {
  data: T;
  status: number;
  ok: boolean;
}

export interface ApiError {
  message: string;
  status: number;
  code?: string;
}

// Auth types
export interface RegisterRequest {
  username: string;
  email: string;
  phone_number?: string;
  password: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserResponse {
  id: number;
  username: string;
  email: string;
  phone_number: string | null;
  usergroup_id: number;
  is_active: boolean;
  created_at: string;
  permissions: Record<string, number | null>;
}

// Feed types
export interface UserFeedResponse {
  id: number;
  user_id: number;
  feedname: string;
  stocks: string[];
  sources: string[];
  created_at: string;
}

export interface CreateFeedRequest {
  feedname: string;
  stocks: string[];
  sources: string[];
}

export interface UpdateFeedRequest {
  feedname?: string;
  stocks?: string[];
  sources?: string[];
}

// News types
export type SentimentType = 'positive' | 'negative' | 'neutral' | null;

export interface NewsArticle {
  id: number | null;
  title: string | null;
  description: string | null;
  content: string | null;
  link: string | null;
  imagelink: string | null;
  keywords: string[] | null;
  creator: string[] | null;
  symbols: string[] | null;
  pubdate: string | null;
  sourcename: string | null;
  sentiment: string | null;
  aisummary: string | null;
}
