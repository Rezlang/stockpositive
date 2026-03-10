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
import { NEWS_SOURCES } from '@/constants/config';

type IconName = keyof typeof Ionicons.glyphMap;

interface SourceCheckboxProps {
  sources: string[];
  onChange: (sources: string[]) => void;
  label?: string;
  error?: string | null;
  style?: StyleProp<ViewStyle>;
}

export function SourceCheckbox({
  sources,
  onChange,
  label,
  error,
  style,
}: SourceCheckboxProps) {
  const { colors } = useTheme();

  const handleToggle = (sourceId: string) => {
    if (sources.includes(sourceId)) {
      onChange(sources.filter((s) => s !== sourceId));
    } else {
      onChange([...sources, sourceId]);
    }
  };

  return (
    <View style={[styles.container, style]}>
      {label && (
        <ThemedText variant="body" color="secondary" style={styles.label}>
          {label}
        </ThemedText>
      )}

      <View style={styles.grid}>
        {NEWS_SOURCES.map((source) => {
          const isSelected = sources.includes(source.id);
          return (
            <TouchableOpacity
              key={source.id}
              style={[
                styles.sourceItem,
                {
                  backgroundColor: isSelected ? colors.primaryLight : colors.surface,
                  borderColor: isSelected ? colors.primary : colors.border,
                },
              ]}
              onPress={() => handleToggle(source.id)}
              activeOpacity={0.7}
            >
              <View style={styles.sourceContent}>
                <Ionicons
                  name={source.icon as IconName}
                  size={20}
                  color={isSelected ? colors.primary : colors.textMuted}
                />
                <ThemedText
                  variant="body"
                  color={isSelected ? 'primary' : undefined}
                  style={styles.sourceName}
                >
                  {source.name}
                </ThemedText>
              </View>
              <View
                style={[
                  styles.checkbox,
                  {
                    borderColor: isSelected ? colors.primary : colors.border,
                    backgroundColor: isSelected ? colors.primary : 'transparent',
                  },
                ]}
              >
                {isSelected && (
                  <Ionicons name="checkmark" size={14} color="#FFFFFF" />
                )}
              </View>
            </TouchableOpacity>
          );
        })}
      </View>

      {error ? (
        <ThemedText variant="caption" color="error" style={styles.error}>
          {error}
        </ThemedText>
      ) : (
        <ThemedText variant="caption" color="muted" style={styles.helperText}>
          Leave empty to receive news from all sources
        </ThemedText>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: 16,
  },
  label: {
    marginBottom: 12,
  },
  grid: {
    gap: 8,
  },
  sourceItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 14,
    borderRadius: 12,
    borderWidth: 1,
  },
  sourceContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  sourceName: {
    fontWeight: '500',
  },
  checkbox: {
    width: 22,
    height: 22,
    borderRadius: 6,
    borderWidth: 2,
    alignItems: 'center',
    justifyContent: 'center',
  },
  error: {
    marginTop: 8,
  },
  helperText: {
    marginTop: 8,
  },
});
