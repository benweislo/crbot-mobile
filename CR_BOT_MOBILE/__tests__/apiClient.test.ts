import { ApiClient, ApiError } from '../src/services/apiClient';

// Mock global fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

beforeEach(() => {
  mockFetch.mockReset();
});

const client = new ApiClient('https://proxy.test', 'CRBOT-TEST-KEY');

describe('ApiClient', () => {
  test('transcribe sends multipart and returns response', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        full_text: '[Speaker 1] Bonjour',
        segments: [],
        duration_seconds: 60,
      }),
    });

    const result = await client.transcribe('file:///audio.m4a', 'audio.m4a', 'fr');
    expect(result.full_text).toContain('Bonjour');
    expect(mockFetch).toHaveBeenCalledTimes(1);
    const [url] = mockFetch.mock.calls[0];
    expect(url).toBe('https://proxy.test/transcribe');
  });

  test('summarize sends JSON and returns summary', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ summary: 'COMPTE RENDU DE RÉUNION...' }),
    });

    const result = await client.summarize('transcript text', 'fr', '');
    expect(result.summary).toContain('COMPTE RENDU');
  });

  test('throws ApiError on network timeout', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network request failed'));

    await expect(client.summarize('text', 'fr', '')).rejects.toThrow(ApiError);
  });

  test('throws ApiError with retry info on 429', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 429,
      json: async () => ({ detail: 'Rate limit exceeded' }),
    });

    try {
      await client.summarize('text', 'fr', '');
      fail('Should have thrown');
    } catch (e) {
      expect(e).toBeInstanceOf(ApiError);
      expect((e as ApiError).status).toBe(429);
    }
  });

  test('throws ApiError with message on 500', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({ detail: 'Internal server error' }),
    });

    try {
      await client.summarize('text', 'fr', '');
      fail('Should have thrown');
    } catch (e) {
      expect(e).toBeInstanceOf(ApiError);
      expect((e as ApiError).status).toBe(500);
    }
  });
});
