import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useMemo,
  ReactNode,
} from 'react';
import { UserFeedResponse, CreateFeedRequest, UpdateFeedRequest } from '@/types/api';
import { feedService } from '@/services/api';
import { storageService } from '@/services/storage';
import { useAuth } from './AuthContext';

interface FeedContextValue {
  feeds: UserFeedResponse[];
  activeFeed: UserFeedResponse | null;
  isLoading: boolean;
  error: string | null;
  setActiveFeed: (feedId: number) => void;
  createFeed: (data: CreateFeedRequest) => Promise<void>;
  updateFeed: (feedId: number, data: UpdateFeedRequest) => Promise<void>;
  deleteFeed: (feedId: number) => Promise<void>;
  refreshFeeds: () => Promise<void>;
  clearError: () => void;
}

const FeedContext = createContext<FeedContextValue | undefined>(undefined);

interface FeedProviderProps {
  children: ReactNode;
}

export function FeedProvider({ children }: FeedProviderProps) {
  const { isAuthenticated } = useAuth();
  const [feeds, setFeeds] = useState<UserFeedResponse[]>([]);
  const [activeFeedId, setActiveFeedId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Find the active feed object
  const activeFeed = useMemo(() => {
    if (activeFeedId === null) return null;
    return feeds.find((feed) => feed.id === activeFeedId) || null;
  }, [feeds, activeFeedId]);

  // Fetch feeds when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      refreshFeeds();
      loadActiveFeedId();
    } else {
      // Clear feeds when logged out
      setFeeds([]);
      setActiveFeedId(null);
    }
  }, [isAuthenticated]);

  const loadActiveFeedId = async () => {
    const savedId = await storageService.getActiveFeedId();
    if (savedId !== null) {
      setActiveFeedId(savedId);
    }
  };

  const refreshFeeds = useCallback(async () => {
    if (!isAuthenticated) return;

    setIsLoading(true);
    setError(null);
    try {
      const fetchedFeeds = await feedService.getFeeds();
      setFeeds(fetchedFeeds);

      // If we have feeds but no active feed, set the first one as active
      if (fetchedFeeds.length > 0 && activeFeedId === null) {
        const savedId = await storageService.getActiveFeedId();
        const feedExists = fetchedFeeds.some((f) => f.id === savedId);
        if (savedId !== null && feedExists) {
          setActiveFeedId(savedId);
        } else {
          setActiveFeedId(fetchedFeeds[0].id);
          await storageService.setActiveFeedId(fetchedFeeds[0].id);
        }
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load feeds';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated, activeFeedId]);

  const setActiveFeed = useCallback((feedId: number) => {
    setActiveFeedId(feedId);
    storageService.setActiveFeedId(feedId);
  }, []);

  const createFeed = useCallback(
    async (data: CreateFeedRequest) => {
      setIsLoading(true);
      setError(null);
      try {
        const newFeed = await feedService.createFeed(data);
        setFeeds((prev) => [...prev, newFeed]);
        // Set the new feed as active
        setActiveFeed(newFeed.id);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to create feed';
        setError(message);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [setActiveFeed]
  );

  const updateFeed = useCallback(
    async (feedId: number, data: UpdateFeedRequest) => {
      setIsLoading(true);
      setError(null);
      try {
        const updatedFeed = await feedService.updateFeed(feedId, data);
        setFeeds((prev) =>
          prev.map((feed) => (feed.id === feedId ? updatedFeed : feed))
        );
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to update feed';
        setError(message);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const deleteFeed = useCallback(
    async (feedId: number) => {
      setIsLoading(true);
      setError(null);
      try {
        await feedService.deleteFeed(feedId);
        setFeeds((prev) => prev.filter((feed) => feed.id !== feedId));

        // If we deleted the active feed, set a new one
        if (activeFeedId === feedId) {
          const remainingFeeds = feeds.filter((f) => f.id !== feedId);
          if (remainingFeeds.length > 0) {
            setActiveFeed(remainingFeeds[0].id);
          } else {
            setActiveFeedId(null);
            await storageService.removeActiveFeedId();
          }
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to delete feed';
        setError(message);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [activeFeedId, feeds, setActiveFeed]
  );

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const value = useMemo(
    () => ({
      feeds,
      activeFeed,
      isLoading,
      error,
      setActiveFeed,
      createFeed,
      updateFeed,
      deleteFeed,
      refreshFeeds,
      clearError,
    }),
    [
      feeds,
      activeFeed,
      isLoading,
      error,
      setActiveFeed,
      createFeed,
      updateFeed,
      deleteFeed,
      refreshFeeds,
      clearError,
    ]
  );

  return <FeedContext.Provider value={value}>{children}</FeedContext.Provider>;
}

export function useFeeds(): FeedContextValue {
  const context = useContext(FeedContext);
  if (context === undefined) {
    throw new Error('useFeeds must be used within a FeedProvider');
  }
  return context;
}
