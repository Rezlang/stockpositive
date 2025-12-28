# React Native Project Setup

This guide walks through setting up a React Native project for the StockPositive mobile app.

## Prerequisites

- **Node.js** 18+ (LTS recommended)
- **npm** or **yarn**
- **Expo CLI** (recommended) or React Native CLI
- **iOS**: Xcode (macOS only)
- **Android**: Android Studio

## Option 1: Expo (Recommended)

Expo provides a managed workflow with simplified setup and deployment.

### Create Project

```bash
npx create-expo-app stockpositive-mobile
cd stockpositive-mobile
```

### Install Dependencies

```bash
# Navigation
npm install @react-navigation/native @react-navigation/stack @react-navigation/bottom-tabs
npm install react-native-screens react-native-safe-area-context

# State Management (Redux Toolkit)
npm install @reduxjs/toolkit react-redux

# API Communication
npm install axios

# Storage
npm install @react-native-async-storage/async-storage

# UI Components (React Native Paper)
npm install react-native-paper react-native-vector-icons

# Forms
npm install react-hook-form yup @hookform/resolvers

# Charts
npm install react-native-chart-kit react-native-svg

# Other
npm install react-native-dotenv
```

### TypeScript Setup

Expo projects come with TypeScript by default. If not:

```bash
npx expo install typescript @types/react @types/react-native
```

Create `tsconfig.json`:
```json
{
  "extends": "expo/tsconfig.base",
  "compilerOptions": {
    "strict": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

### Project Structure

```bash
mkdir -p src/{screens,components,navigation,store,services,types,hooks,utils,constants}
mkdir -p src/screens/{auth,news,stocks,feeds}
mkdir -p src/components/{common,news,stocks}
mkdir -p src/services/{api,storage}
mkdir -p src/store/slices
```

### Environment Variables

Create `.env` file:
```env
API_BASE_URL=http://localhost:8000
```

Configure in `app.json`:
```json
{
  "expo": {
    "extra": {
      "apiBaseUrl": process.env.API_BASE_URL
    }
  }
}
```

### Run the App

```bash
npx expo start
```

Options:
- Press `i` for iOS simulator
- Press `a` for Android emulator
- Scan QR code with Expo Go app for physical device

---

## Option 2: React Native CLI

For more control and native module access.

### Create Project

```bash
npx react-native init StockPositiveMobile --template react-native-template-typescript
cd StockPositiveMobile
```

### Install Dependencies

```bash
# Navigation
npm install @react-navigation/native @react-navigation/stack @react-navigation/bottom-tabs
npm install react-native-screens react-native-safe-area-context react-native-gesture-handler

# State Management
npm install @reduxjs/toolkit react-redux

# API
npm install axios

# Storage
npm install @react-native-async-storage/async-storage

# UI
npm install react-native-paper react-native-vector-icons

# Forms
npm install react-hook-form yup @hookform/resolvers

# Charts
npm install react-native-chart-kit react-native-svg

# Link native dependencies (iOS)
cd ios && pod install && cd ..
```

### Run the App

```bash
# iOS
npx react-native run-ios

# Android
npx react-native run-android
```

---

## TypeScript Configuration

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "esnext",
    "module": "commonjs",
    "lib": ["es2017"],
    "allowJs": true,
    "jsx": "react-native",
    "noEmit": true,
    "isolatedModules": true,
    "strict": true,
    "moduleResolution": "node",
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"],
      "@screens/*": ["src/screens/*"],
      "@services/*": ["src/services/*"],
      "@types/*": ["src/types/*"]
    },
    "allowSyntheticDefaultImports": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "resolveJsonModule": true
  },
  "exclude": [
    "node_modules",
    "babel.config.js",
    "metro.config.js"
  ]
}
```

### babel.config.js

```javascript
module.exports = {
  presets: ['module:metro-react-native-babel-preset'],
  plugins: [
    [
      'module-resolver',
      {
        root: ['./src'],
        alias: {
          '@': './src',
          '@components': './src/components',
          '@screens': './src/screens',
          '@services': './src/services',
          '@types': './src/types'
        }
      }
    ]
  ]
};
```

---

## Redux Toolkit Setup

