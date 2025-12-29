import React from 'react';
import { View, StyleSheet, ViewStyle, StyleProp } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '@/contexts/ThemeContext';
import { ThemedText } from '@/components/atoms/Text/ThemedText';
import { SecondaryButton } from '@/components/atoms/Button/SecondaryButton';

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
  style?: StyleProp<ViewStyle>;
}

export function ErrorMessage({
  message,
  onRetry,
  style,
}: ErrorMessageProps) {
  const { colors } = useTheme();

  return (
    <View style={[styles.container, style]}>
      <View
        style={[
          styles.iconContainer,
          { backgroundColor: `${colors.error}15` },
        ]}
      >
        <Ionicons name="alert-circle" size={32} color={colors.error} />
      </View>
      <ThemedText variant="body" style={styles.message}>
        {message}
      </ThemedText>
      {onRetry && (
        <SecondaryButton
          title="Try Again"
          onPress={onRetry}
          style={styles.button}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
  iconContainer: {
    width: 64,
    height: 64,
    borderRadius: 32,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  message: {
    textAlign: 'center',
    marginBottom: 16,
  },
  button: {
    minWidth: 120,
  },
});
