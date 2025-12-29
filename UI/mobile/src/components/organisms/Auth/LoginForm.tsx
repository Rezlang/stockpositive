import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { useAuth } from '@/contexts/AuthContext';
import { ThemedText } from '@/components/atoms/Text/ThemedText';
import { PrimaryButton } from '@/components/atoms/Button/PrimaryButton';
import { SecondaryButton } from '@/components/atoms/Button/SecondaryButton';
import { FormField } from '@/components/molecules/FormField/FormField';
import { useFormValidation, validationPatterns } from '@/hooks/useFormValidation';

interface LoginFormProps {
  onSwitchToRegister: () => void;
  onSuccess?: () => void;
}

export function LoginForm({ onSwitchToRegister, onSuccess }: LoginFormProps) {
  const { colors } = useTheme();
  const { login, isLoading, error, clearError } = useAuth();
  const [submitError, setSubmitError] = useState<string | null>(null);

  const { values, errors, touched, setValue, setTouched, validate } =
    useFormValidation(
      { email: '', password: '' },
      {
        email: {
          required: true,
          pattern: validationPatterns.email,
        },
        password: {
          required: true,
          minLength: 1,
        },
      }
    );

  const handleSubmit = async () => {
    clearError();
    setSubmitError(null);

    if (!validate()) {
      return;
    }

    try {
      await login(values.email, values.password);
      onSuccess?.();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed';
      setSubmitError(message);
    }
  };

  const displayError = submitError || error;

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.header}>
          <ThemedText variant="largeTitle" style={styles.title}>
            Welcome Back
          </ThemedText>
          <ThemedText variant="body" color="secondary">
            Sign in to access your news feeds
          </ThemedText>
        </View>

        {displayError && (
          <View
            style={[
              styles.errorContainer,
              { backgroundColor: `${colors.error}15` },
            ]}
          >
            <ThemedText variant="body" color="error">
              {displayError}
            </ThemedText>
          </View>
        )}

        <View style={styles.form}>
          <FormField
            label="Email"
            value={values.email}
            onChangeText={(text) => setValue('email', text)}
            error={touched.email ? errors.email : null}
            placeholder="Enter your email"
            keyboardType="email-address"
            autoCapitalize="none"
          />

          <FormField
            label="Password"
            value={values.password}
            onChangeText={(text) => setValue('password', text)}
            error={touched.password ? errors.password : null}
            placeholder="Enter your password"
            secureTextEntry
          />

          <PrimaryButton
            title="Sign In"
            onPress={handleSubmit}
            loading={isLoading}
            style={styles.submitButton}
          />
        </View>

        <View style={styles.footer}>
          <ThemedText variant="body" color="secondary">
            Don't have an account?
          </ThemedText>
          <SecondaryButton
            title="Create Account"
            onPress={onSwitchToRegister}
            style={styles.switchButton}
          />
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    padding: 24,
  },
  header: {
    marginBottom: 32,
  },
  title: {
    marginBottom: 8,
  },
  errorContainer: {
    padding: 16,
    borderRadius: 12,
    marginBottom: 24,
  },
  form: {
    marginBottom: 32,
  },
  submitButton: {
    marginTop: 8,
  },
  footer: {
    alignItems: 'center',
    gap: 12,
  },
  switchButton: {
    minWidth: 160,
  },
});
