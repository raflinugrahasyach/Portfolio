// components/HeartPulseIcon.tsx
// ─────────────────────────────────────────────────────────────────────────────
// Animated heart-pulse SVG icon for branding purposes.
// Used on the Login screen and Dashboard header.
// ─────────────────────────────────────────────────────────────────────────────

import React, { useEffect, useRef } from 'react';
import { Animated, View, StyleSheet } from 'react-native';
import { Colors } from '@/constants/theme';

interface HeartPulseIconProps {
  size?: number;
  color?: string;
  animated?: boolean;
}

export function HeartPulseIcon({
  size = 48,
  color = Colors.accentRed,
  animated: shouldAnimate = true,
}: HeartPulseIconProps) {
  const scaleAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    if (!shouldAnimate) return;

    const pulse = Animated.sequence([
      Animated.timing(scaleAnim, {
        toValue: 1.15,
        duration: 350,
        useNativeDriver: true,
      }),
      Animated.timing(scaleAnim, {
        toValue: 1,
        duration: 350,
        useNativeDriver: true,
      }),
      Animated.delay(700),
    ]);

    const loop = Animated.loop(pulse);
    loop.start();

    return () => loop.stop();
  }, [scaleAnim, shouldAnimate]);

  return (
    <Animated.View style={{ transform: [{ scale: scaleAnim }] }}>
      <View style={[styles.container, { width: size, height: size }]}>
        {/* Simple heart shape using two overlapping circles + rotated square */}
        <View
          style={[
            styles.heartBody,
            {
              width: size * 0.55,
              height: size * 0.55,
              backgroundColor: color,
              borderRadius: size * 0.55,
              top: size * 0.2,
              left: size * 0.04,
            },
          ]}
        />
        <View
          style={[
            styles.heartBody,
            {
              width: size * 0.55,
              height: size * 0.55,
              backgroundColor: color,
              borderRadius: size * 0.55,
              top: size * 0.2,
              right: size * 0.04,
            },
          ]}
        />
        <View
          style={[
            styles.heartDiamond,
            {
              width: size * 0.65,
              height: size * 0.65,
              backgroundColor: color,
              bottom: size * 0.02,
              left: size * 0.175,
            },
          ]}
        />
      </View>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'relative',
  },
  heartBody: {
    position: 'absolute',
  },
  heartDiamond: {
    position: 'absolute',
    transform: [{ rotate: '45deg' }],
  },
});
