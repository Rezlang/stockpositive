import { API_CONFIG } from '@/constants/config';
import { ApiResponse, ApiError } from '@/types/api';
import { storageService } from '@/services/storage';

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';

interface RequestOptions {
  body?: object;
  params?: Record<string, string | string[]>;
  requiresAuth?: boolean;
}

class ApiClient {
  private baseUrl: string;
  private timeout: number;
  private onUnauthorized?: () => void;

  constructor() {
    this.baseUrl = API_CONFIG.BASE_URL;
    this.timeout = API_CONFIG.TIMEOUT;
  }

  setUnauthorizedHandler(handler: () => void) {
    this.onUnauthorized = handler;
  }

  private buildUrl(endpoint: string, params?: Record<string, string | string[]>): string {
    const url = new URL(endpoint, this.baseUrl);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (Array.isArray(value)) {
          value.forEach((v) => url.searchParams.append(key, v));
        } else {
          url.searchParams.append(key, value);
        }
      });
    }
    return url.toString();
  }

  private async getHeaders(requiresAuth: boolean): Promise<HeadersInit> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (requiresAuth) {
      const token = await storageService.getToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    return headers;
  }

  async request<T>(
    method: HttpMethod,
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> {
    const { body, params, requiresAuth = true } = options;

    const url = this.buildUrl(endpoint, params);
    const headers = await this.getHeaders(requiresAuth);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // Handle 401 Unauthorized
      if (response.status === 401) {
        this.onUnauthorized?.();
        throw new Error('Unauthorized');
      }

      const data = response.status !== 204 ? await response.json() : null;

      if (!response.ok) {
        const errorMessage = data?.detail || data?.message || 'Request failed';
        throw new Error(errorMessage);
      }

      return {
        data,
        status: response.status,
        ok: true,
      };
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error('Request timeout');
        }
        throw error;
      }
      throw new Error('An unexpected error occurred');
    }
  }

  // OAuth2 form login (special case - uses form data instead of JSON)
  async loginWithForm(email: string, password: string): Promise<ApiResponse<{ access_token: string; token_type: string }>> {
    const url = this.buildUrl('/users/login');

    const formData = new URLSearchParams();
    formData.append('username', email); // API expects email in username field
    formData.append('password', password);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString(),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      const data = await response.json();

      if (!response.ok) {
        const errorMessage = data?.detail || 'Login failed';
        throw new Error(errorMessage);
      }

      return {
        data,
        status: response.status,
        ok: true,
      };
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error('Request timeout');
        }
        throw error;
      }
      throw new Error('An unexpected error occurred');
    }
  }

  // Convenience methods
  get<T>(endpoint: string, params?: Record<string, string | string[]>): Promise<ApiResponse<T>> {
    return this.request<T>('GET', endpoint, { params });
  }

  post<T>(endpoint: string, body: object, requiresAuth = true): Promise<ApiResponse<T>> {
    return this.request<T>('POST', endpoint, { body, requiresAuth });
  }

  put<T>(endpoint: string, body: object): Promise<ApiResponse<T>> {
    return this.request<T>('PUT', endpoint, { body });
  }

  delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>('DELETE', endpoint);
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
