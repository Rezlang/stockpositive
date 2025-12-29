import React from 'react';
import {
  View,
  TouchableOpacity,
  Image,
  StyleSheet,
  ViewStyle,
  StyleProp,
} from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { ThemedText } from '@/components/atoms/Text/ThemedText';
import { SentimentBadge } from '@/components/atoms/Badge/SentimentBadge';
import { NewsArticle } from '@/types/api';

interface NewsCardPreviewProps {
  article: NewsArticle;
  onPress?: () => void;
  style?: StyleProp<ViewStyle>;
}

export function NewsCardPreview({
  article,
  onPress,
  style,
}: NewsCardPreviewProps) {
  const { colors } = useTheme();

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));

    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffHours < 48) return 'Yesterday';
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <TouchableOpacity
      style={[
        styles.card,
        { backgroundColor: colors.card, borderColor: colors.border },
        style,
      ]}
      onPress={onPress}
      activeOpacity={0.7}
      disabled={!onPress}
    >
      {article.imagelink && (
        <Image
          source={{ uri: article.imagelink }}
          style={styles.image}
          resizeMode="cover"
        />
      )}
      <View style={styles.content}>
        <View style={styles.header}>
          {article.sourcename && (
            <ThemedText variant="caption" color="muted">
              {article.sourcename}
            </ThemedText>
          )}
          {article.pubdate && (
            <ThemedText variant="caption" color="muted">
              {formatDate(article.pubdate)}
            </ThemedText>
          )}
        </View>

        <ThemedText variant="subtitle" numberOfLines={2} style={styles.title}>
          {article.title || 'Untitled'}
        </ThemedText>

        {article.description && (
          <ThemedText
            variant="body"
            color="secondary"
            numberOfLines={2}
            style={styles.description}
          >
            {article.description}
          </ThemedText>
        )}

        <View style={styles.footer}>
          {article.sentiment && <SentimentBadge sentiment={article.sentiment} />}
          {article.symbols && article.symbols.length > 0 && (
            <View style={styles.symbols}>
              {article.symbols.slice(0, 3).map((symbol) => (
                <View
                  key={symbol}
                  style={[styles.symbolBadge, { backgroundColor: colors.surface }]}
                >
                  <ThemedText variant="caption" color="primary">
                    ${symbol}
                  </ThemedText>
                </View>
              ))}
              {article.symbols.length > 3 && (
                <ThemedText variant="caption" color="muted">
                  +{article.symbols.length - 3}
                </ThemedText>
              )}
            </View>
          )}
        </View>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 16,
    borderWidth: 1,
    overflow: 'hidden',
  },
  image: {
    width: '100%',
    height: 160,
  },
  content: {
    padding: 16,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  title: {
    marginBottom: 8,
  },
  description: {
    marginBottom: 12,
  },
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  symbols: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  symbolBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
});
