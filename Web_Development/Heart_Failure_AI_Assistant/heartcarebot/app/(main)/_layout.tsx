// app/(main)/_layout.tsx
// ─────────────────────────────────────────────────────────────────────────────
// Main group layout — wraps Dashboard and Chat screens.
// No tabs or navigation bar; stack-based for simplicity.
// ─────────────────────────────────────────────────────────────────────────────

import { Stack } from 'expo-router';
import { Colors } from '@/constants/theme';

export default function MainLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: Colors.bgPrimary },
        animation: 'slide_from_right',
      }}
    >
      <Stack.Screen name="dashboard" />
      <Stack.Screen name="chat" />
      <Stack.Screen name="schedule" />
    </Stack>
  );
}
