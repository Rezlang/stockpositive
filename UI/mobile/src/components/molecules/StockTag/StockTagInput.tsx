import React, { useState } from 'react';
import {
  View,
  TextInput as RNTextInput,
  StyleSheet,
  ViewStyle,
  StyleProp,
  ScrollView,
} from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { ThemedText } from '@/components/atoms/Text/ThemedText';
import { TagChip } from '@/components/atoms/Chip/TagChip';
import { POPULAR_STOCKS } from '@/constants/config';

interface StockTagInputProps {
  value: string[];
  onChange: (stocks: string[]) => void;
  label?: string;
  error?: string | null;
  style?: StyleProp<ViewStyle>;
}

export function StockTagInput({
  value,
  onChange,
  label,
  error,
  style,
}: StockTagInputProps) {
  const { colors } = useTheme();
  const [inputValue, setInputValue] = useState('');

  const handleAddStock = () => {
    const stock = inputValue.toUpperCase().trim();
    if (stock && !value.includes(stock)) {
      onChange([...value, stock]);
      setInputValue('');
    }
  };

  const handleRemoveStock = (stock: string) => {
    onChange(value.filter((s) => s !== stock));
  };

  const handleQuickAdd = (stock: string) => {
    if (!value.includes(stock)) {
      onChange([...value, stock]);
    }
  };

  const availableQuickStocks = POPULAR_STOCKS.filter(
    (stock) => !value.includes(stock)
  );

  return (
    <View style={[styles.container, style]}>
      {label && (
        <ThemedText variant="body" color="secondary" style={styles.label}>
          {label}
        </ThemedText>
      )}

      {/* Selected stocks */}
      {value.length > 0 && (
        <View style={styles.selectedContainer}>
          {value.map((stock) => (
            <TagChip
              key={stock}
              label={stock}
              onRemove={() => handleRemoveStock(stock)}
              selected
              style={styles.chip}
            />
          ))}
        </View>
      )}

      {/* Input field */}
      <View
        style={[
          styles.inputContainer,
          {
            backgroundColor: colors.inputBackground,
            borderColor: error ? colors.error : colors.inputBorder,
          },
        ]}
      >
        <RNTextInput
          style={[styles.input, { color: colors.text }]}
          value={inputValue}
          onChangeText={setInputValue}
          placeholder="Enter stock symbol (e.g., AAPL)"
          placeholderTextColor={colors.inputPlaceholder}
          autoCapitalize="characters"
          returnKeyType="done"
          onSubmitEditing={handleAddStock}
        />
      </View>

      {error && (
        <ThemedText variant="caption" color="error" style={styles.error}>
          {error}
        </ThemedText>
      )}

      {/* Quick add suggestions */}
      {availableQuickStocks.length > 0 && (
        <View style={styles.suggestions}>
          <ThemedText variant="caption" color="muted" style={styles.suggestionsLabel}>
            Popular stocks:
          </ThemedText>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.suggestionsContent}
          >
            {availableQuickStocks.slice(0, 6).map((stock) => (
              <TagChip
                key={stock}
                label={stock}
                onPress={() => handleQuickAdd(stock)}
                style={styles.suggestionChip}
              />
            ))}
          </ScrollView>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: 16,
  },
  label: {
    marginBottom: 8,
  },
  selectedContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 12,
    gap: 8,
  },
  chip: {
    marginBottom: 0,
  },
  inputContainer: {
    height: 48,
    borderRadius: 12,
    borderWidth: 1,
    justifyContent: 'center',
  },
  input: {
    height: '100%',
    paddingHorizontal: 16,
    fontSize: 16,
  },
  error: {
    marginTop: 4,
  },
  suggestions: {
    marginTop: 12,
  },
  suggestionsLabel: {
    marginBottom: 8,
  },
  suggestionsContent: {
    gap: 8,
  },
  suggestionChip: {
    marginRight: 0,
  },
});
