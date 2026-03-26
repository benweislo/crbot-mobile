import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';
import { Linking, Platform } from 'react-native';
import { RECORDINGS_DIR, AUDIO_QUALITY_MAP } from './config';
import { startBackgroundTask, stopBackgroundTask } from './backgroundTask';
import type { RecordingStatus } from '../types';

export class MicPermissionError extends Error {
  constructor() {
    super('Microphone permission denied');
    this.name = 'MicPermissionError';
  }
}

export class RecorderService {
  private recording: Audio.Recording | null = null;
  private startTime: number = 0;
  private pausedDuration: number = 0;
  private pauseStart: number = 0;

  async start(quality: keyof typeof AUDIO_QUALITY_MAP = 'medium'): Promise<void> {
    const { granted, canAskAgain } = await Audio.requestPermissionsAsync();
    if (!granted) {
      if (!canAskAgain) {
        // Permanently denied — user must go to OS settings
        throw new MicPermissionError();
      }
      throw new MicPermissionError();
    }

    await Audio.setAudioModeAsync({
      allowsRecordingIOS: true,
      playsInSilentModeIOS: true,
      staysActiveInBackground: true,
    });

    const bitRate = AUDIO_QUALITY_MAP[quality];
    this.recording = new Audio.Recording();
    await this.recording.prepareToRecordAsync({
      isMeteringEnabled: true,
      android: {
        extension: '.m4a',
        outputFormat: Audio.AndroidOutputFormat.MPEG_4,
        audioEncoder: Audio.AndroidAudioEncoder.AAC,
        sampleRate: 22050,
        numberOfChannels: 1,
        bitRate,
      },
      ios: {
        extension: '.m4a',
        outputFormat: Audio.IOSOutputFormat.MPEG4AAC,
        audioQuality: Audio.IOSAudioQuality.MEDIUM,
        sampleRate: 22050,
        numberOfChannels: 1,
        bitRate,
      },
      web: {},
    });
    await this.recording.startAsync();
    await startBackgroundTask();
    this.startTime = Date.now();
    this.pausedDuration = 0;
  }

  /** Open OS settings for microphone permission. */
  static async openMicSettings(): Promise<void> {
    if (Platform.OS === 'ios') {
      await Linking.openURL('app-settings:');
    } else {
      await Linking.openSettings();
    }
  }

  async pause(): Promise<void> {
    if (!this.recording) return;
    await this.recording.pauseAsync();
    this.pauseStart = Date.now();
  }

  async resume(): Promise<void> {
    if (!this.recording) return;
    this.pausedDuration += Date.now() - this.pauseStart;
    await this.recording.startAsync();
  }

  async stop(): Promise<{ uri: string; filename: string; durationSeconds: number }> {
    if (!this.recording) throw new Error('No active recording');

    await this.recording.stopAndUnloadAsync();
    await stopBackgroundTask();
    await Audio.setAudioModeAsync({ allowsRecordingIOS: false });

    const uri = this.recording.getURI();
    if (!uri) throw new Error('No recording URI');

    const durationSeconds = Math.round(
      (Date.now() - this.startTime - this.pausedDuration) / 1000,
    );

    // Generate filename
    const now = new Date();
    const pad = (n: number) => String(n).padStart(2, '0');
    const filename = `${now.getFullYear()}_${pad(now.getMonth() + 1)}_${pad(now.getDate())}_${pad(now.getHours())}h${pad(now.getMinutes())}_meeting.m4a`;

    // Move to recordings directory
    await FileSystem.getInfoAsync(RECORDINGS_DIR).then(async (info) => {
      if (!info.exists) await FileSystem.makeDirectoryAsync(RECORDINGS_DIR, { intermediates: true });
    });
    const destUri = `${RECORDINGS_DIR}${filename}`;
    await FileSystem.moveAsync({ from: uri, to: destUri });

    this.recording = null;

    return { uri: destUri, filename, durationSeconds };
  }

  async getStatus(): Promise<Audio.RecordingStatus | null> {
    if (!this.recording) return null;
    return this.recording.getStatusAsync();
  }

  getElapsedSeconds(): number {
    if (!this.startTime) return 0;
    return Math.round((Date.now() - this.startTime - this.pausedDuration) / 1000);
  }
}
