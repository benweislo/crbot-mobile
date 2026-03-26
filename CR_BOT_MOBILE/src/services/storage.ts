import * as FileSystem from 'expo-file-system';
import type { HistoryEntry } from '../types';

export type { HistoryEntry };

/**
 * Simple async mutex — serializes calls to prevent concurrent read-modify-write.
 */
class Mutex {
  private queue: (() => void)[] = [];
  private locked = false;

  async acquire(): Promise<() => void> {
    if (!this.locked) {
      this.locked = true;
      return () => this.release();
    }
    return new Promise<() => void>((resolve) => {
      this.queue.push(() => resolve(() => this.release()));
    });
  }

  private release(): void {
    const next = this.queue.shift();
    if (next) {
      next();
    } else {
      this.locked = false;
    }
  }
}

export class StorageManager {
  private mutex = new Mutex();

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
    const unlock = await this.mutex.acquire();
    try {
      const entries = await this.getHistory();
      entries.unshift(entry);
      await this.save(entries);
    } finally {
      unlock();
    }
  }

  async updateEntry(id: string, updates: Partial<HistoryEntry>): Promise<void> {
    const unlock = await this.mutex.acquire();
    try {
      const entries = await this.getHistory();
      const idx = entries.findIndex((e) => e.id === id);
      if (idx === -1) return;
      entries[idx] = { ...entries[idx], ...updates };
      await this.save(entries);
    } finally {
      unlock();
    }
  }

  async deleteEntry(id: string): Promise<void> {
    const unlock = await this.mutex.acquire();
    try {
      const entries = await this.getHistory();
      await this.save(entries.filter((e) => e.id !== id));
    } finally {
      unlock();
    }
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
