import { StorageManager, type HistoryEntry } from '../src/services/storage';

// Mock expo-file-system
jest.mock('expo-file-system', () => {
  let files: Record<string, string> = {};
  return {
    documentDirectory: 'file:///mock/',
    getInfoAsync: jest.fn(async (path: string) => ({
      exists: path in files,
      size: files[path]?.length ?? 0,
    })),
    readAsStringAsync: jest.fn(async (path: string) => {
      if (!(path in files)) throw new Error('File not found');
      return files[path];
    }),
    writeAsStringAsync: jest.fn(async (path: string, content: string) => {
      files[path] = content;
    }),
    deleteAsync: jest.fn(async (path: string) => {
      delete files[path];
    }),
    makeDirectoryAsync: jest.fn(),
    __reset: () => { files = {}; },
    __getFiles: () => files,
  };
});

const FileSystem = require('expo-file-system');

beforeEach(() => {
  FileSystem.__reset();
});

describe('StorageManager', () => {
  const historyPath = 'file:///mock/history.json';

  test('getHistory returns empty array when no history file', async () => {
    const sm = new StorageManager(historyPath);
    const entries = await sm.getHistory();
    expect(entries).toEqual([]);
  });

  test('addEntry creates entry and persists', async () => {
    const sm = new StorageManager(historyPath);
    const entry: HistoryEntry = {
      id: 'test-uuid-1',
      filename: '2026_03_24_14h30_meeting.m4a',
      date: '2026-03-24T14:30:00',
      duration_seconds: 3600,
      size_bytes: 7200000,
      status: 'recorded',
    };
    await sm.addEntry(entry);
    const entries = await sm.getHistory();
    expect(entries).toHaveLength(1);
    expect(entries[0].id).toBe('test-uuid-1');
    expect(entries[0].status).toBe('recorded');
  });

  test('updateEntry changes status and preserves other fields', async () => {
    const sm = new StorageManager(historyPath);
    await sm.addEntry({
      id: 'test-uuid-2',
      filename: 'meeting.m4a',
      date: '2026-03-24T10:00:00',
      duration_seconds: 1800,
      size_bytes: 3600000,
      status: 'recorded',
    });
    await sm.updateEntry('test-uuid-2', {
      status: 'cr_ready',
      cr_filename: '2026_03_24_10h00_CR.html',
    });
    const entries = await sm.getHistory();
    expect(entries[0].status).toBe('cr_ready');
    expect(entries[0].cr_filename).toBe('2026_03_24_10h00_CR.html');
    expect(entries[0].filename).toBe('meeting.m4a');
  });

  test('deleteEntry removes entry', async () => {
    const sm = new StorageManager(historyPath);
    await sm.addEntry({
      id: 'del-1',
      filename: 'a.m4a',
      date: '2026-01-01T00:00:00',
      duration_seconds: 60,
      size_bytes: 100,
      status: 'recorded',
    });
    await sm.addEntry({
      id: 'del-2',
      filename: 'b.m4a',
      date: '2026-01-01T00:00:00',
      duration_seconds: 60,
      size_bytes: 100,
      status: 'recorded',
    });
    await sm.deleteEntry('del-1');
    const entries = await sm.getHistory();
    expect(entries).toHaveLength(1);
    expect(entries[0].id).toBe('del-2');
  });

  test('status transitions: recorded → processing → cr_ready → sent', async () => {
    const sm = new StorageManager(historyPath);
    await sm.addEntry({
      id: 'transition-1',
      filename: 'meeting.m4a',
      date: '2026-03-24T14:00:00',
      duration_seconds: 600,
      size_bytes: 1000,
      status: 'recorded',
    });
    await sm.updateEntry('transition-1', { status: 'processing' });
    let entries = await sm.getHistory();
    expect(entries[0].status).toBe('processing');

    await sm.updateEntry('transition-1', { status: 'cr_ready', cr_filename: 'CR.html' });
    entries = await sm.getHistory();
    expect(entries[0].status).toBe('cr_ready');

    await sm.updateEntry('transition-1', { status: 'sent', sent_to: 'a@b.com' });
    entries = await sm.getHistory();
    expect(entries[0].status).toBe('sent');
    expect(entries[0].sent_to).toBe('a@b.com');
  });
});
