// Theme Types

export type ThemeMode = 'light' | 'dark';

export interface ThemeColors {
  // Backgrounds
  background: string;
  surface: string;
  card: string;

  // Text
  text: string;
  textSecondary: string;
  textMuted: string;

  // Brand colors
  primary: string;
  primaryLight: string;

  // Status colors
  success: string;
  error: string;
  warning: string;
  info: string;

  // Sentiment colors
  sentimentPositive: string;
  sentimentNegative: string;
  sentimentNeutral: string;

  // UI elements
  border: string;
  divider: string;
  overlay: string;

  // Tab bar
  tabBarBackground: string;
  tabBarActive: string;
  tabBarInactive: string;

  // Input
  inputBackground: string;
  inputBorder: string;
  inputPlaceholder: string;
}

export interface Theme {
  mode: ThemeMode;
  colors: ThemeColors;
}
