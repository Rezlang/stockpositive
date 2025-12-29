import { apiClient } from './client';
import { NewsArticle } from '@/types/api';

export const newsService = {
  async loadNews(
    source: string = 'market',
    symbols?: string[]
  ): Promise<NewsArticle[]> {
    const params: Record<string, string | string[]> = { source };
    if (symbols && symbols.length > 0) {
      params.symbols = symbols;
    }
    const response = await apiClient.get<NewsArticle[]>('/news/load-news', params);
    return response.data;
  },

  async getNewsByFeed(feedId: number): Promise<NewsArticle[]> {
    const response = await apiClient.get<NewsArticle[]>('/news/get-news', {
      feedId: feedId.toString(),
    });
    return response.data;
  },
};
