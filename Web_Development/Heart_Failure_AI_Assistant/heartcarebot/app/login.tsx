// app/login.tsx
// ─────────────────────────────────────────────────────────────────────────────
// HeartCare Bot — Login Screen (One-Time Registration)
// Designed for elderly users: massive input, clear labels, no clutter.
// ─────────────────────────────────────────────────────────────────────────────

import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Animated,
  KeyboardAvoidingView,
  Platform,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { saveSession } from '@/utils/session';
import { HeartPulseIcon } from '@/components/HeartPulseIcon';
import { Colors, Typography, Spacing, Radius, Shadows } from '@/constants/theme';

export default function LoginScreen() {
  const router = useRouter();
  const [patientName, setPatientName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [inputFocused, setInputFocused] = useState(false);

  // Button press animation
  const buttonScale = useRef(new Animated.Value(1)).current;

  const animateButtonPress = (pressed: boolean) => {
    Animated.spring(buttonScale, {
      toValue: pressed ? 0.96 : 1,
      useNativeDriver: true,
      speed: 50,
      bounciness: 4,
    }).start();
  };

  const handleLogin = async () => {
    const name = patientName.trim();
    if (!name) {
      Alert.alert(
        'Nama Diperlukan',
        'Silakan masukkan nama Anda untuk melanjutkan.',
        [{ text: 'Mengerti', style: 'default' }]
      );
      return;
    }

    if (name.length < 2) {
      Alert.alert(
        'Nama Terlalu Pendek',
        'Nama harus terdiri dari minimal 2 karakter.',
        [{ text: 'OK', style: 'default' }]
      );
      return;
    }

    setIsLoading(true);
    try {
      await saveSession(name);
      // Navigate to dashboard with patient name
      router.replace({
        pathname: '/(main)/dashboard',
        params: { patientName: name },
      });
    } catch (error) {
      Alert.alert(
        'Terjadi Kesalahan',
        'Gagal menyimpan sesi. Silakan coba lagi.',
        [{ text: 'OK', style: 'default' }]
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <LinearGradient
      colors={Colors.gradientHero}
      locations={[0, 0.5, 1]}
      style={styles.gradientContainer}
    >
      <StatusBar style="light" />
      <KeyboardAvoidingView
        style={styles.flex}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={0}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          {/* ── Brand Header ─────────────────────────────────────────── */}
          <View style={styles.brandSection}>
            {/* Glowing pulse ring behind heart */}
            <View style={styles.iconRing}>
              <View style={styles.iconRingInner}>
                <HeartPulseIcon size={52} color={Colors.accentRed} animated />
              </View>
            </View>

            <Text style={styles.appName}>HeartCare</Text>
            <Text style={styles.appSubtitle}>Asisten Kesehatan Jantung</Text>

            {/* Decorative ECG-style line */}
            <View style={styles.ecgLine}>
              <View style={styles.ecgSegment} />
              <View style={styles.ecgPeak} />
              <View style={styles.ecgSegment} />
            </View>
          </View>

          {/* ── Login Form Card ────────────────────────────────────────── */}
          <View style={styles.formCard}>
            {/* Accent top border */}
            <LinearGradient
              colors={Colors.gradientButton}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
              style={styles.cardTopBorder}
            />

            <Text style={styles.welcomeTitle}>Selamat Datang</Text>
            <Text style={styles.welcomeSubtitle}>
              Masukkan nama Anda untuk memulai sesi pemantauan kesehatan jantung.
            </Text>

            {/* ── Name Input ─────────────────────────────────────────── */}
            <View style={styles.inputSection}>
              <Text style={styles.inputLabel}>Nama Pasien / Pengasuh</Text>
              <View
                style={[
                  styles.inputWrapper,
                  inputFocused && styles.inputWrapperFocused,
                ]}
              >
                <Text style={styles.inputIcon}>👤</Text>
                <TextInput
                  style={styles.textInput}
                  value={patientName}
                  onChangeText={setPatientName}
                  placeholder="Contoh: Pak Budi Santoso"
                  placeholderTextColor={Colors.textMuted}
                  autoCapitalize="words"
                  autoCorrect={false}
                  returnKeyType="done"
                  onSubmitEditing={handleLogin}
                  onFocus={() => setInputFocused(true)}
                  onBlur={() => setInputFocused(false)}
                  accessibilityLabel="Kolom nama pasien"
                  accessibilityHint="Ketuk di sini dan masukkan nama lengkap Anda"
                  editable={!isLoading}
                />
              </View>
              <Text style={styles.inputHint}>
                * Nama ini akan digunakan selama sesi berlangsung
              </Text>
            </View>

            {/* ── Submit Button ──────────────────────────────────────── */}
            <Animated.View style={{ transform: [{ scale: buttonScale }] }}>
              <TouchableOpacity
                activeOpacity={1}
                onPressIn={() => animateButtonPress(true)}
                onPressOut={() => animateButtonPress(false)}
                onPress={handleLogin}
                disabled={isLoading}
                accessibilityLabel="Tombol masuk"
                accessibilityHint="Ketuk untuk mulai menggunakan aplikasi"
                accessibilityRole="button"
              >
                <LinearGradient
                  colors={isLoading
                    ? [Colors.bgTertiary, Colors.bgTertiary]
                    : Colors.gradientButton
                  }
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 0 }}
                  style={[styles.loginButton, Shadows.button]}
                >
                  {isLoading ? (
                    <ActivityIndicator color={Colors.textOnAccent} size="small" />
                  ) : (
                    <>
                      <Text style={styles.loginButtonText}>Mulai Sekarang</Text>
                      <Text style={styles.loginButtonArrow}>→</Text>
                    </>
                  )}
                </LinearGradient>
              </TouchableOpacity>
            </Animated.View>

            {/* ── Privacy Note ───────────────────────────────────────── */}
            <View style={styles.privacyNote}>
              <Text style={styles.privacyIcon}>🔒</Text>
              <Text style={styles.privacyText}>
                Data Anda tersimpan hanya di perangkat ini. Tidak ada data yang dikirim ke server.
              </Text>
            </View>
          </View>

          {/* ── Footer ────────────────────────────────────────────────── */}
          <Text style={styles.footer}>
            HeartCare Bot — Stage 1 · Versi 1.0.0
          </Text>
        </ScrollView>
      </KeyboardAvoidingView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  gradientContainer: {
    flex: 1,
  },
  flex: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: Spacing.lg,
    paddingTop: Spacing.xxxl,
    paddingBottom: Spacing.xxl,
    alignItems: 'center',
  },

  // ── Brand Section ───────────────────────────────────────────────────────
  brandSection: {
    alignItems: 'center',
    marginBottom: Spacing.xxl,
  },
  iconRing: {
    width: 100,
    height: 100,
    borderRadius: Radius.full,
    backgroundColor: Colors.accentRedPale,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.lg,
    borderWidth: 1,
    borderColor: 'rgba(239,68,68,0.25)',
  },
  iconRingInner: {
    width: 80,
    height: 80,
    borderRadius: Radius.full,
    backgroundColor: 'rgba(239,68,68,0.08)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  appName: {
    fontFamily: Typography.fontFamily.extraBold,
    fontSize: Typography.size.xxxl,
    color: Colors.textPrimary,
    letterSpacing: Typography.tracking.tighter,
    marginBottom: Spacing.xs,
  },
  appSubtitle: {
    fontFamily: Typography.fontFamily.medium,
    fontSize: Typography.size.body,
    color: Colors.accentBlue,
    letterSpacing: Typography.tracking.wider,
    textTransform: 'uppercase',
    marginBottom: Spacing.lg,
  },
  // Decorative ECG line
  ecgLine: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 0,
  },
  ecgSegment: {
    width: 40,
    height: 2,
    backgroundColor: Colors.accentRed,
    opacity: 0.4,
  },
  ecgPeak: {
    width: 20,
    height: 14,
    borderTopWidth: 2,
    borderTopColor: Colors.accentRed,
    borderRightWidth: 2,
    borderRightColor: Colors.accentRed,
    marginTop: -12,
    borderTopRightRadius: 2,
  },

  // ── Form Card ────────────────────────────────────────────────────────────
  formCard: {
    width: '100%',
    backgroundColor: Colors.bgSecondary,
    borderRadius: Radius.xl,
    borderWidth: 1,
    borderColor: Colors.borderGlass,
    overflow: 'hidden',
    marginBottom: Spacing.xl,
    ...Shadows.card,
  },
  cardTopBorder: {
    height: 4,
    width: '100%',
  },
  welcomeTitle: {
    fontFamily: Typography.fontFamily.bold,
    fontSize: Typography.size.xxl,
    color: Colors.textPrimary,
    marginTop: Spacing.xl,
    marginHorizontal: Spacing.xl,
    marginBottom: Spacing.sm,
  },
  welcomeSubtitle: {
    fontFamily: Typography.fontFamily.regular,
    fontSize: Typography.size.body,
    color: Colors.textSecondary,
    lineHeight: Typography.size.body * Typography.lineHeight.relaxed,
    marginHorizontal: Spacing.xl,
    marginBottom: Spacing.xl,
  },

  // ── Input ────────────────────────────────────────────────────────────────
  inputSection: {
    marginHorizontal: Spacing.xl,
    marginBottom: Spacing.xl,
  },
  inputLabel: {
    fontFamily: Typography.fontFamily.semiBold,
    fontSize: Typography.size.body,
    color: Colors.textSecondary,
    marginBottom: Spacing.sm,
    letterSpacing: Typography.tracking.wider,
    textTransform: 'uppercase',
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.bgTertiary,
    borderRadius: Radius.md,
    borderWidth: 2,
    borderColor: Colors.borderGlass,
    paddingHorizontal: Spacing.md,
    minHeight: 64,
    marginBottom: Spacing.sm,
  },
  inputWrapperFocused: {
    borderColor: Colors.accentBlue,
    backgroundColor: Colors.accentBluePale,
  },
  inputIcon: {
    fontSize: 22,
    marginRight: Spacing.sm,
  },
  textInput: {
    flex: 1,
    fontFamily: Typography.fontFamily.medium,
    fontSize: Typography.size.lg,
    color: Colors.textPrimary,
    paddingVertical: Spacing.md,
  },
  inputHint: {
    fontFamily: Typography.fontFamily.regular,
    fontSize: Typography.size.sm,
    color: Colors.textMuted,
    lineHeight: Typography.size.sm * Typography.lineHeight.relaxed,
  },

  // ── Button ───────────────────────────────────────────────────────────────
  loginButton: {
    marginHorizontal: Spacing.xl,
    borderRadius: Radius.md,
    height: 64,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.lg,
    gap: Spacing.sm,
  },
  loginButtonText: {
    fontFamily: Typography.fontFamily.bold,
    fontSize: Typography.size.xl,
    color: Colors.textOnAccent,
    letterSpacing: Typography.tracking.wider,
  },
  loginButtonArrow: {
    fontFamily: Typography.fontFamily.bold,
    fontSize: Typography.size.xl,
    color: Colors.textOnAccent,
  },

  // ── Privacy Note ─────────────────────────────────────────────────────────
  privacyNote: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: Colors.accentBluePale,
    marginHorizontal: Spacing.xl,
    marginBottom: Spacing.xl,
    borderRadius: Radius.sm,
    padding: Spacing.md,
    gap: Spacing.sm,
    borderWidth: 1,
    borderColor: Colors.borderGlass,
  },
  privacyIcon: {
    fontSize: Typography.size.body,
  },
  privacyText: {
    flex: 1,
    fontFamily: Typography.fontFamily.regular,
    fontSize: Typography.size.sm,
    color: Colors.textSecondary,
    lineHeight: Typography.size.sm * Typography.lineHeight.relaxed,
  },

  // ── Footer ───────────────────────────────────────────────────────────────
  footer: {
    fontFamily: Typography.fontFamily.regular,
    fontSize: Typography.size.xs,
    color: Colors.textMuted,
    textAlign: 'center',
  },
});
