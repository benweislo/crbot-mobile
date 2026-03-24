import React from 'react';
import { Text } from 'react-native';
import { sharedStyles } from '../theme/styles';

interface TimerProps {
  seconds: number;
}

export function Timer({ seconds }: TimerProps) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  const pad = (n: number) => String(n).padStart(2, '0');
  const display = h > 0 ? `${pad(h)}:${pad(m)}:${pad(s)}` : `${pad(m)}:${pad(s)}`;

  return <Text style={sharedStyles.timerText}>{display}</Text>;
}
