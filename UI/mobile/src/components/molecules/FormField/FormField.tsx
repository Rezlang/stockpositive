import React from 'react';
import { View, StyleSheet, ViewStyle, StyleProp } from 'react-native';
import { TextInput } from '@/components/atoms/Input/TextInput';
import { PasswordInput } from '@/components/atoms/Input/PasswordInput';

interface FormFieldProps {
  label: string;
  value: string;
  onChangeText: (text: string) => void;
  error?: string | null;
  placeholder?: string;
  secureTextEntry?: boolean;
  autoCapitalize?: 'none' | 'sentences' | 'words' | 'characters';
  keyboardType?: 'default' | 'email-address' | 'phone-pad';
  style?: StyleProp<ViewStyle>;
  testID?: string;
}

export function FormField({
  label,
  value,
  onChangeText,
  error,
  placeholder,
  secureTextEntry = false,
  autoCapitalize = 'none',
  keyboardType = 'default',
  style,
  testID,
}: FormFieldProps) {
  if (secureTextEntry) {
    return (
      <PasswordInput
        label={label}
        value={value}
        onChangeText={onChangeText}
        error={error}
        placeholder={placeholder}
        style={style}
        testID={testID}
      />
    );
  }

  return (
    <TextInput
      label={label}
      value={value}
      onChangeText={onChangeText}
      error={error}
      placeholder={placeholder}
      autoCapitalize={autoCapitalize}
      keyboardType={keyboardType}
      style={style}
      testID={testID}
    />
  );
}
