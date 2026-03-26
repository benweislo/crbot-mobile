import * as AuthSession from 'expo-auth-session';
import * as WebBrowser from 'expo-web-browser';
import * as SecureStore from 'expo-secure-store';
import * as FileSystem from 'expo-file-system';
import Constants from 'expo-constants';

WebBrowser.maybeCompleteAuthSession();

const GMAIL_TOKEN_KEY = 'gmail_tokens';
const GOOGLE_CLIENT_ID: string =
  (Constants.expoConfig?.extra?.GOOGLE_CLIENT_ID as string) ?? '';

// Discovery document for Google OAuth2
const discovery = {
  authorizationEndpoint: 'https://accounts.google.com/o/oauth2/v2/auth',
  tokenEndpoint: 'https://oauth2.googleapis.com/token',
  revocationEndpoint: 'https://oauth2.googleapis.com/revoke',
};

interface GmailTokens {
  access_token: string;
  refresh_token?: string;
  expires_at: number;
  email?: string;
}

export class GmailService {
  private tokens: GmailTokens | null = null;

  async loadTokens(): Promise<GmailTokens | null> {
    try {
      const raw = await SecureStore.getItemAsync(GMAIL_TOKEN_KEY);
      if (raw) {
        this.tokens = JSON.parse(raw);
        return this.tokens;
      }
    } catch { /* no stored tokens */ }
    return null;
  }

  isAuthenticated(): boolean {
    return this.tokens !== null && this.tokens.expires_at > Date.now();
  }

  getEmail(): string | undefined {
    return this.tokens?.email;
  }

  async signIn(): Promise<boolean> {
    const redirectUri = AuthSession.makeRedirectUri({ scheme: 'crbot' });

    const request = new AuthSession.AuthRequest({
      clientId: GOOGLE_CLIENT_ID,
      scopes: [
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/userinfo.email',
      ],
      redirectUri,
      responseType: AuthSession.ResponseType.Code,
      usePKCE: true,
    });

    const result = await request.promptAsync(discovery);

    if (result.type !== 'success' || !result.params.code) return false;

    // Exchange code for tokens
    const tokenResponse = await AuthSession.exchangeCodeAsync(
      {
        clientId: GOOGLE_CLIENT_ID,
        code: result.params.code,
        redirectUri,
        extraParams: { code_verifier: request.codeVerifier! },
      },
      discovery,
    );

    // Get user email
    const userInfo = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
      headers: { Authorization: `Bearer ${tokenResponse.accessToken}` },
    }).then((r) => r.json());

    this.tokens = {
      access_token: tokenResponse.accessToken,
      refresh_token: tokenResponse.refreshToken,
      expires_at: Date.now() + (tokenResponse.expiresIn ?? 3600) * 1000,
      email: userInfo.email,
    };

    await SecureStore.setItemAsync(GMAIL_TOKEN_KEY, JSON.stringify(this.tokens));
    return true;
  }

  async signOut(): Promise<void> {
    this.tokens = null;
    await SecureStore.deleteItemAsync(GMAIL_TOKEN_KEY);
  }

  async sendCR(
    recipientEmail: string,
    date: string,
    htmlFilePath: string,
  ): Promise<void> {
    if (!this.tokens) throw new Error('Not authenticated');

    // Refresh if expired
    if (this.tokens.expires_at < Date.now() && this.tokens.refresh_token) {
      await this.refreshToken();
    }

    const htmlContent = await FileSystem.readAsStringAsync(htmlFilePath);
    const htmlBase64 = btoa(unescape(encodeURIComponent(htmlContent)));
    const filename = htmlFilePath.split('/').pop() ?? 'CR.html';

    // Build MIME message
    const boundary = `boundary_${Date.now()}`;
    const subject = `Compte Rendu — ${date}`;
    const mimeMessage = [
      `To: ${recipientEmail}`,
      `Subject: =?UTF-8?B?${btoa(unescape(encodeURIComponent(subject)))}?=`,
      'MIME-Version: 1.0',
      `Content-Type: multipart/mixed; boundary="${boundary}"`,
      '',
      `--${boundary}`,
      'Content-Type: text/plain; charset=UTF-8',
      '',
      `Veuillez trouver ci-joint le compte rendu de la réunion du ${date}.`,
      '',
      `--${boundary}`,
      `Content-Type: text/html; name="${filename}"`,
      'Content-Transfer-Encoding: base64',
      `Content-Disposition: attachment; filename="${filename}"`,
      '',
      htmlBase64,
      `--${boundary}--`,
    ].join('\r\n');

    const raw = btoa(unescape(encodeURIComponent(mimeMessage)))
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/, '');

    const response = await fetch(
      'https://gmail.googleapis.com/gmail/v1/users/me/messages/send',
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${this.tokens.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ raw }),
      },
    );

    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(`Gmail send failed: ${(body as any).error?.message ?? response.status}`);
    }
  }

  private async refreshToken(): Promise<void> {
    if (!this.tokens?.refresh_token) throw new Error('No refresh token');

    const response = await AuthSession.refreshAsync(
      { clientId: GOOGLE_CLIENT_ID, refreshToken: this.tokens.refresh_token },
      discovery,
    );

    this.tokens = {
      ...this.tokens,
      access_token: response.accessToken,
      expires_at: Date.now() + (response.expiresIn ?? 3600) * 1000,
    };

    await SecureStore.setItemAsync(GMAIL_TOKEN_KEY, JSON.stringify(this.tokens));
  }
}
