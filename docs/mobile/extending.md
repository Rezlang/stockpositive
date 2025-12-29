# Extending the Mobile App

Guide for adding new features to the StockPositive React Native mobile app.

## Adding a New Screen

### Step 1: Create Screen Component

**File**: `src/screens/portfolio/PortfolioScreen.tsx`

```typescript
import React, { useEffect } from 'react';
import { View, StyleSheet } from 'react-native';
import { Text } from 'react-native-paper';
import { useAppDispatch, useAppSelector } from '../../hooks';

export default function PortfolioScreen() {
  const dispatch = useAppDispatch();

  useEffect(() => {
    // Fetch portfolio data
  }, []);

  return (
    <View style={styles.container}>
      <Text variant="headlineMedium">Portfolio</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
});
```

### Step 2: Add to Navigator

**File**: `src/navigation/MainNavigator.tsx`

```typescript
import PortfolioScreen from '../screens/portfolio/PortfolioScreen';

<Tab.Screen
  name="Portfolio"
  component={PortfolioScreen}
  options={{
    tabBarIcon: ({ color, size }) => (
      <MaterialCommunityIcons name="briefcase" color={color} size={size} />
    ),
  }}
/>
```

## Adding a New API Endpoint

### Step 1: Create API Service

**File**: `src/services/api/portfolioService.ts`

```typescript
import apiClient from './client';

export interface Portfolio {
  stocks: Array<{
    symbol: string;
    shares: number;
    avgPrice: number;
  }>;
}

export const getPortfolio = async (): Promise<Portfolio> => {
  const response = await apiClient.get<Portfolio>('/portfolio');
  return response.data;
};
```

### Step 2: Create Redux Slice

**File**: `src/store/slices/portfolioSlice.ts`

```typescript
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { getPortfolio } from '../../services/api/portfolioService';

export const fetchPortfolio = createAsyncThunk(
  'portfolio/fetch',
  async () => {
    return await getPortfolio();
  }
);

const portfolioSlice = createSlice({
  name: 'portfolio',
  initialState: {
    data: null,
    loading: false,
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchPortfolio.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchPortfolio.fulfilled, (state, action) => {
        state.data = action.payload;
        state.loading = false;
      });
  },
});

export default portfolioSlice.reducer;
```

### Step 3: Add to Store

**File**: `src/store/store.ts`

```typescript
import portfolioReducer from './slices/portfolioSlice';

export const store = configureStore({
  reducer: {
    // ... existing reducers
    portfolio: portfolioReducer,
  },
});
```

## Adding a New UI Component

**File**: `src/components/portfolio/StockCard.tsx`

```typescript
import React from 'react';
import { StyleSheet } from 'react-native';
import { Card, Title, Paragraph } from 'react-native-paper';

interface Props {
  symbol: string;
  shares: number;
  avgPrice: number;
}

export default function StockCard({ symbol, shares, avgPrice }: Props) {
  return (
    <Card style={styles.card}>
      <Card.Content>
        <Title>{symbol}</Title>
        <Paragraph>Shares: {shares}</Paragraph>
        <Paragraph>Avg Price: ${avgPrice.toFixed(2)}</Paragraph>
      </Card.Content>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    margin: 8,
  },
});
```

## Testing New Features

```typescript
// Example test
import { render } from '@testing-library/react-native';
import StockCard from '../StockCard';

test('renders stock card', () => {
  const { getByText } = render(
    <StockCard symbol="AAPL" shares={10} avgPrice={150.50} />
  );
  expect(getByText('AAPL')).toBeTruthy();
});
```

## Best Practices

1. **Follow existing patterns**
2. **Use TypeScript** for type safety
3. **Create reusable components**
4. **Write tests** for new features
5. **Handle errors** gracefully
6. **Update documentation**

## Deployment

### Build for Production

**Expo**:
```bash
eas build --platform ios
eas build --platform android
```

**React Native CLI**:
```bash
# iOS
cd ios && xcodebuild
# Android
cd android && ./gradlew assembleRelease
```

## Resources

- [React Navigation Docs](https://reactnavigation.org/)
- [React Native Paper Docs](https://callstack.github.io/react-native-paper/)
- [Redux Toolkit Docs](https://redux-toolkit.js.org/)
- [Backend API Reference](../backend/api.md)
