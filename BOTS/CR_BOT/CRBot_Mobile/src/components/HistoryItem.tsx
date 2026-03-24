import React from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../theme/colors';
import type { HistoryEntry } from '../types';

interface HistoryItemProps {
  entry: HistoryEntry;
  onPress: () => void;
  onDelete: () => void;
}

const STATUS_LABELS: Record<string, { label: string; color: string }> = {
  recorded: { label: 'Enregistré', color: colors.textMuted },
  processing: { label: 'En cours...', color: colors.paused },
  cr_ready: { label: 'CR prêt', color: colors.success },
  sent: { label: 'Envoyé', color: colors.primary },
};

export function HistoryItem({ entry, onPress, onDelete }: HistoryItemProps) {
  const statusInfo = STATUS_LABELS[entry.status] ?? STATUS_LABELS.recorded;
  const date = new Date(entry.date);
  const dateStr = date.toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
  const timeStr = date.toLocaleTimeString('fr-FR', {
    hour: '2-digit',
    minute: '2-digit',
  });
  const durationMin = Math.round(entry.duration_seconds / 60);

  return (
    <Pressable style={styles.container} onPress={onPress}>
      <View style={styles.left}>
        <Text style={styles.date}>{dateStr} à {timeStr}</Text>
        <Text style={styles.meta}>{durationMin} min</Text>
      </View>
      <View style={styles.right}>
        <Text style={[styles.status, { color: statusInfo.color }]}>
          {statusInfo.label}
        </Text>
        <Pressable onPress={onDelete} hitSlop={12}>
          <Ionicons name="trash-outline" size={18} color={colors.textMuted} />
        </Pressable>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 14,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: colors.surfaceBorder,
  },
  left: { flex: 1 },
  date: { color: colors.text, fontSize: 16, fontWeight: '600' },
  meta: { color: colors.textMuted, fontSize: 13, marginTop: 2 },
  right: { alignItems: 'flex-end', gap: 8 },
  status: { fontSize: 13, fontWeight: '600' },
});
