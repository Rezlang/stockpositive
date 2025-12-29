import React, { useState } from 'react';
import {
  View,
  TouchableOpacity,
  Modal,
  FlatList,
  StyleSheet,
  SafeAreaView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '@/contexts/ThemeContext';
import { UserFeedResponse } from '@/types/api';
import { ThemedText } from '@/components/atoms/Text/ThemedText';
import { Divider } from '@/components/atoms/Divider/Divider';

interface FeedSelectorProps {
  feeds: UserFeedResponse[];
  activeFeed: UserFeedResponse | null;
  onSelectFeed: (feedId: number) => void;
}

export function FeedSelector({
  feeds,
  activeFeed,
  onSelectFeed,
}: FeedSelectorProps) {
  const { colors } = useTheme();
  const [isOpen, setIsOpen] = useState(false);

  const handleSelect = (feedId: number) => {
    onSelectFeed(feedId);
    setIsOpen(false);
  };

  if (feeds.length === 0) {
    return null;
  }

  return (
    <>
      <TouchableOpacity
        style={[
          styles.selector,
          { backgroundColor: colors.surface, borderColor: colors.border },
        ]}
        onPress={() => setIsOpen(true)}
        activeOpacity={0.7}
      >
        <View style={styles.selectorContent}>
          <Ionicons name="list" size={18} color={colors.primary} />
          <ThemedText variant="body" numberOfLines={1} style={styles.selectorText}>
            {activeFeed?.feedname || 'Select Feed'}
          </ThemedText>
        </View>
        <Ionicons name="chevron-down" size={18} color={colors.textMuted} />
      </TouchableOpacity>

      <Modal
        visible={isOpen}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setIsOpen(false)}
      >
        <SafeAreaView
          style={[styles.modal, { backgroundColor: colors.background }]}
        >
          <View style={styles.modalHeader}>
            <ThemedText variant="title">Select Feed</ThemedText>
            <TouchableOpacity
              onPress={() => setIsOpen(false)}
              hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
            >
              <Ionicons name="close" size={24} color={colors.text} />
            </TouchableOpacity>
          </View>

          <FlatList
            data={feeds}
            keyExtractor={(item) => item.id.toString()}
            renderItem={({ item }) => (
              <TouchableOpacity
                style={[
                  styles.feedItem,
                  item.id === activeFeed?.id && {
                    backgroundColor: colors.primaryLight,
                  },
                ]}
                onPress={() => handleSelect(item.id)}
              >
                <View style={styles.feedItemContent}>
                  <ThemedText
                    variant="subtitle"
                    color={item.id === activeFeed?.id ? 'primary' : undefined}
                  >
                    {item.feedname}
                  </ThemedText>
                  <ThemedText variant="caption" color="muted">
                    {item.stocks.length} stocks · {item.sources.length} sources
                  </ThemedText>
                </View>
                {item.id === activeFeed?.id && (
                  <Ionicons name="checkmark" size={22} color={colors.primary} />
                )}
              </TouchableOpacity>
            )}
            ItemSeparatorComponent={() => <Divider />}
            contentContainerStyle={styles.list}
          />
        </SafeAreaView>
      </Modal>
    </>
  );
}

const styles = StyleSheet.create({
  selector: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 10,
    borderWidth: 1,
  },
  selectorContent: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    gap: 8,
  },
  selectorText: {
    flex: 1,
  },
  modal: {
    flex: 1,
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    borderBottomWidth: 1,
  },
  list: {
    paddingVertical: 8,
  },
  feedItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 14,
  },
  feedItemContent: {
    flex: 1,
    gap: 2,
  },
});
