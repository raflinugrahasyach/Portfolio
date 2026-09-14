// app/(main)/schedule.tsx
// ─────────────────────────────────────────────────────────────────────────────
// HeartCare Bot — Jadwal Pengingat Screen
// Full schedule management with toggle switches per alarm.
// ─────────────────────────────────────────────────────────────────────────────

import React, { useEffect, useState, useCallback } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Switch,
  Alert,
  ActivityIndicator,
} from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { StatusBar } from "expo-status-bar";
import {
  SCHEDULES,
  ScheduleItem,
  requestNotificationPermissions,
  scheduleAllAlarms,
  cancelAllAlarms,
  getActiveAlarmIds,
  toggleAlarm,
} from "@/utils/notifications";
import { Colors, Typography, Spacing, Radius, Shadows } from "@/constants/theme";

// ── Helper: Format time to HH:mm WIB ─────────────────────────────────────────
function formatTime(hour: number, minute: number): string {
  const h = String(hour).padStart(2, "0");
  const m = String(minute).padStart(2, "0");
  return `${h}:${m} WIB`;
}

function getCategoryLabel(category: ScheduleItem["category"]): string {
  return category === "weight" ? "BERAT BADAN" : "OBAT-OBATAN";
}

function getCategoryIcon(category: ScheduleItem["category"]): string {
  return category === "weight" ? "⚖️" : "💊";
}

// ── Schedule Card Component ───────────────────────────────────────────────────
function ScheduleCard({
  item,
  isActive,
  onToggle,
}: {
  item: ScheduleItem;
  isActive: boolean;
  onToggle: (item: ScheduleItem, isActive: boolean) => void;
}) {
  return (
    <View style={[styles.card, { borderLeftColor: item.color, borderLeftWidth: 4 }]}>
      <View style={styles.cardLeft}>
        <View style={[styles.iconBadge, { backgroundColor: `${item.color}20` }]}>
          <Text style={styles.iconText}>{getCategoryIcon(item.category)}</Text>
        </View>
        <View style={styles.cardTextBlock}>
          <View style={[styles.categoryBadge, { backgroundColor: `${item.color}22` }]}>
            <Text style={[styles.categoryText, { color: item.color }]}>
              {getCategoryLabel(item.category)}
            </Text>
          </View>
          <Text style={styles.cardTitle}>{item.title}</Text>
          <Text style={styles.cardTime}>{formatTime(item.hour, item.minute)}</Text>
          <Text style={styles.cardBody} numberOfLines={2}>{item.body}</Text>
        </View>
      </View>
      <Switch
        value={isActive}
        onValueChange={() => onToggle(item, isActive)}
        trackColor={{ false: Colors.bgTertiary, true: item.color }}
        thumbColor={isActive ? "#FFFFFF" : Colors.textMuted}
        ios_backgroundColor={Colors.bgTertiary}
        style={styles.switch}
      />
    </View>
  );
}

