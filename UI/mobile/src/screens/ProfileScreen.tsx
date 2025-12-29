import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import type { RootTabScreenProps } from '../navigation/types';

export default function ProfileScreen({ navigation }: RootTabScreenProps<'Profile'>) {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>User Profile</Text>
        <Text style={styles.subtitle}>Profile Screen</Text>
        <View style={styles.profileCard}>
          <Text style={styles.label}>Name</Text>
          <Text style={styles.value}>John Investor</Text>
        </View>
        <View style={styles.profileCard}>
          <Text style={styles.label}>Account Status</Text>
          <Text style={styles.value}>Active</Text>
        </View>
        <View style={styles.profileCard}>
          <Text style={styles.label}>Portfolio Value</Text>
          <Text style={styles.value}>$45,230.50</Text>
        </View>
        <View style={styles.profileCard}>
          <Text style={styles.label}>Total Gain/Loss</Text>
          <Text style={[styles.value, styles.positive]}>+12.5%</Text>
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
  profileCard: {
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#34C759',
  },
  label: {
    fontSize: 12,
    color: '#999',
    textTransform: 'uppercase',
    fontWeight: '600',
    marginBottom: 4,
  },
  value: {
    fontSize: 18,
    fontWeight: '600',
    color: '#000',
  },
  positive: {
    color: '#34C759',
  },
});