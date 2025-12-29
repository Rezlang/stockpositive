import React from 'react';
import {
  TouchableOpacity,
  View,
  Text,
  StyleSheet,
  ViewStyle,
  StyleProp,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '@/contexts/ThemeContext';

interface TagChipProps {
  label: string;
  onRemove?: () => void;
  onPress?: () => void;
  selected?: boolean;
  style?: StyleProp<ViewStyle>;
}

export function TagChip({
  label,
  onRemove,
  onPress,
  selected = false,
  style,
}: TagChipProps) {
  const { colors } = useTheme();

  const chipContent = (
    <>
      <Text
        style={[
          styles.label,
          {
            color: selected ? '#FFFFFF' : colors.text,
          },
        ]}
        numberOfLines={1}
      >
        {label}
      </Text>
      {onRemove && (
        <TouchableOpacity
          onPress={onRemove}
          hitSlop={{ top: 8, bottom: 8, left: 4, right: 8 }}
          style={styles.removeButton}
        >
          <Ionicons
            name="close-circle"
            size={16}
            color={selected ? '#FFFFFF' : colors.textMuted}
          />
        </TouchableOpacity>
      )}
    </>
  );

  const chipStyle = [
    styles.chip,
    {
      backgroundColor: selected ? colors.primary : colors.surface,
      borderColor: selected ? colors.primary : colors.border,
    },
    style,
  ];

  if (onPress) {
    return (
      <TouchableOpacity style={chipStyle} onPress={onPress} activeOpacity={0.7}>
        {chipContent}
      </TouchableOpacity>
    );
  }

  return <View style={chipStyle}>{chipContent}</View>;
}

const styles = StyleSheet.create({
  chip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingLeft: 12,
    paddingRight: 8,
    paddingVertical: 6,
    borderRadius: 16,
    borderWidth: 1,
  },
  label: {
    fontSize: 14,
    fontWeight: '500',
  },
  removeButton: {
    marginLeft: 4,
  },
});
