import React, { useState } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { useAuth } from '@/contexts/AuthContext';
import { useFeeds } from '@/contexts/FeedContext';
import { UserFeedResponse } from '@/types/api';
import { ThemedText } from '@/components/atoms/Text/ThemedText';
import { PrimaryButton } from '@/components/atoms/Button/PrimaryButton';
import { LoadingSpinner } from '@/components/atoms/Spinner/LoadingSpinner';
import { EmptyState } from '@/components/molecules/EmptyState/EmptyState';
import { ErrorMessage } from '@/components/molecules/ErrorDisplay/ErrorMessage';
import { FeedList } from '@/components/organisms/Feed/FeedList';
import { FeedEditor } from '@/components/organisms/Feed/FeedEditor';
import { AuthModal } from '@/components/organisms/Auth/AuthModal';

export default function FeedManagementScreen() {
  const { colors } = useTheme();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const {
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
  } = useFeeds();

  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingFeed, setEditingFeed] = useState<UserFeedResponse | null>(null);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  const handleCreateFeed = () => {
    if (!isAuthenticated) {
      setIsAuthModalOpen(true);
      return;
    }
    setEditingFeed(null);
    setIsEditorOpen(true);
  };

  const handleEditFeed = (feed: UserFeedResponse) => {
    setEditingFeed(feed);
    setIsEditorOpen(true);
  };

  const handleDeleteFeed = (feedId: number) => {
    Alert.alert(
      'Delete Feed',
      'Are you sure you want to delete this feed? This action cannot be undone.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await deleteFeed(feedId);
            } catch (err) {
              const message = err instanceof Error ? err.message : 'Failed to delete feed';
              Alert.alert('Error', message);
            }
          },
        },
      ]
    );
  };

  const handleSaveFeed = async (data: any) => {
    if (editingFeed) {
      await updateFeed(editingFeed.id, data);
    } else {
      await createFeed(data);
    }
  };

  // Show loading state
  if (authLoading) {
    return <LoadingSpinner fullScreen message="Loading..." />;
  }

  // Show login prompt if not authenticated
  if (!isAuthenticated) {
    return (
      <View style={[styles.container, { backgroundColor: colors.background }]}>
        <EmptyState
          icon="lock-closed-outline"
          title="Sign In Required"
          message="Create an account or sign in to create and manage your custom news feeds"
          actionLabel="Sign In"
          onAction={() => setIsAuthModalOpen(true)}
        />
        <AuthModal
          visible={isAuthModalOpen}
          onClose={() => setIsAuthModalOpen(false)}
        />
      </View>
    );
  }

  // Show error state
  if (error && feeds.length === 0) {
    return (
      <View style={[styles.container, { backgroundColor: colors.background }]}>
        <ErrorMessage
          message={error}
          onRetry={() => {
            clearError();
            refreshFeeds();
          }}
        />
      </View>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <View style={styles.header}>
        <ThemedText variant="body" color="secondary">
          Manage your personalized news feeds
        </ThemedText>
        <PrimaryButton
          title="Create Feed"
          onPress={handleCreateFeed}
          style={styles.createButton}
        />
      </View>

      <FeedList
        feeds={feeds}
        activeFeedId={activeFeed?.id || null}
        onSelectFeed={setActiveFeed}
        onEditFeed={handleEditFeed}
        onDeleteFeed={handleDeleteFeed}
        onCreateFeed={handleCreateFeed}
        isLoading={isLoading}
        onRefresh={refreshFeeds}
      />

      <FeedEditor
        visible={isEditorOpen}
        feed={editingFeed}
        onClose={() => {
          setIsEditorOpen(false);
          setEditingFeed(null);
        }}
        onSave={handleSaveFeed}
        isLoading={isLoading}
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
    gap: 12,
  },
  createButton: {
    alignSelf: 'flex-start',
  },
});
