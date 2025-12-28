# Authentication

This guide covers JWT authentication implementation in the React Native mobile app.

## Overview

The StockPositive mobile app uses JWT (JSON Web Token) authentication to securely communicate with the v1 backend API.

**Flow**:
1. User registers or logs in
2. Backend returns JWT token
3. Token stored in AsyncStorage
4. Token included in all API requests
5. Token refresh/expiration handling

## Auth State Management

### Redux Slice

**File**: `src/store/slices/authSlice.ts`

```typescript
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { login as apiLogin, register as apiRegister } from '../../services/api/authService';
import { saveToken, removeToken } from '../../services/storage/tokenStorage';

interface User {
  id: number;
  username: string;
  email: string;
  permissions: Record<string, number | null>;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  loading: false,
  error: null,
};

// Async thunks
export const login = createAsyncThunk(
  'auth/login',
  async ({ email, password }: { email: string; password: string }, { rejectWithValue }) => {
    try {
      const response = await apiLogin(email, password);
      await saveToken(response.access_token);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Login failed');
    }
  }
);

export const register = createAsyncThunk(
  'auth/register',
  async (userData: { username: string; email: string; password: string }, { rejectWithValue }) => {
    try {
      const response = await apiRegister(userData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Registration failed');
    }
  }
);

export const logout = createAsyncThunk('auth/logout', async () => {
  await removeToken();
});

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials: (state, action: PayloadAction<{ user: User; token: string }>) => {
      state.user = action.payload.user;
      state.token = action.payload.token;
      state.isAuthenticated = true;
    },
    clearAuth: (state) => {
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.token = action.payload.access_token;
        state.isAuthenticated = true;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Register
      .addCase(register.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Logout
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
      });
  },
});

export const { setCredentials, clearAuth } = authSlice.actions;
export default authSlice.reducer;
```

## API Service

### Auth Service

**File**: `src/services/api/authService.ts`

```typescript
import apiClient from './client';

interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface RegisterData {
  username: string;
  email: string;
  password: string;
  phone_number?: string;
}

interface UserResponse {
  id: number;
  username: string;
  email: string;
  usergroup_id: number;
  is_active: boolean;
  created_at: string;
  permissions: Record<string, number | null>;
}

export const login = async (email: string, password: string): Promise<LoginResponse> => {
  const formData = new FormData();
  formData.append('username', email);  // OAuth2 uses 'username' field
  formData.append('password', password);

  const response = await apiClient.post<LoginResponse>('/users/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });

  return response.data;
};

export const register = async (userData: RegisterData): Promise<UserResponse> => {
  const response = await apiClient.post<UserResponse>('/users/register', userData);
  return response.data;
};

export const getCurrentUser = async (): Promise<UserResponse> => {
  const response = await apiClient.get<UserResponse>('/users/me');
  return response.data;
};
```

## Login Screen

**File**: `src/screens/auth/LoginScreen.tsx`

```typescript
import React, { useState } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { TextInput, Button, Text } from 'react-native-paper';
import { useDispatch, useSelector } from 'react-redux';
import { login } from '../../store/slices/authSlice';
import { AppDispatch, RootState } from '../../store/store';

export default function LoginScreen({ navigation }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const dispatch = useDispatch<AppDispatch>();
  const { loading, error } = useSelector((state: RootState) => state.auth);

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    try {
      await dispatch(login({ email, password })).unwrap();
      // Navigation handled by RootNavigator based on auth state
    } catch (err) {
      Alert.alert('Login Failed', error || 'An error occurred');
    }
  };

  return (
    <View style={styles.container}>
      <Text variant="headlineMedium" style={styles.title}>
        StockPositive
      </Text>

      <TextInput
        label="Email"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        keyboardType="email-address"
        style={styles.input}
      />

      <TextInput
        label="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry={!showPassword}
        right={
          <TextInput.Icon
            icon={showPassword ? 'eye-off' : 'eye'}
            onPress={() => setShowPassword(!showPassword)}
          />
        }
        style={styles.input}
      />

      <Button
        mode="contained"
        onPress={handleLogin}
        loading={loading}
        disabled={loading}
        style={styles.button}
      >
        Login
      </Button>

      <Button
        mode="text"
        onPress={() => navigation.navigate('Register')}
        style={styles.registerButton}
      >
        Don't have an account? Register
      </Button>

      {error && <Text style={styles.error}>{error}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
  },
  title: {
    textAlign: 'center',
    marginBottom: 40,
  },
  input: {
    marginBottom: 16,
  },
  button: {
    marginTop: 8,
  },
  registerButton: {
    marginTop: 16,
  },
  error: {
    color: 'red',
    marginTop: 16,
    textAlign: 'center',
  },
});
```

## Register Screen

**File**: `src/screens/auth/RegisterScreen.tsx`

