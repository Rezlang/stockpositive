import React, { useState, useEffect } from 'react';
import {
  View,
  Modal,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '@/contexts/ThemeContext';
import { UserFeedResponse, CreateFeedRequest, UpdateFeedRequest } from '@/types/api';
import { ThemedText } from '@/components/atoms/Text/ThemedText';
import { TextInput } from '@/components/atoms/Input/TextInput';
import { PrimaryButton } from '@/components/atoms/Button/PrimaryButton';
import { SecondaryButton } from '@/components/atoms/Button/SecondaryButton';
import { StockTagInput } from '@/components/molecules/StockTag/StockTagInput';
import { SourceCheckbox } from '@/components/molecules/SourceSelector/SourceCheckbox';

interface FeedEditorProps {
  visible: boolean;
  feed?: UserFeedResponse | null;
  onClose: () => void;
  onSave: (data: CreateFeedRequest | UpdateFeedRequest) => Promise<void>;
  isLoading?: boolean;
}

export function FeedEditor({
  visible,
  feed,
  onClose,
  onSave,
  isLoading = false,
}: FeedEditorProps) {
  const { colors } = useTheme();
  const isEditing = !!feed;

  const [feedname, setFeedname] = useState('');
  const [stocks, setStocks] = useState<string[]>([]);
  const [sources, setSources] = useState<string[]>([]);
  const [errors, setErrors] = useState<{
    feedname?: string;
    stocks?: string;
    sources?: string;
  }>({});

  // Reset form when modal opens/closes or feed changes
  useEffect(() => {
    if (visible) {
      if (feed) {
        setFeedname(feed.feedname);
        setStocks(feed.stocks);
        setSources(feed.sources);
      } else {
        setFeedname('');
        setStocks([]);
        setSources([]);
      }
      setErrors({});
    }
  }, [visible, feed]);

  const validate = (): boolean => {
    const newErrors: typeof errors = {};

    if (!feedname.trim()) {
      newErrors.feedname = 'Feed name is required';
    }
    if (stocks.length === 0) {
      newErrors.stocks = 'At least one stock is required';
    }
    if (sources.length === 0) {
      newErrors.sources = 'At least one source is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = async () => {
    if (!validate()) return;

    try {
      await onSave({
        feedname: feedname.trim(),
        stocks,
        sources,
      });
      onClose();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to save feed';
      Alert.alert('Error', message);
    }
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={onClose}
    >
      <SafeAreaView
        style={[styles.container, { backgroundColor: colors.background }]}
      >
        <View style={styles.header}>
          <TouchableOpacity onPress={onClose} style={styles.closeButton}>
            <Ionicons name="close" size={28} color={colors.text} />
          </TouchableOpacity>
          <ThemedText variant="title" style={styles.headerTitle}>
            {isEditing ? 'Edit Feed' : 'Create Feed'}
          </ThemedText>
          <View style={styles.headerSpacer} />
        </View>

        <KeyboardAvoidingView
          style={styles.content}
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        >
          <ScrollView
            contentContainerStyle={styles.scrollContent}
            keyboardShouldPersistTaps="handled"
            showsVerticalScrollIndicator={false}
          >
            <TextInput
              label="Feed Name"
              value={feedname}
              onChangeText={setFeedname}
              placeholder="e.g., Tech Stocks, Market Watch"
              error={errors.feedname}
              autoCapitalize="words"
            />

            <StockTagInput
              label="Stocks to Track"
              value={stocks}
              onChange={setStocks}
              error={errors.stocks}
            />

            <SourceCheckbox
              label="News Sources"
              sources={sources}
              onChange={setSources}
              error={errors.sources}
            />
          </ScrollView>

          <View style={[styles.footer, { borderTopColor: colors.border }]}>
            <SecondaryButton
              title="Cancel"
              onPress={onClose}
              style={styles.footerButton}
            />
            <PrimaryButton
              title={isEditing ? 'Save Changes' : 'Create Feed'}
              onPress={handleSave}
              loading={isLoading}
              style={styles.footerButton}
            />
          </View>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  closeButton: {
    padding: 4,
  },
  headerTitle: {
    flex: 1,
    textAlign: 'center',
  },
  headerSpacer: {
    width: 36,
  },
  content: {
    flex: 1,
  },
  scrollContent: {
    padding: 24,
  },
  footer: {
    flexDirection: 'row',
    gap: 12,
    padding: 16,
    borderTopWidth: 1,
  },
  footerButton: {
    flex: 1,
  },
});
