import React from 'react';
import { View, FlatList, StyleSheet, RefreshControl } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { UserFeedResponse } from '@/types/api';
import { FeedListItem } from '@/components/molecules/FeedItem/FeedListItem';
import { EmptyState } from '@/components/molecules/EmptyState/EmptyState';

interface FeedListProps {
  feeds: UserFeedResponse[];
  activeFeedId: number | null;
  onSelectFeed: (feedId: number) => void;
  onEditFeed: (feed: UserFeedResponse) => void;
  onDeleteFeed: (feedId: number) => void;
  onCreateFeed: () => void;
  isLoading?: boolean;
  onRefresh?: () => void;
}

export function FeedList({
  feeds,
  activeFeedId,
  onSelectFeed,
  onEditFeed,
  onDeleteFeed,
  onCreateFeed,
  isLoading = false,
  onRefresh,
}: FeedListProps) {
  const { colors } = useTheme();

  if (feeds.length === 0 && !isLoading) {
    return (
      <EmptyState
        icon="list-outline"
        title="No Feeds Yet"
        message="Create your first feed to start getting personalized news"
        actionLabel="Create Feed"
        onAction={onCreateFeed}
      />
    );
  }

  return (
    <FlatList
      data={feeds}
      keyExtractor={(item) => item.id.toString()}
      renderItem={({ item }) => (
        <FeedListItem
          feed={item}
          isActive={item.id === activeFeedId}
          onPress={() => onSelectFeed(item.id)}
          onEdit={() => onEditFeed(item)}
          onDelete={() => onDeleteFeed(item.id)}
        />
      )}
      contentContainerStyle={styles.list}
      ItemSeparatorComponent={() => <View style={styles.separator} />}
      refreshControl={
        onRefresh ? (
          <RefreshControl
            refreshing={isLoading}
            onRefresh={onRefresh}
            tintColor={colors.primary}
          />
        ) : undefined
      }
    />
  );
}

const styles = StyleSheet.create({
  list: {
    padding: 16,
  },
  separator: {
    height: 12,
  },
});
