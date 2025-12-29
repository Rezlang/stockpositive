# UI Components

Guide for building UI components in the StockPositive React Native mobile app.

## Component Architecture

### Atomic Design Pattern

Components are organized by complexity:
- **Atoms**: Basic components (Button, Input, Text)
- **Molecules**: Simple combinations (NewsCard, SearchBar)
- **Organisms**: Complex components (NewsFeed, StockChart)
- **Templates**: Page layouts
- **Pages**: Complete screens

## UI Library: React Native Paper

React Native Paper provides Material Design components.

### Setup

Already installed in [Setup Guide](setup.md).

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
  },
};
```

## Common Components

### NewsCard

**File**: `src/components/news/NewsCard.tsx`

```typescript
import React from 'react';
import { StyleSheet } from 'react-native';
import { Card, Title, Paragraph, Chip } from 'react-native-paper';
import { NewsArticle } from '../../types/news.types';

interface Props {
  article: NewsArticle;
  onPress?: () => void;
}

export default function NewsCard({ article, onPress }: Props) {
  return (
    <Card style={styles.card} onPress={onPress}>
      {article.image_url && (
        <Card.Cover source={{ uri: article.image_url }} />
      )}
      <Card.Content>
        <Title numberOfLines={2}>{article.title}</Title>
        <Paragraph numberOfLines={3}>{article.description}</Paragraph>
        {article.sentiment && (
          <Chip mode="outlined" style={styles.chip}>
            {article.sentiment}
          </Chip>
        )}
      </Card.Content>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    marginVertical: 8,
    marginHorizontal: 16,
  },
  chip: {
    alignSelf: 'flex-start',
    marginTop: 8,
  },
});
```

### Loading Indicator

```typescript
import { ActivityIndicator } from 'react-native-paper';

<ActivityIndicator animating={true} size="large" />
```

## Styling Patterns

### StyleSheet

```typescript
const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  text: {
    fontSize: 16,
    color: '#333',
  },
});
```

### Responsive Design

```typescript
import { Dimensions } from 'react-native';

const { width } = Dimensions.get('window');

const styles = StyleSheet.create({
  card: {
    width: width - 32, // Full width minus padding
  },
});
```

## Best Practices

1. **Use React Native Paper** for consistent UI
2. **Create reusable components**
3. **Extract styles to StyleSheet**
4. **Use TypeScript interfaces** for props
5. **Handle loading and error states**
6. **Optimize FlatList** with memoization

## Next Steps

- [Navigation](navigation.md)
- [Extending](extending.md)
