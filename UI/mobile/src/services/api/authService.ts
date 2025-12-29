import { apiClient } from './client';
import { RegisterRequest, TokenResponse, UserResponse } from '@/types/api';

export const authService = {
  async register(data: RegisterRequest): Promise<UserResponse> {
    const response = await apiClient.post<UserResponse>(
      '/users/register',
      data,
      false // No auth required for registration
    );
    return response.data;
  },

  async login(email: string, password: string): Promise<TokenResponse> {
    const response = await apiClient.loginWithForm(email, password);
    return response.data;
  },

  async getCurrentUser(): Promise<UserResponse> {
    const response = await apiClient.get<UserResponse>('/users/me');
    return response.data;
  },
};
