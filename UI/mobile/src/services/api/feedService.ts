import { apiClient } from './client';
import {
  UserFeedResponse,
  CreateFeedRequest,
  UpdateFeedRequest,
} from '@/types/api';

export const feedService = {
  async getFeeds(): Promise<UserFeedResponse[]> {
    const response = await apiClient.get<UserFeedResponse[]>('/feeds/get_feeds');
    return response.data;
  },

  async createFeed(data: CreateFeedRequest): Promise<UserFeedResponse> {
    const response = await apiClient.post<UserFeedResponse>(
      '/feeds/add_feed',
      data
    );
    return response.data;
  },

  async updateFeed(
    feedId: number,
    data: UpdateFeedRequest
  ): Promise<UserFeedResponse> {
    const response = await apiClient.put<UserFeedResponse>(
      `/feeds/edit_feed/${feedId}`,
      data
    );
    return response.data;
  },

  async deleteFeed(feedId: number): Promise<void> {
    await apiClient.delete(`/feeds/delete_feed/${feedId}`);
  },
};
