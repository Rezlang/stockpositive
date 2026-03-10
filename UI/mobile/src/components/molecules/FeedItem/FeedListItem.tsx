import React from 'react';
import {
  View,
  TouchableOpacity,
  StyleSheet,
  ViewStyle,
  StyleProp,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '@/contexts/ThemeContext';
import { ThemedText } from '@/components/atoms/Text/ThemedText';
import { IconButton } from '@/components/atoms/Button/IconButton';
import { UserFeedResponse } from '@/types/api';

interface FeedListItemProps {
  feed: UserFeedResponse;
  isActive?: boolean;
  onPress?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
  style?: StyleProp<ViewStyle>;
}

export function FeedListItem({
  feed,
  isActive = false,
  onPress,
  onEdit,
  onDelete,
  style,
}: FeedListItemProps) {
  const { colors } = useTheme();

  return (
    <TouchableOpacity
      style={[
        styles.container,
        {
          backgroundColor: isActive ? colors.primaryLight : colors.card,
          borderColor: isActive ? colors.primary : colors.border,
        },
        style,
      ]}
      onPress={onPress}
      activeOpacity={0.7}
      disabled={!onPress}
    >
      <View style={styles.iconContainer}>
        <Ionicons
          name={isActive ? 'radio-button-on' : 'radio-button-off'}
          size={24}
          color={isActive ? colors.primary : colors.textMuted}
        />
      </View>

      <View style={styles.content}>
        <ThemedText variant="subtitle" numberOfLines={1}>
          {feed.feedname}
        </ThemedText>
        <View style={styles.meta}>
          <ThemedText variant="caption" color="muted">
            {feed.stocks.length === 0 ? 'All stocks' : `${feed.stocks.length} stocks`}
          </ThemedText>
          <View style={styles.dot} />
          <ThemedText variant="caption" color="muted">
            {feed.sources.length === 0 ? 'All sources' : `${feed.sources.length} sources`}
          </ThemedText>
        </View>
      </View>

      <View style={styles.actions}>
        {onEdit && (
          <IconButton
            icon="pencil-outline"
            onPress={onEdit}
            size={20}
            color={colors.textMuted}
          />
        )}
        {onDelete && (
          <IconButton
            icon="trash-outline"
            onPress={onDelete}
            size={20}
            color={colors.error}
          />
        )}
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
  },
  iconContainer: {
    marginRight: 12,
  },
  content: {
    flex: 1,
  },
  meta: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
  },
  dot: {
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: '#999',
    marginHorizontal: 8,
  },
  actions: {
    flexDirection: 'row',
  },
});
