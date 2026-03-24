import type { TranscribeResponse, SummarizeResponse } from '../types';

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number = 0,
    public retryAfter?: number,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export class ApiClient {
  constructor(
    private proxyUrl: string,
    private licenseKey: string,
  ) {}

  async transcribe(
    fileUri: string,
    filename: string,
    language: string,
  ): Promise<TranscribeResponse> {
    const formData = new FormData();
    formData.append('license_key', this.licenseKey);
    formData.append('language', language);
    formData.append('audio', {
      uri: fileUri,
      name: filename,
      type: 'audio/mp4',
    } as any);

    return this.request<TranscribeResponse>('/transcribe', {
      method: 'POST',
      body: formData,
      timeout: 600000, // 10 min
    });
  }

  async summarize(
    transcript: string,
    language: string,
    context: string,
  ): Promise<SummarizeResponse> {
    return this.request<SummarizeResponse>('/summarize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        license_key: this.licenseKey,
        transcript,
        language,
        context,
      }),
      timeout: 120000, // 2 min
    });
  }

  private async request<T>(
    path: string,
    init: RequestInit & { timeout?: number },
  ): Promise<T> {
    const { timeout, ...fetchInit } = init;
    const controller = new AbortController();
    const timer = timeout
      ? setTimeout(() => controller.abort(), timeout)
      : undefined;

    try {
      const response = await fetch(`${this.proxyUrl}${path}`, {
        ...fetchInit,
        signal: controller.signal,
      });

      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        const msg = (body as any).detail ?? `HTTP ${response.status}`;
        throw new ApiError(msg, response.status);
      }

      return (await response.json()) as T;
    } catch (err) {
      if (err instanceof ApiError) throw err;
      throw new ApiError(
        err instanceof Error ? err.message : 'Network error',
        0,
      );
    } finally {
      if (timer) clearTimeout(timer);
    }
  }
}
