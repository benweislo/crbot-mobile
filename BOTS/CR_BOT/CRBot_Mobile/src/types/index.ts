export type RecordingStatus = 'idle' | 'recording' | 'paused' | 'stopped';

export type HistoryEntryStatus = 'recorded' | 'processing' | 'cr_ready' | 'sent';

export interface HistoryEntry {
  id: string;
  filename: string;
  date: string; // ISO 8601
  duration_seconds: number;
  size_bytes: number;
  status: HistoryEntryStatus;
  cr_filename?: string;
  transcript_text?: string;
  summary_text?: string;
  sent_to?: string;
  sent_at?: string;
}

export interface TranscribeResponse {
  segments: Array<{
    start: number;
    end: number;
    speaker: string;
    text: string;
  }>;
  full_text: string;
  duration_seconds: number;
}

export interface SummarizeResponse {
  summary: string;
}

export interface ParsedCR {
  date: string;
  duree: string;
  themes: string[];
  actions: string; // Raw actions text (per-person blocks)
  conclusion: string;
  details: string; // Raw detail sections
}

export interface BrandProfile {
  company_name: string;
  primary_color: string;
  secondary_color: string;
  background_color: string;
  text_color: string;
  font_family: string;
  footer_text: string;
  logo_b64: string;
}

export interface AppSettings {
  recipient_email: string;
  language: 'fr' | 'en';
  audio_quality: 'low' | 'medium' | 'high';
  proxy_url: string;
  license_key: string;
}