```typescript
import React, { useState } from 'react';
import { View, StyleSheet, Alert, ScrollView } from 'react-native';
import { TextInput, Button, Text } from 'react-native-paper';
import { useDispatch, useSelector } from 'react-redux';
import { register } from '../../store/slices/authSlice';
import { AppDispatch, RootState } from '../../store/store';

export default function RegisterScreen({ navigation }) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const dispatch = useDispatch<AppDispatch>();
  const { loading, error } = useSelector((state: RootState) => state.auth);

  const handleRegister = async () => {
    // Validation
    if (!username || !email || !password || !confirmPassword) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    if (password !== confirmPassword) {
      Alert.alert('Error', 'Passwords do not match');
      return;
    }

    if (password.length < 8) {
      Alert.alert('Error', 'Password must be at least 8 characters');
      return;
    }

    try {
      await dispatch(register({ username, email, password })).unwrap();
      Alert.alert('Success', 'Registration successful! Please login.');
      navigation.navigate('Login');
    } catch (err) {
      Alert.alert('Registration Failed', error || 'An error occurred');
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text variant="headlineMedium" style={styles.title}>
        Create Account
      </Text>

      <TextInput
        label="Username"
        value={username}
        onChangeText={setUsername}
        autoCapitalize="none"
        style={styles.input}
      />

      <TextInput
        label="Email"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        keyboardType="email-address"
        style={styles.input}
      />

      <TextInput
        label="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry={!showPassword}
        right={
          <TextInput.Icon
            icon={showPassword ? 'eye-off' : 'eye'}
            onPress={() => setShowPassword(!showPassword)}
          />
        }
        style={styles.input}
      />

      <TextInput
        label="Confirm Password"
        value={confirmPassword}
        onChangeText={setConfirmPassword}
        secureTextEntry={!showPassword}
        style={styles.input}
      />

      <Button
        mode="contained"
        onPress={handleRegister}
        loading={loading}
        disabled={loading}
        style={styles.button}
      >
        Register
      </Button>

      <Button
        mode="text"
        onPress={() => navigation.navigate('Login')}
        style={styles.loginButton}
      >
        Already have an account? Login
      </Button>

      {error && <Text style={styles.error}>{error}</Text>}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    padding: 20,
    justifyContent: 'center',
  },
  title: {
    textAlign: 'center',
    marginBottom: 40,
  },
  input: {
    marginBottom: 16,
  },
  button: {
    marginTop: 8,
  },
  loginButton: {
    marginTop: 16,
  },
  error: {
    color: 'red',
    marginTop: 16,
    textAlign: 'center',
  },
});
```

## Token Storage

**File**: `src/services/storage/tokenStorage.ts`

```typescript
import AsyncStorage from '@react-native-async-storage/async-storage';

const TOKEN_KEY = '@stockpositive_token';
const USER_KEY = '@stockpositive_user';

export const saveToken = async (token: string): Promise<void> => {
  try {
    await AsyncStorage.setItem(TOKEN_KEY, token);
  } catch (error) {
    console.error('Error saving token:', error);
    throw error;
  }
};

export const getToken = async (): Promise<string | null> => {
  try {
    return await AsyncStorage.getItem(TOKEN_KEY);
  } catch (error) {
    console.error('Error getting token:', error);
    return null;
  }
};

export const removeToken = async (): Promise<void> => {
  try {
    await AsyncStorage.removeItem(TOKEN_KEY);
    await AsyncStorage.removeItem(USER_KEY);
  } catch (error) {
    console.error('Error removing token:', error);
  }
};

export const saveUser = async (user: any): Promise<void> => {
  try {
    await AsyncStorage.setItem(USER_KEY, JSON.stringify(user));
  } catch (error) {
    console.error('Error saving user:', error);
  }
};

export const getUser = async (): Promise<any> => {
  try {
    const userJson = await AsyncStorage.getItem(USER_KEY);
    return userJson ? JSON.parse(userJson) : null;
  } catch (error) {
    console.error('Error getting user:', error);
    return null;
  }
};
```

## Auto-Login on App Launch

**File**: `App.tsx`

```typescript
import React, { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { setCredentials } from './src/store/slices/authSlice';
import { getToken, getUser } from './src/services/storage/tokenStorage';
import { getCurrentUser } from './src/services/api/authService';

export default function App() {
  const dispatch = useDispatch();

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    const token = await getToken();
    if (token) {
      try {
        // Fetch current user data
        const user = await getCurrentUser();
        dispatch(setCredentials({ user, token }));
      } catch (error) {
        // Token invalid or expired, stay logged out
        await removeToken();
      }
    }
  };

  return (
    // ... App component
  );
}
```

## Protected Routes

Navigation automatically handles authentication state.

**File**: `src/navigation/RootNavigator.tsx`

```typescript
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { useSelector } from 'react-redux';
import { RootState } from '../store/store';
import AuthNavigator from './AuthNavigator';
import MainNavigator from './MainNavigator';

export default function RootNavigator() {
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);

  return (
    <NavigationContainer>
      {isAuthenticated ? <MainNavigator /> : <AuthNavigator />}
    </NavigationContainer>
  );
}
```

## Logout Functionality

**Usage in any component**:

```typescript
import { useDispatch } from 'react-redux';
import { logout } from '../store/slices/authSlice';

const dispatch = useDispatch();

const handleLogout = async () => {
  await dispatch(logout());
  // Navigation handled automatically by RootNavigator
};
```

## Token Expiration Handling

**File**: `src/services/api/client.ts` (Response Interceptor)

```typescript
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      await removeToken();
      // Dispatch logout action
      store.dispatch(clearAuth());
      // User will be redirected to login automatically
    }
    return Promise.reject(error);
  }
);
```

## Security Best Practices

1. **Never log tokens** in production
2. **Use HTTPS** for all API calls
3. **Validate input** before sending to API
4. **Handle token expiration** gracefully
5. **Clear sensitive data** on logout
6. **Use secure storage** for tokens (AsyncStorage or Keychain)
7. **Implement biometric authentication** (optional)
8. **Add refresh token logic** if needed

## Next Steps

- [API Integration](api-integration.md) - Full API service implementation
- [State Management](state-management.md) - Complete state management patterns
- [Navigation](navigation.md) - Navigation structure
