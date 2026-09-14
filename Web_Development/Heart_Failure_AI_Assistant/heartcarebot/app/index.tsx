// app/index.tsx
// ─────────────────────────────────────────────────────────────────────────────
// HeartCare Bot — Root Entry Route (/)
// Checks authentication/session state and redirects to Dashboard or Login.
// ─────────────────────────────────────────────────────────────────────────────

import React, { useEffect } from 'react';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { getSession } from '@/utils/session';
import { Colors } from '@/constants/theme';

export default function IndexScreen() {
  const router = useRouter();

  useEffect(() => {
    let isMounted = true;

    async function checkAuthAndRedirect() {
      try {
        const session = await getSession();
        if (!isMounted) return;

        if (session && session.patientName) {
          router.replace({
            pathname: '/(main)/dashboard',
            params: { patientName: session.patientName },
          });
        } else {
          router.replace('/login');
        }
      } catch (err) {
        if (isMounted) {
          router.replace('/login');
        }
      }
    }

    checkAuthAndRedirect();

    return () => {
      isMounted = false;
    };
  }, [router]);

  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color={Colors.accentBlue} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.bgPrimary,
    alignItems: 'center',
    justifyContent: 'center',
  },
});
