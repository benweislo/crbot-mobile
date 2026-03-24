import * as FileSystem from 'expo-file-system';
import type { HistoryEntry } from '../types';

export type { HistoryEntry };

export class StorageManager {
  constructor(private historyPath: string) {}

  async getHistory(): Promise<HistoryEntry[]> {
    try {
      const info = await FileSystem.getInfoAsync(this.historyPath);
      if (!info.exists) return [];
      const raw = await FileSystem.readAsStringAsync(this.historyPath);
      return JSON.parse(raw) as HistoryEntry[];
    } catch {
      return [];
    }
  }

  async addEntry(entry: HistoryEntry): Promise<void> {
    const entries = await this.getHistory();
    entries.unshift(entry); // Newest first
    await this.save(entries);
  }

  async updateEntry(id: string, updates: Partial<HistoryEntry>): Promise<void> {
    const entries = await this.getHistory();
    const idx = entries.findIndex((e) => e.id === id);
    if (idx === -1) return;
    entries[idx] = { ...entries[idx], ...updates };
    await this.save(entries);
  }

  async deleteEntry(id: string): Promise<void> {
    const entries = await this.getHistory();
    await this.save(entries.filter((e) => e.id !== id));
  }

  async getTotalSize(): Promise<number> {
    const entries = await this.getHistory();
    return entries.reduce((sum, e) => sum + (e.size_bytes ?? 0), 0);
  }

  private async save(entries: HistoryEntry[]): Promise<void> {
    await FileSystem.writeAsStringAsync(
      this.historyPath,
      JSON.stringify(entries, null, 2),
    );
  }
}
