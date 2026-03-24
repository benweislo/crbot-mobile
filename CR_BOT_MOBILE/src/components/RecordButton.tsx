import React from 'react';
import { Pressable, StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withRepeat,
  withTiming,
  cancelAnimation,
} from 'react-native-reanimated';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../theme/colors';
import type { RecordingStatus } from '../types';

interface RecordButtonProps {
  status: RecordingStatus;
  onPress: () => void;
}

const SIZE = 80;

export function RecordButton({ status, onPress }: RecordButtonProps) {
  const pulseScale = useSharedValue(1);

  React.useEffect(() => {
    if (status === 'recording') {
      pulseScale.value = withRepeat(
        withTiming(1.15, { duration: 800 }),
        -1,
        true,
      );
    } else {
      cancelAnimation(pulseScale);
      pulseScale.value = withTiming(1, { duration: 200 });
    }
  }, [status]);

  const pulseStyle = useAnimatedStyle(() => ({
    transform: [{ scale: pulseScale.value }],
  }));

  const bgColors =
    status === 'recording'
      ? [colors.recording, '#CC2200']
      : status === 'paused'
        ? [colors.paused, '#CC7700']
        : [colors.gradientStart, colors.gradientEnd];

  const icon =
    status === 'recording'
      ? 'stop'
      : status === 'paused'
        ? 'play'
        : 'mic';

  return (
    <Pressable onPress={onPress}>
      <Animated.View style={[styles.wrapper, pulseStyle]}>
        <LinearGradient
          colors={bgColors as [string, string]}
          style={styles.button}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
        >
          <Ionicons name={icon} size={36} color="#fff" />
        </LinearGradient>
      </Animated.View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    width: SIZE + 16,
    height: SIZE + 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  button: {
    width: SIZE,
    height: SIZE,
    borderRadius: SIZE / 2,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 12,
    elevation: 8,
  },
});
