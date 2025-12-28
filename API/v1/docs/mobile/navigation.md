# Navigation

Guide for implementing navigation in the StockPositive React Native mobile app.

## React Navigation

The app uses React Navigation v6+ for routing and navigation.

## Navigation Structure

### Root Navigator

**File**: `src/navigation/RootNavigator.tsx`

```typescript
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { useAppSelector } from '../hooks';
import AuthNavigator from './AuthNavigator';
import MainNavigator from './MainNavigator';

export default function RootNavigator() {
  const { isAuthenticated } = useAppSelector(state => state.auth);

  return (
    <NavigationContainer>
      {isAuthenticated ? <MainNavigator /> : <AuthNavigator />}
    </NavigationContainer>
  );
}
```

### Auth Navigator

**File**: `src/navigation/AuthNavigator.tsx`

```typescript
import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import LoginScreen from '../screens/auth/LoginScreen';
import RegisterScreen from '../screens/auth/RegisterScreen';

const Stack = createStackNavigator();

export default function AuthNavigator() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Register" component={RegisterScreen} />
    </Stack.Navigator>
  );
}
```

### Main Navigator (Tabs)

**File**: `src/navigation/MainNavigator.tsx`

```typescript
import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import NewsFeedScreen from '../screens/news/NewsFeedScreen';
import StockChartScreen from '../screens/stocks/StockChartScreen';
import FeedOptionsScreen from '../screens/feeds/FeedOptionsScreen';

const Tab = createBottomTabNavigator();

export default function MainNavigator() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: true,
        tabBarActiveTintColor: '#1E88E5',
      }}
    >
      <Tab.Screen
        name="News"
        component={NewsFeedScreen}
        options={{
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="newspaper" color={color} size={size} />
          ),
        }}
      />
      <Tab.Screen
        name="Charts"
        component={StockChartScreen}
        options={{
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="chart-line" color={color} size={size} />
          ),
        }}
      />
      <Tab.Screen
        name="Feeds"
        component={FeedOptionsScreen}
        options={{
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="rss" color={color} size={size} />
          ),
        }}
      />
    </Tab.Navigator>
  );
}
```

## Navigation Between Screens

```typescript
// In component
import { useNavigation } from '@react-navigation/native';

const navigation = useNavigation();

// Navigate to screen
navigation.navigate('ScreenName');

// Navigate with params
navigation.navigate('Details', { id: 123 });

// Go back
navigation.goBack();
```

## TypeScript Types

```typescript
export type RootStackParamList = {
  Login: undefined;
  Register: undefined;
  News: undefined;
  Charts: undefined;
  Feeds: undefined;
  Details: { id: number };
};
```

## Deep Linking

Configure deep linking for external navigation.

## Best Practices

1. **Type navigation** with TypeScript
2. **Use hooks** (useNavigation, useRoute)
3. **Optimize screens** with React.memo
4. **Handle back button** on Android

## Next Steps

- [Extending](extending.md)
