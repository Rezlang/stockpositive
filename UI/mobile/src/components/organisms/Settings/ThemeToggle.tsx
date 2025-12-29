import React from 'react';
import { View, Switch, StyleSheet, ViewStyle, StyleProp } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '@/contexts/ThemeContext';
import { ThemedText } from '@/components/atoms/Text/ThemedText';

interface ThemeToggleProps {
  style?: StyleProp<ViewStyle>;
}

export function ThemeToggle({ style }: ThemeToggleProps) {
  const { theme, colors, isDark, toggleTheme } = useTheme();

  return (
    <View
      style={[
        styles.container,
        { backgroundColor: colors.surface, borderColor: colors.border },
        style,
      ]}
    >
      <View style={styles.content}>
        <View style={[styles.iconContainer, { backgroundColor: colors.primaryLight }]}>
          <Ionicons
            name={isDark ? 'moon' : 'sunny'}
            size={20}
            color={colors.primary}
          />
        </View>
        <View style={styles.textContainer}>
          <ThemedText variant="subtitle">Dark Mode</ThemedText>
          <ThemedText variant="caption" color="muted">
            {isDark ? 'On' : 'Off'}
          </ThemedText>
        </View>
      </View>
      <Switch
        value={isDark}
        onValueChange={toggleTheme}
        trackColor={{
          false: colors.border,
          true: colors.primary,
        }}
        thumbColor="#FFFFFF"
        ios_backgroundColor={colors.border}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  iconContainer: {
    width: 40,
    height: 40,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  textContainer: {
    gap: 2,
  },
});
