import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, StyleSheet, Pressable, ScrollView, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { GlassCard } from '../components/GlassCard';
import { GmailService } from '../services/gmailService';
import * as FileSystem from 'expo-file-system';
import { loadSettings, saveSettings, HISTORY_FILE, RECORDINGS_DIR, CR_DIR } from '../services/config';
import { StorageManager } from '../services/storage';
import { colors } from '../theme/colors';
import { sharedStyles } from '../theme/styles';
import type { AppSettings } from '../types';

const gmail = new GmailService();

export default function SettingsScreen() {
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const [gmailEmail, setGmailEmail] = useState<string | undefined>();
  const [storageSize, setStorageSize] = useState(0);
  // Local draft values for text inputs (saved onBlur, not every keystroke)
  const [draftEmail, setDraftEmail] = useState('');
  const [draftProxyUrl, setDraftProxyUrl] = useState('');

  useEffect(() => {
    loadSettings().then((s) => {
      setSettings(s);
      setDraftEmail(s.recipient_email);
      setDraftProxyUrl(s.proxy_url);
    });
    gmail.loadTokens().then(() => setGmailEmail(gmail.getEmail()));
    new StorageManager(HISTORY_FILE).getTotalSize().then(setStorageSize);
  }, []);

  const handleSave = async (updates: Partial<AppSettings>) => {
    if (!settings) return;
    const newSettings = { ...settings, ...updates };
    setSettings(newSettings);
    await saveSettings(newSettings);
  };

  const handleGmailConnect = async () => {
    const ok = await gmail.signIn();
    if (ok) setGmailEmail(gmail.getEmail());
    else Alert.alert('Erreur', 'Connexion Gmail échouée');
  };

  const handleGmailDisconnect = async () => {
    await gmail.signOut();
    setGmailEmail(undefined);
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  if (!settings) return null;

  return (
    <SafeAreaView style={styles.screen}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text style={[sharedStyles.heading, styles.title]}>Réglages</Text>

        <GlassCard style={styles.card}>
          <Text style={styles.label}>Email destinataire</Text>
          <TextInput
            style={styles.input}
            value={draftEmail}
            onChangeText={setDraftEmail}
            onBlur={() => handleSave({ recipient_email: draftEmail })}
            placeholder="collegue@email.com"
            placeholderTextColor={colors.textMuted}
            keyboardType="email-address"
            autoCapitalize="none"
          />
        </GlassCard>

        <GlassCard style={styles.card}>
          <Text style={styles.label}>Compte Gmail</Text>
          {gmailEmail ? (
            <View style={styles.row}>
              <Text style={sharedStyles.text}>{gmailEmail}</Text>
              <Pressable onPress={handleGmailDisconnect}>
                <Text style={styles.link}>Déconnecter</Text>
              </Pressable>
            </View>
          ) : (
            <Pressable onPress={handleGmailConnect}>
              <Text style={styles.link}>Se connecter avec Google</Text>
            </Pressable>
          )}
        </GlassCard>

        <GlassCard style={styles.card}>
          <Text style={styles.label}>Langue du CR</Text>
          <View style={styles.row}>
            {(['fr', 'en'] as const).map((lang) => (
              <Pressable
                key={lang}
                style={[
                  styles.chip,
                  settings.language === lang && styles.chipActive,
                ]}
                onPress={() => handleSave({ language: lang })}
              >
                <Text
                  style={[
                    styles.chipText,
                    settings.language === lang && styles.chipTextActive,
                  ]}
                >
                  {lang === 'fr' ? 'Français' : 'English'}
                </Text>
              </Pressable>
            ))}
          </View>
        </GlassCard>

        <GlassCard style={styles.card}>
          <Text style={styles.label}>Qualité audio</Text>
          <View style={styles.row}>
            {(['low', 'medium', 'high'] as const).map((q) => (
              <Pressable
                key={q}
                style={[
                  styles.chip,
                  settings.audio_quality === q && styles.chipActive,
                ]}
                onPress={() => handleSave({ audio_quality: q })}
              >
                <Text
                  style={[
                    styles.chipText,
                    settings.audio_quality === q && styles.chipTextActive,
                  ]}
                >
                  {q === 'low' ? '64 kbps' : q === 'medium' ? '96 kbps' : '128 kbps'}
                </Text>
              </Pressable>
            ))}
          </View>
        </GlassCard>

        <GlassCard style={styles.card}>
          <Text style={styles.label}>Stockage</Text>
          <View style={styles.row}>
            <Text style={sharedStyles.textMuted}>{formatSize(storageSize)} utilisés</Text>
            <Pressable onPress={() => {
              Alert.alert('Nettoyer', 'Supprimer tous les enregistrements et CRs ?', [
                { text: 'Annuler', style: 'cancel' },
                {
                  text: 'Nettoyer',
                  style: 'destructive',
                  onPress: async () => {
                    const entries = await new StorageManager(HISTORY_FILE).getHistory();
                    for (const e of entries) {
                      try { await FileSystem.deleteAsync(`${RECORDINGS_DIR}${e.filename}`, { idempotent: true }); } catch {}
                      if (e.cr_filename) try { await FileSystem.deleteAsync(`${CR_DIR}${e.cr_filename}`, { idempotent: true }); } catch {}
                    }
                    await FileSystem.writeAsStringAsync(HISTORY_FILE, '[]');
                    setStorageSize(0);
                  },
                },
              ]);
            }}>
              <Text style={styles.link}>Nettoyer</Text>
            </Pressable>
          </View>
        </GlassCard>

        <GlassCard style={styles.card}>
          <Text style={styles.label}>Proxy URL (avancé)</Text>
          <TextInput
            style={styles.input}
            value={draftProxyUrl}
            onChangeText={setDraftProxyUrl}
            onBlur={() => handleSave({ proxy_url: draftProxyUrl })}
            placeholder="https://crbot-proxy.example.com"
            placeholderTextColor={colors.textMuted}
            autoCapitalize="none"
          />
        </GlassCard>

        <GlassCard style={styles.card}>
          <Text style={styles.label}>À propos</Text>
          <Text style={sharedStyles.text}>CR_BOT Mobile v0.1.0 (beta)</Text>
          <Text style={[sharedStyles.textMuted, { marginTop: 4 }]}>Par WSLO.lab — IA pour écoles d'animation 3D</Text>
        </GlassCard>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.bg },
  scroll: { padding: 20 },
  title: { marginBottom: 20 },
  card: { marginBottom: 16 },
  label: { color: colors.textMuted, fontSize: 13, fontWeight: '600', marginBottom: 8, textTransform: 'uppercase', letterSpacing: 0.5 },
  input: { color: colors.text, fontSize: 16, borderBottomWidth: 1, borderBottomColor: colors.surfaceBorder, paddingVertical: 8 },
  row: { flexDirection: 'row', alignItems: 'center', gap: 12, flexWrap: 'wrap' },
  link: { color: colors.primary, fontSize: 16, fontWeight: '600' },
  chip: { paddingHorizontal: 16, paddingVertical: 8, borderRadius: 20, borderWidth: 1, borderColor: colors.surfaceBorder },
  chipActive: { borderColor: colors.primary, backgroundColor: 'rgba(110,62,168,0.15)' },
  chipText: { color: colors.textMuted, fontSize: 14 },
  chipTextActive: { color: colors.primary, fontWeight: '600' },
});