// ── Main Schedule Screen ──────────────────────────────────────────────────────
export default function ScheduleScreen() {
  const router = useRouter();
  const [activeIds, setActiveIds] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [permGranted, setPermGranted] = useState(false);

  // Load current active alarm state
  const refreshActiveIds = useCallback(async () => {
    const ids = await getActiveAlarmIds();
    setActiveIds(ids);
  }, []);

  useEffect(() => {
    (async () => {
      const granted = await requestNotificationPermissions();
      setPermGranted(granted);
      if (granted) {
        await refreshActiveIds();
      }
      setLoading(false);
    })();
  }, [refreshActiveIds]);

  const handleToggle = useCallback(
    async (item: ScheduleItem, isActive: boolean) => {
      if (!permGranted) {
        Alert.alert(
          "Izin Diperlukan",
          "Aplikasi membutuhkan izin notifikasi untuk mengaktifkan pengingat. Aktifkan di Pengaturan > Aplikasi > HeartCare.",
          [{ text: "OK" }]
        );
        return;
      }
      try {
        await toggleAlarm(item, isActive);
        await refreshActiveIds();
      } catch (e) {
        Alert.alert("Gagal", "Tidak dapat mengubah pengingat. Coba lagi.");
      }
    },
    [permGranted, refreshActiveIds]
  );

  const handleActivateAll = useCallback(async () => {
    if (!permGranted) {
      Alert.alert(
        "Izin Diperlukan",
        "Aktifkan izin notifikasi terlebih dahulu di pengaturan perangkat.",
        [{ text: "OK" }]
      );
      return;
    }
    setLoading(true);
    await scheduleAllAlarms();
    await refreshActiveIds();
    setLoading(false);
    Alert.alert("✅ Berhasil", "Semua 4 pengingat harian telah diaktifkan!");
  }, [permGranted, refreshActiveIds]);

  const handleCancelAll = useCallback(async () => {
    Alert.alert(
      "Matikan Semua Pengingat",
      "Apakah Anda yakin ingin mematikan semua pengingat harian?",
      [
        { text: "Batal", style: "cancel" },
        {
          text: "Matikan Semua",
          style: "destructive",
          onPress: async () => {
            setLoading(true);
            await cancelAllAlarms();
            await refreshActiveIds();
            setLoading(false);
          },
        },
      ]
    );
  }, [refreshActiveIds]);

  const activeCount = SCHEDULES.filter((s) => activeIds.has(s.id)).length;

  return (
    <LinearGradient colors={Colors.gradientHero} locations={[0, 0.5, 1]} style={styles.container}>
      <StatusBar style="light" />
      <SafeAreaView style={styles.safeArea} edges={["top"]}>
        {/* ── Header ─── */}
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.backBtn}
            onPress={() => router.back()}
            accessibilityLabel="Kembali ke Dashboard"
            accessibilityRole="button"
          >
            <Text style={styles.backArrow}>←</Text>
          </TouchableOpacity>
          <View style={styles.headerCenter}>
            <Text style={styles.headerTitle}>Jadwal Pengingat</Text>
            <Text style={styles.headerSub}>
              {activeCount} dari {SCHEDULES.length} alarm aktif
            </Text>
          </View>
          <View style={{ width: 44 }} />
        </View>

        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={Colors.accentBlue} />
            <Text style={styles.loadingText}>Memuat status pengingat...</Text>
          </View>
        ) : (
          <ScrollView
            contentContainerStyle={styles.scrollContent}
            showsVerticalScrollIndicator={false}
          >
            {/* ── Permission Warning ─── */}
            {!permGranted && (
              <View style={styles.warningCard}>
                <Text style={styles.warningIcon}>⚠️</Text>
                <Text style={styles.warningText}>
                  Izin notifikasi belum diberikan. Fitur pengingat tidak akan berfungsi. Aktifkan
                  izin di Pengaturan perangkat Anda.
                </Text>
              </View>
            )}

            {/* ── Status Summary Card ─── */}
            <LinearGradient
              colors={["rgba(59,130,246,0.18)", "rgba(59,130,246,0.05)"]}
              style={styles.summaryCard}
            >
              <Text style={styles.summaryTitle}>Status Pengingat Hari Ini</Text>
              <View style={styles.summaryRow}>
                <View style={styles.summaryBadge}>
                  <Text style={styles.summaryNum}>{activeCount}</Text>
                  <Text style={styles.summaryLabel}>Aktif</Text>
                </View>
                <View style={styles.summaryDivider} />
                <View style={styles.summaryBadge}>
                  <Text style={[styles.summaryNum, { color: Colors.textMuted }]}>
                    {SCHEDULES.length - activeCount}
                  </Text>
                  <Text style={styles.summaryLabel}>Nonaktif</Text>
                </View>
                <View style={styles.summaryDivider} />
                <View style={styles.summaryBadge}>
                  <Text style={[styles.summaryNum, { color: Colors.accentAmber }]}>
                    {SCHEDULES.length}
                  </Text>
                  <Text style={styles.summaryLabel}>Total</Text>
                </View>
              </View>
            </LinearGradient>

            {/* ── Section: BERAT BADAN ─── */}
            <View style={styles.sectionHeader}>
              <View style={[styles.sectionBar, { backgroundColor: Colors.accentGreen }]} />
              <Text style={styles.sectionLabel}>BERAT BADAN</Text>
            </View>
            {SCHEDULES.filter((s) => s.category === "weight").map((item) => (
              <ScheduleCard
                key={item.id}
                item={item}
                isActive={activeIds.has(item.id)}
                onToggle={handleToggle}
              />
            ))}

            {/* ── Section: OBAT-OBATAN ─── */}
            <View style={[styles.sectionHeader, { marginTop: Spacing.lg }]}>
              <View style={[styles.sectionBar, { backgroundColor: Colors.accentBlue }]} />
              <Text style={styles.sectionLabel}>OBAT-OBATAN</Text>
            </View>
            {SCHEDULES.filter((s) => s.category === "medication").map((item) => (
              <ScheduleCard
                key={item.id}
                item={item}
                isActive={activeIds.has(item.id)}
                onToggle={handleToggle}
              />
            ))}

            {/* ── Bulk Action Buttons ─── */}
            <View style={styles.bulkActions}>
              <TouchableOpacity
                style={[styles.bulkBtn, styles.bulkBtnPrimary, Shadows.button]}
                onPress={handleActivateAll}
                accessibilityLabel="Aktifkan semua pengingat"
                accessibilityRole="button"
              >
                <Text style={styles.bulkBtnText}>✅  Aktifkan Semua</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.bulkBtn, styles.bulkBtnDanger]}
                onPress={handleCancelAll}
                accessibilityLabel="Matikan semua pengingat"
                accessibilityRole="button"
              >
                <Text style={[styles.bulkBtnText, { color: Colors.accentRed }]}>
                  🔕  Matikan Semua
                </Text>
              </TouchableOpacity>
            </View>

            {/* ── Info note ─── */}
            <View style={styles.infoNote}>
              <Text style={styles.infoNoteText}>
                ℹ️ Pengingat berjalan setiap hari pada waktu yang telah ditentukan, bahkan saat
                aplikasi ditutup. Pastikan perangkat tidak dalam mode Jangan Ganggu.
              </Text>
            </View>
          </ScrollView>
        )}
      </SafeAreaView>
    </LinearGradient>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────────
