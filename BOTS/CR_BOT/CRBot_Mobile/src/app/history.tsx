import React, { useState, useCallback } from 'react';
import { FlatList, View, Text, StyleSheet, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useFocusEffect, useRouter } from 'expo-router';
import * as FileSystem from 'expo-file-system';
import { HistoryItem } from '../components/HistoryItem';
import { StorageManager } from '../services/storage';
import { HISTORY_FILE, RECORDINGS_DIR, CR_DIR } from '../services/config';
import { colors } from '../theme/colors';
import { sharedStyles } from '../theme/styles';
import type { HistoryEntry } from '../types';

const sm = new StorageManager(HISTORY_FILE);

export default function HistoryScreen() {
  const [entries, setEntries] = useState<HistoryEntry[]>([]);
  const [totalSize, setTotalSize] = useState(0);
  const router = useRouter();

  useFocusEffect(
    useCallback(() => {
      sm.getHistory().then(setEntries);
      sm.getTotalSize().then(setTotalSize);
    }, []),
  );

  const formatSize = (bytes: number) => {
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const handlePress = (entry: HistoryEntry) => {
    if (entry.status === 'cr_ready' || entry.status === 'sent') {
      router.push({
        pathname: '/preview',
        params: { file: `${CR_DIR}${entry.cr_filename}` },
      });
    } else if (entry.status === 'recorded') {
      // Navigate to recorder with this file to generate CR
      router.push({
        pathname: '/',
        params: { generateFile: entry.filename, generateId: entry.id },
      });
    }
  };

  const handleDelete = (entry: HistoryEntry) => {
    Alert.alert('Supprimer', `Supprimer ${entry.filename} ?`, [
      { text: 'Annuler', style: 'cancel' },
      {
        text: 'Supprimer',
        style: 'destructive',
        onPress: async () => {
          await sm.deleteEntry(entry.id);
          // Delete files
          try {
            await FileSystem.deleteAsync(`${RECORDINGS_DIR}${entry.filename}`, { idempotent: true });
            if (entry.cr_filename) {
              await FileSystem.deleteAsync(`${CR_DIR}${entry.cr_filename}`, { idempotent: true });
            }
          } catch { /* ignore */ }
          setEntries((prev) => prev.filter((e) => e.id !== entry.id));
        },
      },
    ]);
  };

  return (
    <SafeAreaView style={styles.screen}>
      <View style={styles.header}>
        <Text style={sharedStyles.heading}>Historique</Text>
        {totalSize > 0 && (
          <Text style={sharedStyles.textMuted}>{formatSize(totalSize)}</Text>
        )}
      </View>
      {entries.length === 0 ? (
        <View style={styles.empty}>
          <Text style={sharedStyles.textMuted}>Aucun enregistrement</Text>
        </View>
      ) : (
        <FlatList
          data={entries}
          keyExtractor={(e) => e.id}
          renderItem={({ item }) => (
            <HistoryItem
              entry={item}
              onPress={() => handlePress(item)}
              onDelete={() => handleDelete(item)}
            />
          )}
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.bg },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 20, paddingBottom: 8 },
  empty: { flex: 1, alignItems: 'center', justifyContent: 'center' },
});