### Create Store

**File**: `src/store/store.ts`

```typescript
import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import newsReducer from './slices/newsSlice';
import feedsReducer from './slices/feedsSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    news: newsReducer,
    feeds: feedsReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

### Wrap App with Provider

**File**: `App.tsx`

```typescript
import React from 'react';
import { Provider } from 'react-redux';
import { store } from './src/store/store';
import RootNavigator from './src/navigation/RootNavigator';

export default function App() {
  return (
    <Provider store={store}>
      <RootNavigator />
    </Provider>
  );
}
```

---

## React Navigation Setup

### Install Dependencies

Already installed in previous steps.

### Create Root Navigator

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

---

## Axios Setup

### Create API Client

**File**: `src/services/api/client.ts`

```typescript
import axios from 'axios';
import { getToken } from '../storage/tokenStorage';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  async (config) => {
    const token = await getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle token expiration
      // Dispatch logout action
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

---

## AsyncStorage Setup

### Token Storage Service

**File**: `src/services/storage/tokenStorage.ts`

```typescript
import AsyncStorage from '@react-native-async-storage/async-storage';

const TOKEN_KEY = '@stockpositive_token';

export const saveToken = async (token: string): Promise<void> => {
  try {
    await AsyncStorage.setItem(TOKEN_KEY, token);
  } catch (error) {
    console.error('Error saving token:', error);
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
  } catch (error) {
    console.error('Error removing token:', error);
  }
};
```

---

## React Native Paper Setup

### Wrap App with Provider

**File**: `App.tsx`

```typescript
import React from 'react';
import { Provider as StoreProvider } from 'react-redux';
import { Provider as PaperProvider } from 'react-native-paper';
import { store } from './src/store/store';
import { theme } from './src/constants/theme';
import RootNavigator from './src/navigation/RootNavigator';

export default function App() {
  return (
    <StoreProvider store={store}>
      <PaperProvider theme={theme}>
        <RootNavigator />
      </PaperProvider>
    </StoreProvider>
  );
}
```

### Theme Configuration

**File**: `src/constants/theme.ts`

```typescript
import { DefaultTheme } from 'react-native-paper';

export const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#1E88E5',
    accent: '#FFC107',
    background: '#FFFFFF',
    surface: '#F5F5F5',
    error: '#F44336',
    text: '#212121',
    onSurface: '#757575',
    disabled: '#BDBDBD',
    placeholder: '#9E9E9E',
    backdrop: '#000000',
    notification: '#F44336',
  },
};
```

---

## Development Tools

### ESLint

```bash
npm install --save-dev eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
```

**.eslintrc.js**:
```javascript
module.exports = {
  root: true,
  extends: [
    '@react-native',
    'plugin:@typescript-eslint/recommended',
  ],
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint'],
  rules: {
    'no-console': 'warn',
    '@typescript-eslint/no-unused-vars': 'error',
  },
};
```

### Prettier

```bash
npm install --save-dev prettier
```

**.prettierrc**:
```json
{
  "singleQuote": true,
  "trailingComma": "es5",
  "tabWidth": 2,
  "semi": true,
  "printWidth": 100
}
```

---

## Testing Setup

### Jest (comes with React Native)

```bash
npm install --save-dev @testing-library/react-native @testing-library/jest-native
```

### Run Tests

```bash
npm test
```

---

## Build and Deployment

### Expo

```bash
# Install EAS CLI
npm install -g eas-cli

# Configure EAS
eas build:configure

# Build for iOS
eas build --platform ios

# Build for Android
eas build --platform android
```

### React Native CLI

```bash
# iOS
cd ios && xcodebuild

# Android
cd android && ./gradlew assembleRelease
```

---

## Troubleshooting

### Metro Bundler Issues

```bash
# Clear cache
npx react-native start --reset-cache
```

### Pod Install Fails (iOS)

```bash
cd ios
pod deintegrate
pod install
cd ..
```

### Android Build Fails

```bash
cd android
./gradlew clean
cd ..
```

---

## Next Steps

- [Authentication Implementation](authentication.md)
- [API Integration](api-integration.md)
- [State Management](state-management.md)
- [UI Components](ui-components.md)
