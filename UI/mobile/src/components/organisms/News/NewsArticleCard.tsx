import React from 'react';
import {
  View,
  TouchableOpacity,
  Image,
  StyleSheet,
  Linking,
  ViewStyle,
  StyleProp,
} from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { ThemedText } from '@/components/atoms/Text/ThemedText';
import { SentimentBadge } from '@/components/atoms/Badge/SentimentBadge';
import { TagChip } from '@/components/atoms/Chip/TagChip';
import { NewsArticle } from '@/types/api';

interface NewsArticleCardProps {
  article: NewsArticle;
  style?: StyleProp<ViewStyle>;
}

export function NewsArticleCard({ article, style }: NewsArticleCardProps) {
  const { colors } = useTheme();

  const handlePress = () => {
    if (article.link) {
      Linking.openURL(article.link);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMinutes = Math.floor(diffMs / (1000 * 60));

    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffHours < 48) return 'Yesterday';
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    });
  };

  return (
    <TouchableOpacity
      style={[
        styles.card,
        { backgroundColor: colors.card, borderColor: colors.border },
        style,
      ]}
      onPress={handlePress}
      activeOpacity={0.8}
      disabled={!article.link}
    >
      {/* Image */}
      {article.imagelink && (
        <Image
          source={{ uri: article.imagelink }}
          style={styles.image}
          resizeMode="cover"
        />
      )}

      <View style={styles.content}>
        {/* Source and Date */}
        <View style={styles.meta}>
          {article.sourcename && (
            <ThemedText variant="caption" color="primary" style={styles.source}>
              {article.sourcename}
            </ThemedText>
          )}
          {article.pubdate && (
            <ThemedText variant="caption" color="muted">
              {formatDate(article.pubdate)}
            </ThemedText>
          )}
        </View>

        {/* Title */}
        <ThemedText variant="title" numberOfLines={3} style={styles.title}>
          {article.title || 'Untitled Article'}
        </ThemedText>

        {/* Description */}
        {article.description && (
          <ThemedText
            variant="body"
            color="secondary"
            numberOfLines={3}
            style={styles.description}
          >
            {article.description}
          </ThemedText>
        )}

        {/* AI Summary */}
        {article.aisummary && (
          <View
            style={[
              styles.summaryContainer,
              { backgroundColor: colors.surface },
            ]}
          >
            <ThemedText variant="caption" color="primary" style={styles.summaryLabel}>
              AI Summary
            </ThemedText>
            <ThemedText variant="body" numberOfLines={4}>
              {article.aisummary}
            </ThemedText>
          </View>
        )}

        {/* Footer with Sentiment and Symbols */}
        <View style={styles.footer}>
          {article.sentiment && (
            <SentimentBadge sentiment={article.sentiment} />
          )}

          {article.symbols && article.symbols.length > 0 && (
            <View style={styles.symbols}>
              {article.symbols.slice(0, 4).map((symbol) => (
                <View
                  key={symbol}
                  style={[
                    styles.symbolBadge,
                    { backgroundColor: colors.surface },
                  ]}
                >
                  <ThemedText variant="caption" color="primary">
                    ${symbol}
                  </ThemedText>
                </View>
              ))}
              {article.symbols.length > 4 && (
                <ThemedText variant="caption" color="muted">
                  +{article.symbols.length - 4}
                </ThemedText>
              )}
            </View>
          )}
        </View>

        {/* Creators */}
        {article.creator && article.creator.length > 0 && (
          <ThemedText variant="caption" color="muted" style={styles.creators}>
            By {article.creator.slice(0, 2).join(', ')}
            {article.creator.length > 2 && ` +${article.creator.length - 2} more`}
          </ThemedText>
        )}
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
    height: 200,
  },
  content: {
    padding: 16,
  },
  meta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  source: {
    fontWeight: '600',
  },
  title: {
    marginBottom: 8,
    lineHeight: 26,
  },
  description: {
    marginBottom: 12,
  },
  summaryContainer: {
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
  },
  summaryLabel: {
    fontWeight: '600',
    marginBottom: 4,
  },
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  symbols: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    flexWrap: 'wrap',
  },
  symbolBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  creators: {
    marginTop: 4,
  },
});
