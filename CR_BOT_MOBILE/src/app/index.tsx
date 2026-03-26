import React, { useState, useEffect, useRef, useCallback } from 'react';
import { View, Text, StyleSheet, Image, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { RecordButton } from '../components/RecordButton';
import { Timer } from '../components/Timer';
import { AudioLevel } from '../components/AudioLevel';
import { GlassCard } from '../components/GlassCard';
import * as Network from 'expo-network';
import { RecorderService, MicPermissionError } from '../services/recorder';
import { ApiClient, ApiError } from '../services/apiClient';
import { StorageManager } from '../services/storage';
import { generateHTML } from '../services/crEngine';
import { loadSettings, ensureDirectories, HISTORY_FILE, CR_DIR, BRAND } from '../services/config';
import { colors } from '../theme/colors';
import { sharedStyles } from '../theme/styles';
import type { RecordingStatus } from '../types';
import * as FileSystem from 'expo-file-system';
import 'react-native-get-random-values';
import { v4 as uuidv4 } from 'uuid';

const logo = require('../../assets/logo-wslo.png');
const recorder = new RecorderService();

export default function RecorderScreen() {
  const router = useRouter();
  const [status, setStatus] = useState<RecordingStatus>('idle');
  const [seconds, setSeconds] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  const [processing, setProcessing] = useState(false);
  const [lastRecording, setLastRecording] = useState<{
    uri: string;
    filename: string;
    durationSeconds: number;
  } | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    ensureDirectories();
  }, []);

  useEffect(() => {
    if (status === 'recording') {
      timerRef.current = setInterval(async () => {
        setSeconds(recorder.getElapsedSeconds());
        const recStatus = await recorder.getStatus();
        if (recStatus?.metering != null) {
          // metering is in dBFS (-160..0), normalize to 0..1
          const db = recStatus.metering;
          const normalized = Math.max(0, Math.min(1, (db + 60) / 60));
          setAudioLevel(normalized);
        }
      }, 250);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
      setAudioLevel(0);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [status]);

  const handlePress = useCallback(async () => {
    try {
      if (status === 'idle') {
        const settings = await loadSettings();
        await recorder.start(settings.audio_quality);
        setStatus('recording');
        setSeconds(0);
      } else if (status === 'recording') {
        // Stop
        const result = await recorder.stop();
        setStatus('stopped');
        setLastRecording(result);
        setSeconds(result.durationSeconds);

        // Add to history
        const sm = new StorageManager(HISTORY_FILE);
        const fileInfo = await FileSystem.getInfoAsync(result.uri);
        await sm.addEntry({
          id: uuidv4(),
          filename: result.filename,
          date: new Date().toISOString(),
          duration_seconds: result.durationSeconds,
          size_bytes: (fileInfo as any).size ?? 0,
          status: 'recorded',
        });
      } else if (status === 'paused') {
        await recorder.resume();
        setStatus('recording');
      }
    } catch (err: any) {
      if (err instanceof MicPermissionError) {
        Alert.alert(
          'Micro requis',
          'CR_BOT a besoin du micro pour enregistrer vos réunions.',
          [
            { text: 'Annuler', style: 'cancel' },
            { text: 'Ouvrir les paramètres', onPress: () => RecorderService.openMicSettings() },
          ],
        );
      } else {
        Alert.alert('Erreur', err.message);
      }
    }
  }, [status]);

  const handlePause = useCallback(async () => {
    if (status === 'recording') {
      await recorder.pause();
      setStatus('paused');
    }
  }, [status]);

  const handleGenerate = useCallback(async () => {
    if (!lastRecording) return;
    setProcessing(true);

    try {
      // WiFi check
      const networkState = await Network.getNetworkStateAsync();
      if (networkState.type === Network.NetworkStateType.CELLULAR) {
        const fileInfo = await FileSystem.getInfoAsync(lastRecording.uri);
        const sizeMB = ((fileInfo as any).size ?? 0) / (1024 * 1024);
        const proceed = await new Promise<boolean>((resolve) => {
          Alert.alert(
            'Données mobiles',
            `Vous êtes en données mobiles. Envoyer ${sizeMB.toFixed(1)} MB ?`,
            [
              { text: 'Attendre WiFi', style: 'cancel', onPress: () => resolve(false) },
              { text: 'Envoyer', onPress: () => resolve(true) },
            ],
          );
        });
        if (!proceed) { setProcessing(false); return; }
      }

      const settings = await loadSettings();
      const client = new ApiClient(settings.proxy_url, settings.license_key);
      const sm = new StorageManager(HISTORY_FILE);
      const entries = await sm.getHistory();
      const entry = entries.find((e) => e.filename === lastRecording.filename);
      if (!entry) return;

      await sm.updateEntry(entry.id, { status: 'processing' });

      // Stage 1: Transcribe (skip if already cached)
      const transcription = entry.transcript_text
        ? { full_text: entry.transcript_text, segments: [], duration_seconds: entry.duration_seconds }
        : await client.transcribe(
        lastRecording.uri,
        lastRecording.filename,
        settings.language,
      );

      // Stage 2: Summarize
      const summary = await client.summarize(
        transcription.full_text,
        settings.language,
        '',
      );

      // Stage 3: Generate HTML
      const html = generateHTML(summary.summary, BRAND);
      const baseName = lastRecording.filename.replace(/\.m4a$/, '').replace(/_meeting$/, '');
      const crFilename = `${baseName}_CR.html`;
      const crPath = `${CR_DIR}${crFilename}`;
      await FileSystem.writeAsStringAsync(crPath, html);

      await sm.updateEntry(entry.id, {
        status: 'cr_ready',
        cr_filename: crFilename,
        transcript_text: transcription.full_text,
        summary_text: summary.summary,
      });

      setStatus('idle');
      setLastRecording(null);
      setSeconds(0);

      // Navigate to preview
      router.push({ pathname: '/preview', params: { file: crPath } });
    } catch (err: any) {
      if (err instanceof ApiError && err.status === 429) {
        Alert.alert('Limite atteinte', 'Réessayez dans quelques minutes.', [
          { text: 'OK' },
          { text: 'Réessayer', onPress: () => handleGenerate() },
        ]);
      } else {
        Alert.alert('Erreur', err.message, [
          { text: 'OK' },
          { text: 'Réessayer', onPress: () => handleGenerate() },
        ]);
      }
    } finally {
      setProcessing(false);
    }
  }, [lastRecording, router]);

  return (
    <SafeAreaView style={styles.screen}>
      <View style={styles.content}>
        <Image source={logo} style={styles.logo} resizeMode="contain" />

        <View style={styles.center}>
          <Timer seconds={seconds} />
          <AudioLevel level={audioLevel} isActive={status === 'recording'} />

          <View style={styles.buttonRow}>
            {status === 'recording' && (
              <RecordButton status="paused" onPress={handlePause} />
            )}
            <RecordButton status={status} onPress={handlePress} />
          </View>

          <Text style={sharedStyles.textMuted}>
            {status === 'idle' && 'Appuyez pour enregistrer'}
            {status === 'recording' && 'Enregistrement en cours...'}
            {status === 'paused' && 'En pause'}
            {status === 'stopped' && `${lastRecording?.filename}`}
          </Text>
        </View>

        {status === 'stopped' && lastRecording && (
          <GlassCard style={styles.generateCard}>
            <Text
              style={[sharedStyles.text, styles.generateBtn]}
              onPress={handleGenerate}
            >
              {processing ? 'Génération en cours...' : 'Générer le CR'}
            </Text>
          </GlassCard>
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.bg },
  content: { flex: 1, alignItems: 'center', paddingTop: 40 },
  logo: { width: 120, height: 40, marginBottom: 40, opacity: 0.8 },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: 24 },
  buttonRow: { flexDirection: 'row', alignItems: 'center', gap: 20 },
  generateCard: { marginBottom: 40, marginHorizontal: 20, alignSelf: 'stretch' },
  generateBtn: { textAlign: 'center', fontWeight: '700', fontSize: 18, color: colors.primary },
});
