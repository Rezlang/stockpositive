import React, { useState } from 'react';
import { View, StyleSheet } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { useAuth } from '@/contexts/AuthContext';
import { useFeeds } from '@/contexts/FeedContext';
import { useNews } from '@/hooks/useNews';
import { ThemedText } from '@/components/atoms/Text/ThemedText';
import { NewsList } from '@/components/organisms/News/NewsList';
import { FeedSelector } from '@/components/organisms/Feed/FeedSelector';
import { AuthModal } from '@/components/organisms/Auth/AuthModal';
import { EmptyState } from '@/components/molecules/EmptyState/EmptyState';
import type { RootTabScreenProps } from '../navigation/types';

export default function HomeScreen({ navigation }: RootTabScreenProps<'News'>) {
  const { colors } = useTheme();
  const { isAuthenticated } = useAuth();
  const { feeds, activeFeed, setActiveFeed } = useFeeds();
  const { articles, isLoading, error, refresh } = useNews(activeFeed?.id);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  // Prompt for login if not authenticated
  const showLoginPrompt = !isAuthenticated && feeds.length === 0;

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      {/* Header with Feed Selector */}
      {isAuthenticated && feeds.length > 0 && (
        <View style={styles.header}>
          <FeedSelector
            feeds={feeds}
            activeFeed={activeFeed}
            onSelectFeed={setActiveFeed}
          />
        </View>
      )}

      {/* Welcome message for non-authenticated users */}
      {!isAuthenticated && (
        <View style={styles.welcomeHeader}>
          <ThemedText variant="largeTitle" style={styles.welcomeTitle}>
            Market News
          </ThemedText>
          <ThemedText variant="body" color="secondary">
            Sign in to create custom feeds and personalize your news
          </ThemedText>
        </View>
      )}

      {/* Show empty state prompting login */}
      {showLoginPrompt ? (
        <EmptyState
          icon="newspaper-outline"
          title="Personalized News Awaits"
          message="Create an account to build custom feeds and get news tailored to your stock interests"
          actionLabel="Get Started"
          onAction={() => setIsAuthModalOpen(true)}
        />
      ) : (
        <NewsList
          articles={articles}
          isLoading={isLoading}
          error={error}
          onRefresh={refresh}
          emptyIcon="newspaper-outline"
          emptyTitle={activeFeed ? 'No News for This Feed' : 'No News Available'}
          emptyMessage={
            activeFeed
              ? `No recent news found for ${activeFeed.stocks.join(', ')}`
              : 'Check back later for the latest market news'
          }
        />
      )}

      <AuthModal
        visible={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    padding: 16,
    paddingBottom: 8,
  },
  welcomeHeader: {
    padding: 16,
    paddingBottom: 8,
  },
  welcomeTitle: {
    marginBottom: 4,
  },
});
