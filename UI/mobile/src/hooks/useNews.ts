import { useState, useEffect, useCallback } from 'react';
import { NewsArticle } from '@/types/api';
import { newsService } from '@/services/api';

interface UseNewsResult {
  articles: NewsArticle[];
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export function useNews(feedId?: number | null): UseNewsResult {
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchNews = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      let news: NewsArticle[];

      if (feedId) {
        // Fetch news for a specific feed
        news = await newsService.getNewsByFeed(feedId);
      } else {
        // Fetch general market news
        news = await newsService.loadNews('market');
      }

      setArticles(news);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load news';
      setError(message);
      setArticles([]);
    } finally {
      setIsLoading(false);
    }
  }, [feedId]);

  useEffect(() => {
    fetchNews();
  }, [fetchNews]);

  const refresh = useCallback(async () => {
    await fetchNews();
  }, [fetchNews]);

  return {
    articles,
    isLoading,
    error,
    refresh,
  };
}
