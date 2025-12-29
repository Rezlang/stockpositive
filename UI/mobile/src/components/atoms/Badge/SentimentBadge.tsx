import React from 'react';
import { View, Text, StyleSheet, ViewStyle, StyleProp } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '@/contexts/ThemeContext';

interface SentimentBadgeProps {
  sentiment: string | null;
  style?: StyleProp<ViewStyle>;
}

export function SentimentBadge({ sentiment, style }: SentimentBadgeProps) {
  const { colors } = useTheme();

  const getSentimentConfig = () => {
    const normalizedSentiment = sentiment?.toLowerCase() || '';

    if (normalizedSentiment.includes('positive') || normalizedSentiment === 'bullish') {
      return {
        label: 'Positive',
        color: colors.sentimentPositive,
        icon: 'trending-up' as const,
      };
    }
    if (normalizedSentiment.includes('negative') || normalizedSentiment === 'bearish') {
      return {
        label: 'Negative',
        color: colors.sentimentNegative,
        icon: 'trending-down' as const,
      };
    }
    return {
      label: 'Neutral',
      color: colors.sentimentNeutral,
      icon: 'remove' as const,
    };
  };

  const config = getSentimentConfig();

  return (
    <View
      style={[
        styles.badge,
        { backgroundColor: `${config.color}20` },
        style,
      ]}
    >
      <Ionicons name={config.icon} size={12} color={config.color} />
      <Text style={[styles.text, { color: config.color }]}>
        {config.label}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    gap: 4,
  },
  text: {
    fontSize: 11,
    fontWeight: '600',
  },
});
