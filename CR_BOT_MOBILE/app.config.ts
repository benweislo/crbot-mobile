import { ExpoConfig, ConfigContext } from 'expo/config';

export default ({ config }: ConfigContext): ExpoConfig => ({
  ...config,
  name: config.name ?? 'CR_BOT',
  slug: config.slug ?? 'crbot-mobile',
  extra: {
    ...config.extra,
    LICENSE_KEY: process.env.CRBOT_LICENSE_KEY ?? '',
    GOOGLE_CLIENT_ID: process.env.GOOGLE_CLIENT_ID ?? '',
    PROXY_URL: process.env.CRBOT_PROXY_URL ?? '',
  },
});
