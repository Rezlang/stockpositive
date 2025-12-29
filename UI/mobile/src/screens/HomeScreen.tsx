import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import type { RootTabScreenProps } from '../navigation/types';

export default function HomeScreen({ navigation }: RootTabScreenProps<'Home'>) {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Welcome to StockPositive</Text>
        <Text style={styles.subtitle}>Home Screen</Text>
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Market Overview</Text>
          <Text style={styles.cardText}>
            Track your favorite stocks and stay updated with the latest market news.
          </Text>
        </View>
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Your Portfolio</Text>
          <Text style={styles.cardText}>
            View your stock holdings and performance metrics.
          </Text>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  content: {
    padding: 16,
    paddingTop: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#000',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 24,
  },
  card: {
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#007AFF',
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
    color: '#000',
  },
  cardText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
});