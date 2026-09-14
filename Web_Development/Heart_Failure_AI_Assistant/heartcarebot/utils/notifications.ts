// utils/notifications.ts
// ─────────────────────────────────────────────────────────────────────────────
// HeartCare Bot — Local Notification Utility
// ─────────────────────────────────────────────────────────────────────────────

import * as Notifications from "expo-notifications";
import { Platform } from "react-native";

const CHANNEL_ID = "heartcare-alarms";

export interface ScheduleItem {
  id: string;
  title: string;
  body: string;
  hour: number;
  minute: number;
  icon: string;
  category: "weight" | "medication";
  color: string;
}

export const SCHEDULES: ScheduleItem[] = [
  {
    id: "weight-morning",
    title: "Pengukuran Berat Badan",
    body: "Waktunya timbang badan! Timbang sebelum makan pagi dan catat hasilnya.",
    hour: 8,
    minute: 0,
    icon: "scale",
    category: "weight",
    color: "#22C55E",
  },
  {
    id: "med-morning",
    title: "Minum Obat Pagi",
    body: "Jangan lupa minum obat jantung pagi Anda sesuai anjuran dokter.",
    hour: 8,
    minute: 0,
    icon: "pill",
    category: "medication",
    color: "#3B82F6",
  },
  {
    id: "med-afternoon",
    title: "Minum Obat Siang",
    body: "Saatnya minum obat siang. Pastikan Anda sudah makan terlebih dahulu.",
    hour: 13,
    minute: 0,
    icon: "pill",
    category: "medication",
    color: "#F59E0B",
  },
  {
    id: "med-evening",
    title: "Minum Obat Malam",
    body: "Pengingat obat malam hari. Minum obat sebelum tidur sesuai resep dokter.",
    hour: 20,
    minute: 0,
    icon: "pill",
    category: "medication",
    color: "#8B5CF6",
  },
];

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldPlaySound: true,
    shouldSetBadge: false,
    shouldShowAlert: true,
    shouldShowBanner: true,
    shouldShowList: true,
  }),
});

export async function setupNotificationChannel(): Promise<void> {
  if (Platform.OS === "android") {
    await Notifications.setNotificationChannelAsync(CHANNEL_ID, {
      name: "HeartCare Alarm Harian",
      description: "Pengingat harian untuk berat badan dan obat-obatan",
      importance: Notifications.AndroidImportance.HIGH,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: "#3B82F6",
      sound: "default",
      enableVibrate: true,
      showBadge: true,
    });
  }
}

export async function requestNotificationPermissions(): Promise<boolean> {
  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  if (existingStatus === "granted") return true;
  const { status } = await Notifications.requestPermissionsAsync();
  return status === "granted";
}

export async function scheduleAllAlarms(): Promise<void> {
  await cancelAllAlarms();
  await setupNotificationChannel();
  for (const schedule of SCHEDULES) {
    await Notifications.scheduleNotificationAsync({
      identifier: schedule.id,
      content: {
        title: schedule.title,
        body: schedule.body,
        sound: "default",
        data: { scheduleId: schedule.id, category: schedule.category },
        ...(Platform.OS === "android" && {
          channelId: CHANNEL_ID,
          color: schedule.color,
          priority: Notifications.AndroidNotificationPriority.HIGH,
        }),
      },
      trigger: {
        type: Notifications.SchedulableTriggerInputTypes.DAILY,
        hour: schedule.hour,
        minute: schedule.minute,
      },
    });
  }
}

export async function cancelAlarm(scheduleId: string): Promise<void> {
  await Notifications.cancelScheduledNotificationAsync(scheduleId);
}

export async function cancelAllAlarms(): Promise<void> {
  for (const schedule of SCHEDULES) {
    try {
      await Notifications.cancelScheduledNotificationAsync(schedule.id);
    } catch (_) {}
  }
}

export async function getActiveAlarmIds(): Promise<Set<string>> {
  const scheduled = await Notifications.getAllScheduledNotificationsAsync();
  const ids = new Set<string>();
  for (const n of scheduled) {
    if (n.identifier) ids.add(n.identifier);
  }
  return ids;
}

export async function toggleAlarm(
  schedule: ScheduleItem,
  currentlyActive: boolean
): Promise<void> {
  if (currentlyActive) {
    await cancelAlarm(schedule.id);
  } else {
    await setupNotificationChannel();
    await Notifications.scheduleNotificationAsync({
      identifier: schedule.id,
      content: {
        title: schedule.title,
        body: schedule.body,
        sound: "default",
        data: { scheduleId: schedule.id, category: schedule.category },
        ...(Platform.OS === "android" && {
          channelId: CHANNEL_ID,
          color: schedule.color,
          priority: Notifications.AndroidNotificationPriority.HIGH,
        }),
      },
      trigger: {
        type: Notifications.SchedulableTriggerInputTypes.DAILY,
        hour: schedule.hour,
        minute: schedule.minute,
      },
    });
  }
}
