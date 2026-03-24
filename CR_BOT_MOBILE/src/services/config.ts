import * as SecureStore from 'expo-secure-store';
import * as FileSystem from 'expo-file-system';
import type { AppSettings, BrandProfile } from '../types';

export const PROXY_URL = 'https://crbot-proxy.example.com';
export const LICENSE_KEY = 'CRBOT-BETA-0001-WSLO';

export const RECORDINGS_DIR = `${FileSystem.documentDirectory}recordings/`;
export const CR_DIR = `${FileSystem.documentDirectory}cr/`;
export const HISTORY_FILE = `${FileSystem.documentDirectory}history.json`;

export const AUDIO_QUALITY_MAP = {
  low: 64000,
  medium: 96000,
  high: 128000,
} as const;

export const DEFAULT_SETTINGS: AppSettings = {
  recipient_email: '',
  language: 'fr',
  audio_quality: 'medium',
  proxy_url: PROXY_URL,
  license_key: LICENSE_KEY,
};

export const BRAND: BrandProfile = {
  company_name: 'CR_BOT',
  primary_color: '#6e3ea8',
  secondary_color: '#E93F7F',
  background_color: '#050505',
  text_color: '#E5E5E5',
  font_family: 'system-ui, -apple-system, sans-serif',
  footer_text: 'Compte rendu généré par CR_BOT',
  logo_b64: '', // Loaded at runtime from assets
};

const SETTINGS_KEY = 'crbot_settings';

export async function loadSettings(): Promise<AppSettings> {
  try {
    const raw = await SecureStore.getItemAsync(SETTINGS_KEY);
    if (raw) return { ...DEFAULT_SETTINGS, ...JSON.parse(raw) };
  } catch {
    // Fall through to defaults
  }
  return { ...DEFAULT_SETTINGS };
}

export async function saveSettings(settings: AppSettings): Promise<void> {
  await SecureStore.setItemAsync(SETTINGS_KEY, JSON.stringify(settings));
}

export async function ensureDirectories(): Promise<void> {
  const dirs = [RECORDINGS_DIR, CR_DIR];
  for (const dir of dirs) {
    const info = await FileSystem.getInfoAsync(dir);
    if (!info.exists) {
      await FileSystem.makeDirectoryAsync(dir, { intermediates: true });
    }
  }
}
