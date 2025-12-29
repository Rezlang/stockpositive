import React from 'react';
import { Text, TextStyle, StyleSheet, StyleProp } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';

type TextVariant =
  | 'largeTitle'
  | 'title'
  | 'subtitle'
  | 'body'
  | 'caption'
  | 'label';

interface ThemedTextProps {
  children: React.ReactNode;
  variant?: TextVariant;
  color?: 'primary' | 'secondary' | 'muted' | 'error' | 'success';
  style?: StyleProp<TextStyle>;
  numberOfLines?: number;
  testID?: string;
}

export function ThemedText({
  children,
  variant = 'body',
  color,
  style,
  numberOfLines,
  testID,
}: ThemedTextProps) {
  const { colors } = useTheme();

  const getTextColor = () => {
    switch (color) {
      case 'primary':
        return colors.primary;
      case 'secondary':
        return colors.textSecondary;
      case 'muted':
        return colors.textMuted;
      case 'error':
        return colors.error;
      case 'success':
        return colors.success;
      default:
        return colors.text;
    }
  };

  const variantStyles: Record<TextVariant, TextStyle> = {
    largeTitle: {
      fontSize: 28,
      fontWeight: '700',
      lineHeight: 34,
    },
    title: {
      fontSize: 20,
      fontWeight: '600',
      lineHeight: 25,
    },
    subtitle: {
      fontSize: 16,
      fontWeight: '500',
      lineHeight: 21,
    },
    body: {
      fontSize: 14,
      fontWeight: '400',
      lineHeight: 20,
    },
    caption: {
      fontSize: 12,
      fontWeight: '400',
      lineHeight: 16,
    },
    label: {
      fontSize: 12,
      fontWeight: '600',
      lineHeight: 16,
      textTransform: 'uppercase',
      letterSpacing: 0.5,
    },
  };

  return (
    <Text
      style={[variantStyles[variant], { color: getTextColor() }, style]}
      numberOfLines={numberOfLines}
      testID={testID}
    >
      {children}
    </Text>
  );
}
