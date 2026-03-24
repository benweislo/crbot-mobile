import React from 'react';
import { View, StyleSheet } from 'react-native';
import Animated, { useAnimatedStyle, withTiming } from 'react-native-reanimated';
import { colors } from '../theme/colors';

interface AudioLevelProps {
  level: number; // 0-1
  isActive: boolean;
}

const BAR_COUNT = 5;

export function AudioLevel({ level, isActive }: AudioLevelProps) {
  return (
    <View style={styles.container}>
      {Array.from({ length: BAR_COUNT }, (_, i) => (
        <Bar key={i} index={i} level={level} isActive={isActive} />
      ))}
    </View>
  );
}

function Bar({ index, level, isActive }: { index: number; level: number; isActive: boolean }) {
  const threshold = (index + 1) / BAR_COUNT;
  const animStyle = useAnimatedStyle(() => ({
    height: withTiming(isActive && level >= threshold ? 12 + index * 6 : 4, {
      duration: 100,
    }),
    backgroundColor: isActive && level >= threshold ? colors.secondary : colors.surfaceBorder,
  }));

  return <Animated.View style={[styles.bar, animStyle]} />;
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 4,
    height: 42,
  },
  bar: {
    width: 6,
    borderRadius: 3,
  },
});