const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: { flex: 1 },

  // Header
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: Colors.divider,
  },
  backBtn: {
    width: 44,
    height: 44,
    borderRadius: Radius.full,
    backgroundColor: Colors.bgGlass,
    borderWidth: 1,
    borderColor: Colors.borderGlass,
    alignItems: "center",
    justifyContent: "center",
  },
  backArrow: {
    fontSize: 24,
    color: Colors.textPrimary,
    fontFamily: Typography.fontFamily.bold,
  },
  headerCenter: { alignItems: "center" },
  headerTitle: {
    fontFamily: Typography.fontFamily.bold,
    fontSize: Typography.size.xl,
    color: Colors.textPrimary,
  },
  headerSub: {
    fontFamily: Typography.fontFamily.regular,
    fontSize: Typography.size.sm,
    color: Colors.accentBlue,
    marginTop: 2,
  },

  // Loading
  loadingContainer: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: Spacing.md,
  },
  loadingText: {
    fontFamily: Typography.fontFamily.regular,
    fontSize: Typography.size.body,
    color: Colors.textSecondary,
  },

  // Scroll
  scrollContent: {
    padding: Spacing.lg,
    paddingBottom: Spacing.xxl,
    gap: Spacing.md,
  },

  // Warning
  warningCard: {
    flexDirection: "row",
    alignItems: "flex-start",
    backgroundColor: "rgba(245,158,11,0.15)",
    borderRadius: Radius.md,
    borderWidth: 1,
    borderColor: "rgba(245,158,11,0.35)",
    padding: Spacing.md,
    gap: Spacing.sm,
  },
  warningIcon: { fontSize: 20, flexShrink: 0 },
  warningText: {
    flex: 1,
    fontFamily: Typography.fontFamily.medium,
    fontSize: Typography.size.body,
    color: Colors.accentAmber,
    lineHeight: Typography.size.body * Typography.lineHeight.relaxed,
  },

  // Summary card
  summaryCard: {
    borderRadius: Radius.lg,
    borderWidth: 1,
    borderColor: Colors.borderGlass,
    padding: Spacing.lg,
    marginBottom: Spacing.sm,
  },
  summaryTitle: {
    fontFamily: Typography.fontFamily.semiBold,
    fontSize: Typography.size.body,
    color: Colors.textPrimary,
    marginBottom: Spacing.md,
    textAlign: "center",
  },
  summaryRow: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    gap: Spacing.lg,
  },
  summaryBadge: { alignItems: "center", gap: 4 },
  summaryNum: {
    fontFamily: Typography.fontFamily.extraBold,
    fontSize: Typography.size.xxxl,
    color: Colors.accentGreen,
  },
  summaryLabel: {
    fontFamily: Typography.fontFamily.medium,
    fontSize: Typography.size.sm,
    color: Colors.textMuted,
  },
  summaryDivider: {
    width: 1,
    height: 48,
    backgroundColor: Colors.divider,
  },

  // Section headers
  sectionHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: Spacing.sm,
    marginBottom: Spacing.sm,
  },
  sectionBar: {
    width: 4,
    height: 20,
    borderRadius: Radius.full,
  },
  sectionLabel: {
    fontFamily: Typography.fontFamily.semiBold,
    fontSize: Typography.size.sm,
    color: Colors.textMuted,
    letterSpacing: Typography.tracking.widest,
  },

  // Schedule cards
  card: {
    backgroundColor: Colors.bgSecondary,
    borderRadius: Radius.lg,
    borderWidth: 1,
    borderColor: Colors.borderGlass,
    padding: Spacing.md,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: Spacing.sm,
  },
  cardLeft: {
    flexDirection: "row",
    alignItems: "flex-start",
    flex: 1,
    gap: Spacing.md,
  },
  iconBadge: {
    width: 52,
    height: 52,
    borderRadius: Radius.md,
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
  },
  iconText: { fontSize: 26 },
  cardTextBlock: { flex: 1, gap: 4 },
  categoryBadge: {
    alignSelf: "flex-start",
    borderRadius: Radius.sm,
    paddingHorizontal: Spacing.sm,
    paddingVertical: 2,
    marginBottom: 2,
  },
  categoryText: {
    fontFamily: Typography.fontFamily.semiBold,
    fontSize: 11,
    letterSpacing: Typography.tracking.widest,
  },
  cardTitle: {
    fontFamily: Typography.fontFamily.bold,
    fontSize: Typography.size.body,
    color: Colors.textPrimary,
  },
  cardTime: {
    fontFamily: Typography.fontFamily.semiBold,
    fontSize: Typography.size.xl,
    color: Colors.accentBlue,
    marginVertical: 2,
  },
  cardBody: {
    fontFamily: Typography.fontFamily.regular,
    fontSize: Typography.size.sm,
    color: Colors.textMuted,
    lineHeight: Typography.size.sm * Typography.lineHeight.relaxed,
  },
  switch: { flexShrink: 0, marginLeft: Spacing.sm },

  // Bulk actions
  bulkActions: {
    gap: Spacing.md,
    marginTop: Spacing.md,
  },
  bulkBtn: {
    borderRadius: Radius.lg,
    paddingVertical: Spacing.md,
    alignItems: "center",
    justifyContent: "center",
    minHeight: 60,
  },
  bulkBtnPrimary: {
    backgroundColor: Colors.accentBlue,
  },
  bulkBtnDanger: {
    backgroundColor: "rgba(239,68,68,0.12)",
    borderWidth: 1,
    borderColor: "rgba(239,68,68,0.30)",
  },
  bulkBtnText: {
    fontFamily: Typography.fontFamily.bold,
    fontSize: Typography.size.body,
    color: Colors.textOnAccent,
  },

  // Info note
  infoNote: {
    backgroundColor: Colors.bgGlass,
    borderRadius: Radius.md,
    borderWidth: 1,
    borderColor: Colors.borderGlass,
    padding: Spacing.md,
    marginTop: Spacing.sm,
  },
  infoNoteText: {
    fontFamily: Typography.fontFamily.regular,
    fontSize: Typography.size.sm,
    color: Colors.textMuted,
    lineHeight: Typography.size.sm * Typography.lineHeight.relaxed,
  },
});
