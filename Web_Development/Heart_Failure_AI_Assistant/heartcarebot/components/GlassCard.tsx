// components/GlassCard.tsx
// ─────────────────────────────────────────────────────────────────────────────
// Reusable glassmorphism container card.
// Renders a frosted-glass panel with configurable padding and border radius.
// ─────────────────────────────────────────────────────────────────────────────

import React from 'react';
import {
  StyleSheet,
  View,
  ViewStyle,
  StyleProp,
} from 'react-native';
import { Colors, Radius, Spacing } from '@/constants/theme';

interface GlassCardProps {
  children: React.ReactNode;
  style?: StyleProp<ViewStyle>;
  padding?: number;
  radius?: number;
}

export function GlassCard({
  children,
  style,
  padding = Spacing.lg,
  radius = Radius.lg,
}: GlassCardProps) {
  return (
    <View
      style={[
        styles.card,
        { padding, borderRadius: radius },
        style,
      ]}
    >
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.bgGlass,
    borderWidth: 1,
    borderColor: Colors.borderGlass,
    // Soft inner shadow simulation via additional layer
    overflow: 'hidden',
  },
});
