import { StyleSheet } from 'react-native';
import { colors } from './colors';

export const sharedStyles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: colors.bg,
  },
  screenPadded: {
    flex: 1,
    backgroundColor: colors.bg,
    paddingHorizontal: 20,
  },
  text: {
    color: colors.text,
    fontSize: 16,
  },
  textMuted: {
    color: colors.textMuted,
    fontSize: 14,
  },
  heading: {
    color: colors.text,
    fontSize: 22,
    fontWeight: '700',
  },
  timerText: {
    color: colors.text,
    fontSize: 40,
    fontFamily: 'monospace',
    fontVariant: ['tabular-nums'],
  },
});
