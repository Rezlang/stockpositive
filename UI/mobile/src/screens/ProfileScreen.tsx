import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '@/contexts/ThemeContext';
import { useAuth } from '@/contexts/AuthContext';
import { useFeeds } from '@/contexts/FeedContext';
import { ThemedText } from '@/components/atoms/Text/ThemedText';
import { PrimaryButton } from '@/components/atoms/Button/PrimaryButton';
import { SecondaryButton } from '@/components/atoms/Button/SecondaryButton';
import { Divider } from '@/components/atoms/Divider/Divider';
import { LoadingSpinner } from '@/components/atoms/Spinner/LoadingSpinner';
import { ThemeToggle } from '@/components/organisms/Settings/ThemeToggle';
import { AuthModal } from '@/components/organisms/Auth/AuthModal';
import type { RootTabScreenProps } from '../navigation/types';

export default function ProfileScreen({ navigation }: RootTabScreenProps<'Profile'>) {
  const { colors } = useTheme();
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const { feeds } = useFeeds();
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  const handleLogout = () => {
    Alert.alert(
      'Sign Out',
      'Are you sure you want to sign out?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Sign Out',
          style: 'destructive',
          onPress: logout,
        },
      ]
    );
  };

  if (isLoading) {
    return <LoadingSpinner fullScreen />;
  }

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: colors.background }]}
      contentContainerStyle={styles.contentContainer}
    >
      {/* User Info Section */}
      {isAuthenticated && user ? (
        <View style={styles.section}>
          <View
            style={[
              styles.profileHeader,
              { backgroundColor: colors.surface },
            ]}
          >
            <View
              style={[
                styles.avatar,
                { backgroundColor: colors.primaryLight },
              ]}
            >
              <ThemedText variant="largeTitle" color="primary">
                {user.username.charAt(0).toUpperCase()}
              </ThemedText>
            </View>
            <View style={styles.userInfo}>
              <ThemedText variant="title">{user.username}</ThemedText>
              <ThemedText variant="body" color="secondary">
                {user.email}
              </ThemedText>
            </View>
          </View>

          {/* Stats */}
          <View style={styles.statsRow}>
            <View
              style={[styles.statCard, { backgroundColor: colors.surface }]}
            >
              <Ionicons name="list" size={24} color={colors.primary} />
              <ThemedText variant="title">{feeds.length}</ThemedText>
              <ThemedText variant="caption" color="muted">
                Feeds
              </ThemedText>
            </View>
            <View
              style={[styles.statCard, { backgroundColor: colors.surface }]}
            >
              <Ionicons
                name={user.is_active ? 'checkmark-circle' : 'close-circle'}
                size={24}
                color={user.is_active ? colors.success : colors.error}
              />
              <ThemedText variant="title">
                {user.is_active ? 'Active' : 'Inactive'}
              </ThemedText>
              <ThemedText variant="caption" color="muted">
                Status
              </ThemedText>
            </View>
          </View>
        </View>
      ) : (
        <View style={styles.section}>
          <View
            style={[
              styles.guestCard,
              { backgroundColor: colors.surface },
            ]}
          >
            <Ionicons
              name="person-circle-outline"
              size={64}
              color={colors.textMuted}
            />
            <ThemedText variant="title" style={styles.guestTitle}>
              Welcome, Guest
            </ThemedText>
            <ThemedText
              variant="body"
              color="secondary"
              style={styles.guestMessage}
            >
              Sign in to access personalized features and save your preferences
            </ThemedText>
            <PrimaryButton
              title="Sign In"
              onPress={() => setIsAuthModalOpen(true)}
              style={styles.signInButton}
            />
          </View>
        </View>
      )}

      <Divider style={styles.divider} />

      {/* Settings Section */}
      <View style={styles.section}>
        <ThemedText variant="label" color="muted" style={styles.sectionTitle}>
          Preferences
        </ThemedText>
        <ThemeToggle />
      </View>

      {/* Account Section */}
      {isAuthenticated && (
        <>
          <Divider style={styles.divider} />
          <View style={styles.section}>
            <ThemedText variant="label" color="muted" style={styles.sectionTitle}>
              Account
            </ThemedText>
            <View
              style={[
                styles.infoCard,
                { backgroundColor: colors.surface, borderColor: colors.border },
              ]}
            >
              <View style={styles.infoRow}>
                <ThemedText variant="body" color="secondary">
                  Member Since
                </ThemedText>
                <ThemedText variant="body">
                  {user?.created_at
                    ? new Date(user.created_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                      })
                    : 'N/A'}
                </ThemedText>
              </View>
            </View>

            <SecondaryButton
              title="Sign Out"
              onPress={handleLogout}
              style={styles.logoutButton}
            />
          </View>
        </>
      )}

      {/* App Info */}
      <View style={styles.appInfo}>
        <ThemedText variant="caption" color="muted">
          StockPositive v1.0.0
        </ThemedText>
      </View>

      <AuthModal
        visible={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
      />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  contentContainer: {
    padding: 16,
  },
  section: {
    marginBottom: 8,
  },
  sectionTitle: {
    marginBottom: 12,
  },
  profileHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 16,
    marginBottom: 16,
  },
  avatar: {
    width: 64,
    height: 64,
    borderRadius: 32,
    alignItems: 'center',
    justifyContent: 'center',
  },
  userInfo: {
    marginLeft: 16,
    flex: 1,
  },
  statsRow: {
    flexDirection: 'row',
    gap: 12,
  },
  statCard: {
    flex: 1,
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    gap: 4,
  },
  guestCard: {
    padding: 32,
    borderRadius: 16,
    alignItems: 'center',
  },
  guestTitle: {
    marginTop: 16,
    marginBottom: 8,
  },
  guestMessage: {
    textAlign: 'center',
    marginBottom: 24,
  },
  signInButton: {
    minWidth: 160,
  },
  divider: {
    marginVertical: 24,
  },
  infoCard: {
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    marginBottom: 16,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  logoutButton: {
    marginTop: 8,
  },
  appInfo: {
    alignItems: 'center',
    marginTop: 32,
    marginBottom: 16,
  },
});
