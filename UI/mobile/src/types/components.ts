import { ReactNode } from 'react';
import { StyleProp, ViewStyle, TextStyle } from 'react-native';
import { NewsArticle, UserFeedResponse } from './api';

// Common prop patterns
export interface BaseComponentProps {
  style?: StyleProp<ViewStyle>;
  testID?: string;
}

export interface TextComponentProps extends BaseComponentProps {
  textStyle?: StyleProp<TextStyle>;
}

export interface PressableComponentProps extends BaseComponentProps {
  onPress?: () => void;
  disabled?: boolean;
}

export interface ChildrenProps {
  children: ReactNode;
}

// Button variants
export type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost';
export type ButtonSize = 'small' | 'medium' | 'large';

export interface ButtonProps extends PressableComponentProps {
  title: string;
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  icon?: ReactNode;
}

// Input props
export interface TextInputProps extends BaseComponentProps {
  value: string;
  onChangeText: (text: string) => void;
  placeholder?: string;
  error?: string | null;
  label?: string;
  autoCapitalize?: 'none' | 'sentences' | 'words' | 'characters';
  keyboardType?: 'default' | 'email-address' | 'phone-pad' | 'numeric';
  secureTextEntry?: boolean;
  multiline?: boolean;
  maxLength?: number;
  editable?: boolean;
}

// Specific component props
export interface NewsCardProps extends PressableComponentProps {
  article: NewsArticle;
  compact?: boolean;
}

export interface FeedListItemProps extends PressableComponentProps {
  feed: UserFeedResponse;
  isActive?: boolean;
  onEdit?: () => void;
  onDelete?: () => void;
}

export interface FormFieldProps {
  label: string;
  value: string;
  onChangeText: (text: string) => void;
  error?: string | null;
  placeholder?: string;
  secureTextEntry?: boolean;
  autoCapitalize?: 'none' | 'sentences' | 'words' | 'characters';
  keyboardType?: 'default' | 'email-address' | 'phone-pad';
}

export interface EmptyStateProps extends BaseComponentProps {
  icon?: string;
  title: string;
  message?: string;
  actionLabel?: string;
  onAction?: () => void;
}

export interface ErrorMessageProps extends BaseComponentProps {
  message: string;
  onRetry?: () => void;
}

export interface TagChipProps extends BaseComponentProps {
  label: string;
  onRemove?: () => void;
  selected?: boolean;
  onSelect?: () => void;
}

export interface SentimentBadgeProps extends BaseComponentProps {
  sentiment: string | null;
}
