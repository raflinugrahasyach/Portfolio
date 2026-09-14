// app/(main)/dashboard.tsx
// ─────────────────────────────────────────────────────────────────────────────
// HeartCare Bot — Main Dashboard Screen
// Designed for elderly users: zero clutter, massive tap targets, bold text.
// ─────────────────────────────────────────────────────────────────────────────

import React, { useRef, useEffect, useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Animated,
  Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { clearSession } from '@/utils/session';
import { HeartPulseIcon } from '@/components/HeartPulseIcon';
import { Colors, Typography, Spacing, Radius, Shadows } from '@/constants/theme';

// ── Action Button Data ────────────────────────────────────────────────────────
interface ActionButton {
  id: string;
  icon: string;
  title: string;
  subtitle: string;
  gradient: readonly [string, string];
  accentColor: string;
  onPress: () => void;
  disabled?: boolean;
}

// ── Stat Card Component ───────────────────────────────────────────────────────
function StatCard({
  icon,
  label,
  value,
  color,
}: {
  icon: string;
  label: string;
  value: string;
  color: string;
}) {
  return (
    <View style={[styles.statCard, { borderColor: `${color}30` }]}>
      <Text style={styles.statIcon}>{icon}</Text>
      <Text style={[styles.statValue, { color }]}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

// ── Main Dashboard Component ──────────────────────────────────────────────────
export default function DashboardScreen() {
  const router = useRouter();
  const { patientName } = useLocalSearchParams<{ patientName: string }>();
  const displayName = patientName ?? 'Pengguna';

  // Get time-based greeting
  const getGreeting = (): { text: string; emoji: string } => {
    const hour = new Date().getHours();
    if (hour < 11) return { text: 'Selamat Pagi', emoji: '🌅' };
    if (hour < 15) return { text: 'Selamat Siang', emoji: '☀️' };
    if (hour < 18) return { text: 'Selamat Sore', emoji: '🌇' };
    return { text: 'Selamat Malam', emoji: '🌙' };
  };

  const greeting = getGreeting();

  // Button press animations (one per action button)
  const chatBtnScale = useRef(new Animated.Value(1)).current;
  const schedBtnScale = useRef(new Animated.Value(1)).current;

  // Header fade-in animation
  const headerOpacity = useRef(new Animated.Value(0)).current;
  const headerSlide = useRef(new Animated.Value(-20)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(headerOpacity, {
        toValue: 1,
        duration: 600,
        useNativeDriver: true,
      }),
      Animated.timing(headerSlide, {
        toValue: 0,
        duration: 600,
        useNativeDriver: true,
      }),
    ]).start();
  }, [headerOpacity, headerSlide]);

  const animateBtn = (anim: Animated.Value, pressed: boolean) => {
    Animated.spring(anim, {
      toValue: pressed ? 0.97 : 1,
      useNativeDriver: true,
      speed: 50,
      bounciness: 4,
    }).start();
  };

  const handleLogout = () => {
    Alert.alert(
      'Keluar Aplikasi',
      'Apakah Anda yakin ingin keluar dan menghapus sesi ini?',
      [
        { text: 'Batal', style: 'cancel' },
        {
          text: 'Keluar',
          style: 'destructive',
          onPress: async () => {
            await clearSession();
            router.replace('/login');
          },
        },
      ]
    );
  };

  const actionButtons: ActionButton[] = [
    {
      id: 'chat',
      icon: '🤖',
      title: 'Buka Chatbot Medis',
      subtitle: 'Tanya tentang kondisi jantung, gejala, & perawatan Anda',
      gradient: Colors.gradientButton,
      accentColor: Colors.accentBlue,
      onPress: () => router.push({
        pathname: '/(main)/chat',
        params: { patientName: displayName },
      }),
    },
    {
      id: 'schedule',
      icon: '📅',
      title: 'Jadwal Pengingat',
      subtitle: 'Kelola jadwal minum obat & pemeriksaan rutin Anda',
      gradient: Colors.gradientAmber,
      accentColor: Colors.accentAmber,
      onPress: () => router.push('/(main)/schedule' as any),
    },
  ];

  return (
    <LinearGradient
      colors={Colors.gradientHero}
      locations={[0, 0.5, 1]}
      style={styles.container}
    >
      <StatusBar style="light" />
      <SafeAreaView style={styles.safeArea} edges={['top']}>
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >

          {/* ── Top Bar ──────────────────────────────────────────────── */}
          <View style={styles.topBar}>
            <View style={styles.topBarLeft}>
              <HeartPulseIcon size={28} color={Colors.accentRed} animated />
              <Text style={styles.topBarTitle}>HeartCare</Text>
            </View>
            <TouchableOpacity
              style={styles.logoutBtn}
              onPress={handleLogout}
              accessibilityLabel="Tombol keluar"
              accessibilityRole="button"
            >
              <Text style={styles.logoutText}>Keluar</Text>
            </TouchableOpacity>
          </View>

          {/* ── Welcome Header ───────────────────────────────────────── */}
          <Animated.View
            style={[
              styles.welcomeSection,
              {
                opacity: headerOpacity,
                transform: [{ translateY: headerSlide }],
              },
            ]}
          >
            <View style={styles.greetingBadge}>
              <Text style={styles.greetingEmoji}>{greeting.emoji}</Text>
              <Text style={styles.greetingBadgeText}>{greeting.text}</Text>
            </View>

            <Text style={styles.patientName}>
              {displayName}
            </Text>

            <Text style={styles.welcomeSubtext}>
              Bagaimana kondisi Anda hari ini? Pilih layanan di bawah untuk memulai.
            </Text>
          </Animated.View>

          {/* ── Health Status Strip ───────────────────────────────────── */}
          <View style={styles.statsRow}>
            <StatCard icon="💊" label="Obat Hari Ini" value="Siap" color={Colors.accentGreen} />
            <StatCard icon="❤️" label="Status" value="Dipantau" color={Colors.accentRed} />
            <StatCard icon="📊" label="Catatan" value="0 Log" color={Colors.accentBlue} />
          </View>

          {/* ── Section Label ─────────────────────────────────────────── */}
          <View style={styles.sectionHeader}>
            <View style={styles.sectionAccentBar} />
            <Text style={styles.sectionLabel}>LAYANAN UTAMA</Text>
          </View>

          {/* ── Action Buttons ───────────────────────────────────────── */}
          <View style={styles.actionsContainer}>
            {actionButtons.map((btn, index) => {
              const scaleAnim = index === 0 ? chatBtnScale : schedBtnScale;

              return (
                <Animated.View
                  key={btn.id}
                  style={{ transform: [{ scale: scaleAnim }] }}
                >
                  <TouchableOpacity
                    activeOpacity={1}
                    onPressIn={() => animateBtn(scaleAnim, true)}
                    onPressOut={() => animateBtn(scaleAnim, false)}
                    onPress={btn.onPress}
                    accessibilityLabel={btn.title}
                    accessibilityHint={btn.subtitle}
                    accessibilityRole="button"
                    style={[styles.actionButtonOuter, Shadows.button]}
                  >
                    <LinearGradient
                      colors={btn.gradient}
                      start={{ x: 0, y: 0 }}
                      end={{ x: 1, y: 1 }}
                      style={styles.actionButtonGradient}
                    >
                      {/* Glassmorphism overlay */}
                      <View style={styles.actionButtonGlass}>
                        {/* Left: Icon in circle */}
                        <View style={[
                          styles.actionIconCircle,
                          { backgroundColor: 'rgba(255,255,255,0.15)' }
                        ]}>
                          <Text style={styles.actionIcon}>{btn.icon}</Text>
                        </View>

                        {/* Center: Text */}
                        <View style={styles.actionTextBlock}>
                          <Text style={styles.actionTitle}>{btn.title}</Text>
                          <Text style={styles.actionSubtitle}>{btn.subtitle}</Text>
                          {btn.disabled && (
                            <View style={styles.comingSoonBadge}>
                              <Text style={styles.comingSoonText}>SEGERA HADIR</Text>
                            </View>
                          )}
                        </View>

                        {/* Right: Arrow */}
                        <Text style={styles.actionArrow}>
                          {btn.disabled ? '🔒' : '›'}
                        </Text>
                      </View>
                    </LinearGradient>
                  </TouchableOpacity>
                </Animated.View>
              );
            })}
          </View>

          {/* ── Info Card ─────────────────────────────────────────────── */}
          <View style={styles.infoCard}>
            <LinearGradient
              colors={Colors.gradientCard}
              style={styles.infoCardGradient}
            >
              <Text style={styles.infoIcon}>ℹ️</Text>
              <View style={styles.infoTextBlock}>
                <Text style={styles.infoTitle}>Tentang HeartCare Bot</Text>
                <Text style={styles.infoBody}>
                  Aplikasi ini membantu Anda memantau kondisi gagal jantung dan menjawab pertanyaan seputar kesehatan jantung. Bukan pengganti dokter.
                </Text>
              </View>
            </LinearGradient>
          </View>

          {/* ── Emergency Note ────────────────────────────────────────── */}
          <View style={styles.emergencyCard}>
            <Text style={styles.emergencyIcon}>🚨</Text>
            <Text style={styles.emergencyText}>
              Darurat? Segera hubungi{' '}
              <Text style={styles.emergencyNumber}>119</Text>
              {' '}atau pergi ke IGD rumah sakit terdekat.
            </Text>
          </View>

        </ScrollView>
      </SafeAreaView>
    </LinearGradient>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────────
const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  safeArea: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: Spacing.lg,
    paddingBottom: Spacing.xxl,
  },

  // ── Top Bar ─────────────────────────────────────────────────────────────
  topBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: Spacing.md,
    marginBottom: Spacing.md,
  },
  topBarLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
  },
  topBarTitle: {
    fontFamily: Typography.fontFamily.bold,
    fontSize: Typography.size.xl,
    color: Colors.textPrimary,
    letterSpacing: Typography.tracking.tighter,
  },
  logoutBtn: {
    paddingVertical: Spacing.sm,
    paddingHorizontal: Spacing.md,
    backgroundColor: Colors.bgGlass,
    borderRadius: Radius.full,
    borderWidth: 1,
    borderColor: Colors.borderGlass,
  },
  logoutText: {
    fontFamily: Typography.fontFamily.medium,
    fontSize: Typography.size.sm,
    color: Colors.textSecondary,
  },

  // ── Welcome Section ──────────────────────────────────────────────────────
  welcomeSection: {
    marginBottom: Spacing.xl,
    paddingTop: Spacing.md,
  },
  greetingBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.accentBluePale,
    borderRadius: Radius.full,
    paddingVertical: Spacing.xs,
    paddingHorizontal: Spacing.md,
    alignSelf: 'flex-start',
    marginBottom: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.borderGlass,
    gap: Spacing.xs,
  },
  greetingEmoji: {
    fontSize: Typography.size.body,
  },
  greetingBadgeText: {
    fontFamily: Typography.fontFamily.medium,
    fontSize: Typography.size.body,
    color: Colors.accentBlue,
  },
  patientName: {
    fontFamily: Typography.fontFamily.extraBold,
    fontSize: Typography.size.xxxl,
    color: Colors.textPrimary,
    marginBottom: Spacing.sm,
    lineHeight: Typography.size.xxxl * Typography.lineHeight.tight,
  },
  welcomeSubtext: {
    fontFamily: Typography.fontFamily.regular,
    fontSize: Typography.size.body,
    color: Colors.textSecondary,
    lineHeight: Typography.size.body * Typography.lineHeight.relaxed,
  },

  // ── Stats Row ─────────────────────────────────────────────────────────────
  statsRow: {
    flexDirection: 'row',
    gap: Spacing.sm,
    marginBottom: Spacing.xl,
  },
  statCard: {
    flex: 1,
    backgroundColor: Colors.bgSecondary,
    borderRadius: Radius.md,
    borderWidth: 1,
    padding: Spacing.md,
    alignItems: 'center',
    gap: Spacing.xs,
  },
  statIcon: {
    fontSize: 20,
  },
  statValue: {
    fontFamily: Typography.fontFamily.bold,
    fontSize: Typography.size.sm,
    textAlign: 'center',
  },
  statLabel: {
    fontFamily: Typography.fontFamily.regular,
    fontSize: Typography.size.xs,
    color: Colors.textMuted,
    textAlign: 'center',
  },

  // ── Section Header ────────────────────────────────────────────────────────
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    marginBottom: Spacing.md,
  },
  sectionAccentBar: {
    width: 4,
    height: 20,
    backgroundColor: Colors.accentBlue,
    borderRadius: Radius.full,
  },
  sectionLabel: {
    fontFamily: Typography.fontFamily.semiBold,
    fontSize: Typography.size.sm,
    color: Colors.textMuted,
    letterSpacing: Typography.tracking.widest,
    textTransform: 'uppercase',
  },

  // ── Action Buttons ────────────────────────────────────────────────────────
  actionsContainer: {
    gap: Spacing.md,
    marginBottom: Spacing.xl,
  },
  actionButtonOuter: {
    borderRadius: Radius.xl,
    overflow: 'hidden',
  },
  actionButtonGradient: {
    borderRadius: Radius.xl,
    minHeight: 120,
  },
  actionButtonGlass: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: Spacing.lg,
    gap: Spacing.md,
    backgroundColor: 'rgba(0,0,0,0.08)',
    borderRadius: Radius.xl,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.20)',
    minHeight: 120,
  },
  actionIconCircle: {
    width: 64,
    height: 64,
    borderRadius: Radius.full,
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
  },
  actionIcon: {
    fontSize: 32,
  },
  actionTextBlock: {
    flex: 1,
  },
  actionTitle: {
    fontFamily: Typography.fontFamily.bold,
    fontSize: Typography.size.xl,
    color: Colors.textOnAccent,
    marginBottom: Spacing.xs,
    lineHeight: Typography.size.xl * Typography.lineHeight.tight,
  },
  actionSubtitle: {
    fontFamily: Typography.fontFamily.regular,
    fontSize: Typography.size.body,
    color: 'rgba(255,255,255,0.80)',
    lineHeight: Typography.size.body * Typography.lineHeight.normal,
  },
  comingSoonBadge: {
    marginTop: Spacing.sm,
    backgroundColor: 'rgba(0,0,0,0.25)',
    borderRadius: Radius.sm,
    paddingVertical: 3,
    paddingHorizontal: Spacing.sm,
    alignSelf: 'flex-start',
  },
  comingSoonText: {
    fontFamily: Typography.fontFamily.semiBold,
    fontSize: Typography.size.xs,
    color: 'rgba(255,255,255,0.80)',
    letterSpacing: Typography.tracking.widest,
  },
  actionArrow: {
    fontFamily: Typography.fontFamily.extraBold,
    fontSize: 32,
    color: 'rgba(255,255,255,0.80)',
    flexShrink: 0,
  },

  // ── Info Card ────────────────────────────────────────────────────────────
  infoCard: {
    borderRadius: Radius.lg,
    overflow: 'hidden',
    marginBottom: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.borderGlass,
  },
  infoCardGradient: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    padding: Spacing.lg,
    gap: Spacing.md,
  },
  infoIcon: {
    fontSize: 22,
    flexShrink: 0,
  },
  infoTextBlock: {
    flex: 1,
  },
  infoTitle: {
    fontFamily: Typography.fontFamily.semiBold,
    fontSize: Typography.size.body,
    color: Colors.textPrimary,
    marginBottom: Spacing.xs,
  },
  infoBody: {
    fontFamily: Typography.fontFamily.regular,
    fontSize: Typography.size.body,
    color: Colors.textSecondary,
    lineHeight: Typography.size.body * Typography.lineHeight.relaxed,
  },

  // ── Emergency Card ────────────────────────────────────────────────────────
  emergencyCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.accentRedPale,
    borderRadius: Radius.md,
    borderWidth: 1,
    borderColor: 'rgba(239,68,68,0.25)',
    padding: Spacing.md,
    gap: Spacing.sm,
  },
  emergencyIcon: {
    fontSize: 22,
    flexShrink: 0,
  },
  emergencyText: {
    flex: 1,
    fontFamily: Typography.fontFamily.medium,
    fontSize: Typography.size.body,
    color: Colors.textSecondary,
    lineHeight: Typography.size.body * Typography.lineHeight.relaxed,
  },
  emergencyNumber: {
    fontFamily: Typography.fontFamily.extraBold,
    fontSize: Typography.size.body,
    color: Colors.accentRed,
  },
});
