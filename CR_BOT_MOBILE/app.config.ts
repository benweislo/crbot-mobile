import { ExpoConfig, ConfigContext } from 'expo/config';

export default ({ config }: ConfigContext): ExpoConfig => ({
  ...config,
  name: config.name ?? 'CR_BOT',
  slug: config.slug ?? 'crbot-mobile',
  extra: {
    ...config.extra,
    LICENSE_KEY: process.env.CRBOT_LICENSE_KEY ?? '',
  },
});
