import AsyncStorage from '@react-native-async-storage/async-storage';
import { STORAGE_KEYS } from '@/constants/config';
import { ThemeMode } from '@/types/theme';

export const storageService = {
  // Theme
  async getTheme(): Promise<ThemeMode | null> {
    try {
      const theme = await AsyncStorage.getItem(STORAGE_KEYS.THEME);
      if (theme === 'light' || theme === 'dark') {
        return theme;
      }
      return null;
    } catch {
      return null;
    }
  },

  async setTheme(theme: ThemeMode): Promise<void> {
    try {
      await AsyncStorage.setItem(STORAGE_KEYS.THEME, theme);
    } catch (error) {
      console.error('Failed to save theme:', error);
    }
  },

  // Auth token
  async getToken(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
    } catch {
      return null;
    }
  },

  async setToken(token: string): Promise<void> {
    try {
      await AsyncStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, token);
    } catch (error) {
      console.error('Failed to save token:', error);
    }
  },

  async removeToken(): Promise<void> {
    try {
      await AsyncStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
    } catch (error) {
      console.error('Failed to remove token:', error);
    }
  },

  // Active feed
  async getActiveFeedId(): Promise<number | null> {
    try {
      const id = await AsyncStorage.getItem(STORAGE_KEYS.ACTIVE_FEED_ID);
      return id ? parseInt(id, 10) : null;
    } catch {
      return null;
    }
  },

  async setActiveFeedId(id: number): Promise<void> {
    try {
      await AsyncStorage.setItem(STORAGE_KEYS.ACTIVE_FEED_ID, id.toString());
    } catch (error) {
      console.error('Failed to save active feed ID:', error);
    }
  },

  async removeActiveFeedId(): Promise<void> {
    try {
      await AsyncStorage.removeItem(STORAGE_KEYS.ACTIVE_FEED_ID);
    } catch (error) {
      console.error('Failed to remove active feed ID:', error);
    }
  },

  // Clear all app data
  async clearAll(): Promise<void> {
    try {
      const keys = Object.values(STORAGE_KEYS);
      await AsyncStorage.multiRemove(keys);
    } catch (error) {
      console.error('Failed to clear storage:', error);
    }
  },
};
