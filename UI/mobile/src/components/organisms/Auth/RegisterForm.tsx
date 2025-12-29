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
import {
  useFormValidation,
  validationPatterns,
  passwordValidator,
} from '@/hooks/useFormValidation';

interface RegisterFormProps {
  onSwitchToLogin: () => void;
  onSuccess?: () => void;
}

export function RegisterForm({ onSwitchToLogin, onSuccess }: RegisterFormProps) {
  const { colors } = useTheme();
  const { register, isLoading, error, clearError } = useAuth();
  const [submitError, setSubmitError] = useState<string | null>(null);

  const { values, errors, touched, setValue, setTouched, validate } =
    useFormValidation(
      {
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
      },
      {
        username: {
          required: true,
          minLength: 3,
          maxLength: 50,
        },
        email: {
          required: true,
          pattern: validationPatterns.email,
        },
        password: {
          required: true,
          custom: passwordValidator,
        },
        confirmPassword: {
          required: true,
          custom: (value) => {
            if (value !== values.password) {
              return 'Passwords do not match';
            }
            return null;
          },
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
      await register({
        username: values.username,
        email: values.email,
        password: values.password,
      });
      onSuccess?.();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Registration failed';
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
            Create Account
          </ThemedText>
          <ThemedText variant="body" color="secondary">
            Sign up to get personalized news feeds
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
            label="Username"
            value={values.username}
            onChangeText={(text) => setValue('username', text)}
            error={touched.username ? errors.username : null}
            placeholder="Choose a username"
            autoCapitalize="none"
          />

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
            placeholder="Create a password"
            secureTextEntry
          />

          <FormField
            label="Confirm Password"
            value={values.confirmPassword}
            onChangeText={(text) => setValue('confirmPassword', text)}
            error={touched.confirmPassword ? errors.confirmPassword : null}
            placeholder="Confirm your password"
            secureTextEntry
          />

          <View style={styles.passwordHint}>
            <ThemedText variant="caption" color="muted">
              Password must contain at least 8 characters, one uppercase, one
              lowercase, one digit, and one special character.
            </ThemedText>
          </View>

          <PrimaryButton
            title="Create Account"
            onPress={handleSubmit}
            loading={isLoading}
            style={styles.submitButton}
          />
        </View>

        <View style={styles.footer}>
          <ThemedText variant="body" color="secondary">
            Already have an account?
          </ThemedText>
          <SecondaryButton
            title="Sign In"
            onPress={onSwitchToLogin}
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
  passwordHint: {
    marginTop: -8,
    marginBottom: 16,
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
