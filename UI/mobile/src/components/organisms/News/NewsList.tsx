import React from 'react';
import {
  View,
  FlatList,
  StyleSheet,
  RefreshControl,
  ViewStyle,
  StyleProp,
} from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { NewsArticle } from '@/types/api';
import { NewsArticleCard } from './NewsArticleCard';
import { LoadingSpinner } from '@/components/atoms/Spinner/LoadingSpinner';
import { EmptyState } from '@/components/molecules/EmptyState/EmptyState';
import { ErrorMessage } from '@/components/molecules/ErrorDisplay/ErrorMessage';

interface NewsListProps {
  articles: NewsArticle[];
  isLoading: boolean;
  error: string | null;
  onRefresh: () => void;
  emptyIcon?: string;
  emptyTitle?: string;
  emptyMessage?: string;
  style?: StyleProp<ViewStyle>;
}

export function NewsList({
  articles,
  isLoading,
  error,
  onRefresh,
  emptyIcon = 'newspaper-outline',
  emptyTitle = 'No News Available',
  emptyMessage = 'Check back later for the latest market news',
  style,
}: NewsListProps) {
  const { colors } = useTheme();

  // Show loading state only if there's no data yet
  if (isLoading && articles.length === 0) {
    return <LoadingSpinner fullScreen message="Loading news..." />;
  }

  // Show error state
  if (error && articles.length === 0) {
    return (
      <View style={[styles.centered, style]}>
        <ErrorMessage message={error} onRetry={onRefresh} />
      </View>
    );
  }

  // Show empty state
  if (articles.length === 0) {
    return (
      <EmptyState
        icon={emptyIcon as any}
        title={emptyTitle}
        message={emptyMessage}
        style={style}
      />
    );
  }

  return (
    <FlatList
      data={articles}
      keyExtractor={(item, index) => item.id?.toString() || `article-${index}`}
      renderItem={({ item }) => <NewsArticleCard article={item} />}
      contentContainerStyle={styles.list}
      ItemSeparatorComponent={() => <View style={styles.separator} />}
      refreshControl={
        <RefreshControl
          refreshing={isLoading}
          onRefresh={onRefresh}
          tintColor={colors.primary}
        />
      }
      showsVerticalScrollIndicator={false}
      style={style}
    />
  );
}

const styles = StyleSheet.create({
  list: {
    padding: 16,
  },
  separator: {
    height: 16,
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
});
