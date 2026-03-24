import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Pressable, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { WebView } from 'react-native-webview';
import { useLocalSearchParams } from 'expo-router';
import * as FileSystem from 'expo-file-system';
import { LinearGradient } from 'expo-linear-gradient';
import { GmailService } from '../services/gmailService';
import { loadSettings, HISTORY_FILE } from '../services/config';
import { StorageManager } from '../services/storage';
import { colors } from '../theme/colors';

const gmail = new GmailService();

export default function PreviewScreen() {
  const { file } = useLocalSearchParams<{ file: string }>();
  const [html, setHtml] = useState('');
  const [sending, setSending] = useState(false);

  useEffect(() => {
    if (file) {
      FileSystem.readAsStringAsync(file).then(setHtml).catch(() => {});
    }
  }, [file]);

  const handleSend = async () => {
    if (!file) return;
    setSending(true);
    try {
      await gmail.loadTokens();
      if (!gmail.isAuthenticated()) {
        const ok = await gmail.signIn();
        if (!ok) {
          Alert.alert('Erreur', 'Connexion Gmail échouée');
          return;
        }
      }
      const settings = await loadSettings();
      if (!settings.recipient_email) {
        Alert.alert('Erreur', 'Configurez l\'email destinataire dans Réglages');
        return;
      }

      // Extract date from filename
      const filename = file.split('/').pop() ?? '';
      const dateMatch = filename.match(/(\d{4}_\d{2}_\d{2})/);
      const date = dateMatch?.[1]?.replace(/_/g, '/') ?? new Date().toLocaleDateString('fr-FR');

      await gmail.sendCR(settings.recipient_email, date, file);

      // Update history entry
      const sm = new StorageManager(HISTORY_FILE);
      const entries = await sm.getHistory();
      const entry = entries.find((e) => e.cr_filename && file.includes(e.cr_filename));
      if (entry) {
        await sm.updateEntry(entry.id, {
          status: 'sent',
          sent_to: settings.recipient_email,
          sent_at: new Date().toISOString(),
        });
      }

      Alert.alert('Envoyé', `CR envoyé à ${settings.recipient_email}`);
    } catch (err: any) {
      Alert.alert('Erreur', err.message);
    } finally {
      setSending(false);
    }
  };

  if (!html) {
    return (
      <SafeAreaView style={styles.screen}>
        <Text style={styles.placeholder}>Aucun CR à afficher</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.screen}>
      <WebView
        source={{ html }}
        style={styles.webview}
        originWhitelist={['*']}
        scalesPageToFit
      />
      <View style={styles.bottomBar}>
        <Pressable onPress={handleSend} disabled={sending}>
          <LinearGradient
            colors={[colors.gradientStart, colors.gradientEnd]}
            style={styles.sendButton}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
          >
            <Text style={styles.sendText}>
              {sending ? 'Envoi en cours...' : 'Envoyer par email'}
            </Text>
          </LinearGradient>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.bg },
  webview: { flex: 1 },
  placeholder: { color: colors.textMuted, textAlign: 'center', marginTop: 100 },
  bottomBar: { padding: 16, backgroundColor: colors.bg, borderTopWidth: 1, borderTopColor: colors.surfaceBorder },
  sendButton: { paddingVertical: 14, borderRadius: 12, alignItems: 'center' },
  sendText: { color: '#fff', fontWeight: '700', fontSize: 16 },
});
