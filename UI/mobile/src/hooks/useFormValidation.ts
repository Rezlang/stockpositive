import { useState, useCallback, useMemo } from 'react';

interface ValidationRules {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  custom?: (value: string) => string | null;
}

type ValidationErrors<T> = Record<keyof T, string | null>;
type TouchedFields<T> = Record<keyof T, boolean>;

interface UseFormValidationResult<T extends Record<string, string>> {
  values: T;
  errors: ValidationErrors<T>;
  touched: TouchedFields<T>;
  setValue: (field: keyof T, value: string) => void;
  setTouched: (field: keyof T) => void;
  validate: () => boolean;
  validateField: (field: keyof T) => string | null;
  reset: () => void;
  isValid: boolean;
}

export function useFormValidation<T extends Record<string, string>>(
  initialValues: T,
  rules: Partial<Record<keyof T, ValidationRules>>
): UseFormValidationResult<T> {
  const [values, setValues] = useState<T>(initialValues);
  const [touched, setTouchedFields] = useState<TouchedFields<T>>(
    () => Object.keys(initialValues).reduce((acc, key) => ({ ...acc, [key]: false }), {} as TouchedFields<T>)
  );
  const [errors, setErrors] = useState<ValidationErrors<T>>(
    () => Object.keys(initialValues).reduce((acc, key) => ({ ...acc, [key]: null }), {} as ValidationErrors<T>)
  );

  const validateField = useCallback(
    (field: keyof T): string | null => {
      const value = values[field];
      const fieldRules = rules[field];

      if (!fieldRules) return null;

      if (fieldRules.required && !value.trim()) {
        return 'This field is required';
      }

      if (fieldRules.minLength && value.length < fieldRules.minLength) {
        return `Must be at least ${fieldRules.minLength} characters`;
      }

      if (fieldRules.maxLength && value.length > fieldRules.maxLength) {
        return `Must be at most ${fieldRules.maxLength} characters`;
      }

      if (fieldRules.pattern && !fieldRules.pattern.test(value)) {
        return 'Invalid format';
      }

      if (fieldRules.custom) {
        return fieldRules.custom(value);
      }

      return null;
    },
    [values, rules]
  );

  const setValue = useCallback(
    (field: keyof T, value: string) => {
      setValues((prev) => ({ ...prev, [field]: value }));

      // Validate on change if field was already touched
      if (touched[field]) {
        const error = validateField(field);
        setErrors((prev) => ({ ...prev, [field]: error }));
      }
    },
    [touched, validateField]
  );

  const setTouched = useCallback(
    (field: keyof T) => {
      setTouchedFields((prev) => ({ ...prev, [field]: true }));
      const error = validateField(field);
      setErrors((prev) => ({ ...prev, [field]: error }));
    },
    [validateField]
  );

  const validate = useCallback((): boolean => {
    const newErrors: ValidationErrors<T> = {} as ValidationErrors<T>;
    let isValid = true;

    (Object.keys(values) as Array<keyof T>).forEach((field) => {
      const error = validateField(field);
      newErrors[field] = error;
      if (error) isValid = false;
    });

    setErrors(newErrors);
    setTouchedFields(
      Object.keys(values).reduce((acc, key) => ({ ...acc, [key]: true }), {} as TouchedFields<T>)
    );

    return isValid;
  }, [values, validateField]);

  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors(
      Object.keys(initialValues).reduce((acc, key) => ({ ...acc, [key]: null }), {} as ValidationErrors<T>)
    );
    setTouchedFields(
      Object.keys(initialValues).reduce((acc, key) => ({ ...acc, [key]: false }), {} as TouchedFields<T>)
    );
  }, [initialValues]);

  const isValid = useMemo(() => {
    return Object.values(errors).every((error) => error === null) &&
      Object.values(values).every((value) => (value as string).length > 0);
  }, [errors, values]);

  return {
    values,
    errors,
    touched,
    setValue,
    setTouched,
    validate,
    validateField,
    reset,
    isValid,
  };
}

// Common validation patterns
export const validationPatterns = {
  email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  // Password: min 8 chars, 1 digit, 1 uppercase, 1 lowercase, 1 special char
  password: /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$/,
};

export const passwordValidator = (value: string): string | null => {
  if (value.length < 8) {
    return 'Password must be at least 8 characters';
  }
  if (!/\d/.test(value)) {
    return 'Password must contain at least one digit';
  }
  if (!/[a-z]/.test(value)) {
    return 'Password must contain at least one lowercase letter';
  }
  if (!/[A-Z]/.test(value)) {
    return 'Password must contain at least one uppercase letter';
  }
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(value)) {
    return 'Password must contain at least one special character';
  }
  return null;
};
