// app/(main)/chat.tsx
// ─────────────────────────────────────────────────────────────────────────────
// HeartCare Bot — Connected AI Chat Interface Screen (Real RAG FastAPI)
// Dynamic connection to FastAPI backend (IndoSBERT 768D + Pinecone + Web Search Fallback).
// Senior-friendly UI: large tap targets, high contrast, source attribution pills.
// ─────────────────────────────────────────────────────────────────────────────

import React, { useState, useRef, useCallback } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Animated,
  ActivityIndicator,
  Alert,
} from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { useRouter, useLocalSearchParams } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { StatusBar } from "expo-status-bar";
import { Colors, Typography, Spacing, Radius, Shadows } from "@/constants/theme";

// ── Backend API Config ───────────────────────────────────────────────────────
// Uses EXPO_PUBLIC_AI_API_URL from .env if defined (e.g. http://192.168.100.9:8000)
// Defaults to Android emulator loopback 10.0.2.2 or localhost for web/iOS
const DEFAULT_API_URL =
  Platform.OS === "android" ? "http://10.0.2.2:8000" : "http://localhost:8000";
const AI_API_URL = process.env.EXPO_PUBLIC_AI_API_URL || DEFAULT_API_URL;

// ── Types ─────────────────────────────────────────────────────────────────────
type MessageSender = "bot" | "user";
type SourceType = "rag" | "web_search" | "error";

interface SourceItem {
  title: string;
  type: string;
  url?: string;
  snippet?: string;
  score?: number;
}

interface ChatMessage {
  id: string;
  sender: MessageSender;
  text: string;
  timestamp: Date;
  isTyping?: boolean;
  isError?: boolean;
  sourceType?: SourceType;
  sources?: SourceItem[];
}

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
}

// ── Initial Welcome Messages ──────────────────────────────────────────────────
const INITIAL_MESSAGES: ChatMessage[] = [
  {
    id: "bot-welcome",
    sender: "bot",
    text: "Halo! 👋 Saya HeartCare Bot, asisten pintar perawatan mandiri gagal jantung Anda. Saya terhubung langsung ke basis pengetahuan pedoman klinis (RAG) untuk menjawab pertanyaan seputar cairan, berat badan, garam, dan obat.\n\nApa yang ingin Anda tanyakan?",
    timestamp: new Date(),
    sourceType: "rag",
    sources: [
      {
        title: "Pedoman Tata Laksana Gagal Jantung PERKI",
        type: "document",
      },
    ],
  },
];

function formatTime(date: Date): string {
  return date.toLocaleTimeString("id-ID", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

// ── Source Citation Pill ──────────────────────────────────────────────────────
function SourcePill({
  sourceType,
  sources,
  isError,
}: {
  sourceType?: SourceType;
  sources?: SourceItem[];
  isError?: boolean;
}) {
  if (isError) {
    return (
      <View
        style={[
          styles.sourceBadge,
          {
            backgroundColor: "rgba(239,68,68,0.15)",
            borderColor: "rgba(239,68,68,0.4)",
          },
        ]}
      >
        <Text style={styles.sourceBadgeIcon}>⚠️</Text>
        <Text
          style={[styles.sourceBadgeText, { color: Colors.accentRed }]}
          numberOfLines={1}
        >
          Koneksi Terputus
        </Text>
      </View>
    );
  }

  if (!sourceType || !sources || sources.length === 0) return null;

  const isRag = sourceType === "rag";
  const isWeb = sourceType === "web_search";

  const badgeColor = isRag ? "#22C55E" : "#3B82F6";
  const badgeBg = isRag ? "rgba(34,197,94,0.15)" : "rgba(59,130,246,0.15)";
  const icon = isRag ? "📚" : "🌐";
  const label = isRag
    ? `Sumber: ${sources[0]?.title || "Pedoman Klinis KMS"}`
    : `Pencarian Web: ${sources[0]?.title || "Kemenkes / Inaheart"}`;

  return (
    <View
      style={[
        styles.sourceBadge,
        { backgroundColor: badgeBg, borderColor: `${badgeColor}40` },
      ]}
    >
      <Text style={styles.sourceBadgeIcon}>{icon}</Text>
      <Text
        style={[styles.sourceBadgeText, { color: badgeColor }]}
        numberOfLines={1}
      >
        {label}
      </Text>
    </View>
  );
}

// ── Chat Bubble Component ─────────────────────────────────────────────────────
function ChatBubble({ message }: { message: ChatMessage }) {
  const isBot = message.sender === "bot";
  const isError = message.isError;

  return (
    <View
      style={[
        styles.bubbleRow,
        isBot ? styles.bubbleRowBot : styles.bubbleRowUser,
      ]}
    >
      {isBot && (
        <View
          style={[
            styles.botAvatar,
            isError && { borderColor: Colors.accentRed },
          ]}
        >
          <Text style={styles.botAvatarText}>{isError ? "⚠️" : "❤️"}</Text>
        </View>
      )}

      <View style={styles.bubbleContainer}>
        <Text
          style={[
            styles.senderLabel,
            isBot ? styles.senderLabelBot : styles.senderLabelUser,
            isError && { color: Colors.accentRed },
          ]}
        >
          {isBot ? (isError ? "Sistem / Error" : "HeartCare Bot") : "Anda"}
        </Text>

        {isBot ? (
          <View
            style={[
              styles.bubble,
              styles.bubbleBot,
              isError && styles.bubbleError,
            ]}
          >
            {message.isTyping ? (
              <View style={styles.typingIndicator}>
                <ActivityIndicator size="small" color={Colors.accentBlue} />
                <Text style={styles.typingText}>
                  Menghubungi AI &amp; menganalisis pedoman...
                </Text>
              </View>
            ) : (
              <>
                <Text
                  style={[
                    styles.bubbleText,
                    styles.bubbleTextBot,
                    isError && styles.bubbleTextError,
                  ]}
                >
                  {message.text}
                </Text>
                <SourcePill
                  sourceType={message.sourceType}
                  sources={message.sources}
                  isError={isError}
                />
              </>
            )}
          </View>
        ) : (
          <LinearGradient
            colors={Colors.gradientButton}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={[styles.bubble, styles.bubbleUser]}
          >
            <Text style={[styles.bubbleText, styles.bubbleTextUser]}>
              {message.text}
            </Text>
          </LinearGradient>
        )}

        <Text
          style={[
            styles.timestamp,
            isBot ? styles.timestampBot : styles.timestampUser,
          ]}
        >
          {formatTime(message.timestamp)}
        </Text>
      </View>

      {!isBot && (
        <View style={styles.userAvatar}>
          <Text style={styles.userAvatarText}>👤</Text>
        </View>
      )}
    </View>
  );
}

// ── Quick Suggestion Chips ────────────────────────────────────────────────────
const QUICK_SUGGESTIONS = [
  "Berapa batas minum air sehari?",
  "Kenapa berat badan harus ditimbang tiap pagi?",
  "Berapa batas konsumsi garam?",
  "Apa tanda bahaya gagal jantung?",
];

// ── Main Chat Screen Component ────────────────────────────────────────────────
export default function ChatScreen() {
  const router = useRouter();
  const { patientName } = useLocalSearchParams<{ patientName: string }>();
  const displayName = patientName ?? "Pengguna";

  const [messages, setMessages] = useState<ChatMessage[]>(INITIAL_MESSAGES);
  const [inputText, setInputText] = useState("");
  const [isBotTyping, setIsBotTyping] = useState(false);

  const flatListRef = useRef<FlatList<ChatMessage>>(null);
  const sendBtnScale = useRef(new Animated.Value(1)).current;

  const scrollToBottom = useCallback(() => {
    flatListRef.current?.scrollToEnd({ animated: true });
  }, []);

  const animateSendBtn = (pressed: boolean) => {
    Animated.spring(sendBtnScale, {
      toValue: pressed ? 0.9 : 1,
      useNativeDriver: true,
      speed: 50,
      bounciness: 8,
    }).start();
  };

  const sendMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || isBotTyping) return;

      const userMessage: ChatMessage = {
        id: generateId(),
        sender: "user",
        text: trimmed,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setInputText("");
      setIsBotTyping(true);
      setTimeout(scrollToBottom, 80);

      const typingPlaceholderId = generateId();
      const typingMsg: ChatMessage = {
        id: typingPlaceholderId,
        sender: "bot",
        text: "",
        timestamp: new Date(),
        isTyping: true,
      };

      setMessages((prev) => [...prev, typingMsg]);
      setTimeout(scrollToBottom, 100);

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 25000); // 25s timeout for AI response

      try {
        const historyPayload = messages
          .filter((m) => !m.isError && !m.isTyping)
          .slice(-6)
          .map((m) => ({
            sender: m.sender,
            text: m.text,
          }));

        const response = await fetch(`${AI_API_URL}/chat`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
          body: JSON.stringify({
            message: trimmed,
            patient_name: displayName,
            conversation_history: historyPayload,
          }),
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          const errorData = await response.json().catch(() => null);
          const errorDetail =
            errorData?.detail || `Server merespons dengan status HTTP ${response.status}`;
          throw new Error(errorDetail);
        }

        const data = await response.json();

        const botReplyMessage: ChatMessage = {
          id: generateId(),
          sender: "bot",
          text: data.reply || "Maaf, tidak ada respons yang diterima dari model AI.",
          timestamp: new Date(),
          sourceType: data.source_type,
          sources: data.sources,
        };

        setMessages((prev) =>
          prev.filter((m) => m.id !== typingPlaceholderId).concat(botReplyMessage)
        );
      } catch (err: any) {
        clearTimeout(timeoutId);
        console.error("[Chat API Error]:", err);

        const isTimeout = err?.name === "AbortError";
        const errorText = isTimeout
          ? `⏱️ Batas waktu permintaan habis (Timeout 25s).\nServer AI di ${AI_API_URL} tidak merespons tepat waktu.`
          : `⚠️ Gagal terhubung ke Server AI Medis (${AI_API_URL}).\n\nPastikan:\n1. Server FastAPI sudah berjalan di port 8000.\n2. Variabel EXPO_PUBLIC_AI_API_URL di file .env sesuai dengan IP Wi-Fi laptop Anda.\n3. HP dan Laptop terhubung ke jaringan Wi-Fi yang sama.`;

        const errorReplyMessage: ChatMessage = {
          id: generateId(),
          sender: "bot",
          text: errorText,
          timestamp: new Date(),
          isError: true,
          sourceType: "error",
        };

        setMessages((prev) =>
          prev.filter((m) => m.id !== typingPlaceholderId).concat(errorReplyMessage)
        );
      } finally {
        setIsBotTyping(false);
        setTimeout(scrollToBottom, 120);
      }
    },
    [isBotTyping, messages, displayName, scrollToBottom]
  );

  const handleQuickSuggestion = (suggestion: string) => {
    sendMessage(suggestion);
  };

  const handleClearChat = () => {
    Alert.alert(
      "Hapus Percakapan",
      "Apakah Anda yakin ingin menghapus seluruh riwayat percakapan ini?",
      [
        { text: "Batal", style: "cancel" },
        {
          text: "Hapus",
          style: "destructive",
          onPress: () => setMessages(INITIAL_MESSAGES),
        },
      ]
    );
  };

  return (
    <LinearGradient
      colors={Colors.gradientHero}
      locations={[0, 0.5, 1]}
      style={styles.container}
    >
      <StatusBar style="light" />
      <SafeAreaView style={styles.safeArea} edges={["top"]}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.backBtn}
            onPress={() => router.back()}
            accessibilityLabel="Kembali ke Beranda"
            accessibilityRole="button"
          >
            <Text style={styles.backBtnText}>‹</Text>
          </TouchableOpacity>

          <View style={styles.headerCenter}>
            <Text style={styles.headerTitle}>HeartCare Bot</Text>
            <View style={styles.onlineBadge}>
              <View style={styles.onlineDot} />
              <Text style={styles.onlineText}>AI Klinis Aktif (RAG)</Text>
            </View>
          </View>

          <TouchableOpacity
            style={styles.clearBtn}
            onPress={handleClearChat}
            accessibilityLabel="Hapus riwayat chat"
            accessibilityRole="button"
          >
            <Text style={styles.clearBtnText}>Hapus</Text>
          </TouchableOpacity>
        </View>

        <KeyboardAvoidingView
          style={styles.chatArea}
          behavior={Platform.OS === "ios" ? "padding" : undefined}
          keyboardVerticalOffset={Platform.OS === "ios" ? 10 : 0}
        >
          <FlatList
            ref={flatListRef}
            data={messages}
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => <ChatBubble message={item} />}
            contentContainerStyle={styles.messageList}
            onContentSizeChange={scrollToBottom}
            showsVerticalScrollIndicator={false}
          />

          {/* Quick Suggestions */}
          <View style={styles.suggestionsContainer}>
            <FlatList
              horizontal
              showsHorizontalScrollIndicator={false}
              data={QUICK_SUGGESTIONS}
              keyExtractor={(item) => item}
              contentContainerStyle={styles.suggestionsList}
              renderItem={({ item }) => (
                <TouchableOpacity
                  style={styles.suggestionChip}
                  onPress={() => handleQuickSuggestion(item)}
                  activeOpacity={0.8}
                >
                  <Text style={styles.suggestionText}>{item}</Text>
                </TouchableOpacity>
              )}
            />
          </View>

          {/* Input Bar */}
          <View style={styles.inputContainer}>
            <TextInput
              style={styles.input}
              placeholder="Ketik pertanyaan kesehatan jantung..."
              placeholderTextColor={Colors.textMuted}
              value={inputText}
              onChangeText={setInputText}
              multiline
              maxLength={500}
              accessibilityLabel="Kolom pesan"
            />
            <Animated.View style={{ transform: [{ scale: sendBtnScale }] }}>
              <TouchableOpacity
                style={[
                  styles.sendBtn,
                  (!inputText.trim() || isBotTyping) && styles.sendBtnDisabled,
                ]}
                onPressIn={() => animateSendBtn(true)}
                onPressOut={() => animateSendBtn(false)}
                onPress={() => sendMessage(inputText)}
                disabled={!inputText.trim() || isBotTyping}
                accessibilityLabel="Kirim pesan"
                accessibilityRole="button"
              >
                <Text style={styles.sendBtnText}>➤</Text>
              </TouchableOpacity>
            </Animated.View>
          </View>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: { flex: 1 },
  header: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: Colors.borderGlass,
  },
  backBtn: {
    width: 44,
    height: 44,
    borderRadius: Radius.full,
    backgroundColor: Colors.bgSecondary,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: Colors.borderGlass,
  },
  backBtnText: {
    fontSize: 28,
    color: Colors.textPrimary,
    lineHeight: 32,
    fontWeight: "bold",
  },
  headerCenter: { flex: 1, alignItems: "center" },
  headerTitle: {
    fontFamily: Typography.fontFamily.bold,
    fontSize: Typography.size.lg,
    color: Colors.textPrimary,
  },
  onlineBadge: {
    flexDirection: "row",
    alignItems: "center",
    gap: 5,
    marginTop: 2,
  },
  onlineDot: {
    width: 7,
    height: 7,
    borderRadius: Radius.full,
    backgroundColor: Colors.accentGreen,
  },
  onlineText: {
    fontFamily: Typography.fontFamily.medium,
    fontSize: 11,
    color: Colors.accentGreen,
  },
  clearBtn: {
    paddingVertical: Spacing.xs,
    paddingHorizontal: Spacing.md,
    borderRadius: Radius.full,
    backgroundColor: Colors.bgGlass,
    borderWidth: 1,
    borderColor: Colors.borderGlass,
  },
  clearBtnText: {
    fontFamily: Typography.fontFamily.medium,
    fontSize: Typography.size.xs,
    color: Colors.textSecondary,
  },
  chatArea: { flex: 1 },
  messageList: {
    paddingHorizontal: Spacing.lg,
    paddingTop: Spacing.md,
    paddingBottom: Spacing.md,
  },
  bubbleRow: {
    flexDirection: "row",
    alignItems: "flex-end",
    marginBottom: Spacing.md,
    gap: Spacing.sm,
  },
  bubbleRowBot: { justifyContent: "flex-start" },
  bubbleRowUser: { justifyContent: "flex-end" },
  botAvatar: {
    width: 36,
    height: 36,
    borderRadius: Radius.full,
    backgroundColor: Colors.accentRedPale,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: "rgba(239,68,68,0.3)",
    marginBottom: 18,
  },
  botAvatarText: { fontSize: 18 },
  userAvatar: {
    width: 36,
    height: 36,
    borderRadius: Radius.full,
    backgroundColor: Colors.accentBluePale,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: "rgba(59,130,246,0.3)",
    marginBottom: 18,
  },
  userAvatarText: { fontSize: 18 },
  bubbleContainer: { maxWidth: "80%" },
  senderLabel: {
    fontFamily: Typography.fontFamily.semiBold,
    fontSize: 11,
    marginBottom: 3,
  },
  senderLabelBot: { color: Colors.accentBlue, marginLeft: Spacing.xs },
  senderLabelUser: {
    color: Colors.textMuted,
    textAlign: "right",
    marginRight: Spacing.xs,
  },
  bubble: {
    borderRadius: Radius.xl,
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
    minWidth: 80,
  },
  bubbleBot: {
    backgroundColor: Colors.bgSecondary,
    borderWidth: 1,
    borderColor: Colors.borderGlass,
    borderBottomLeftRadius: 4,
  },
  bubbleError: {
    backgroundColor: "rgba(239,68,68,0.12)",
    borderColor: "rgba(239,68,68,0.4)",
  },
  bubbleUser: {
    borderBottomRightRadius: 4,
  },
  bubbleText: {
    fontFamily: Typography.fontFamily.regular,
    fontSize: 17,
    lineHeight: 24,
  },
  bubbleTextBot: { color: Colors.textPrimary },
  bubbleTextError: { color: "#FCA5A5" },
  bubbleTextUser: { color: "#FFFFFF", fontWeight: "500" },
  timestamp: {
    fontFamily: Typography.fontFamily.regular,
    fontSize: 10,
    marginTop: 4,
  },
  timestampBot: { color: Colors.textMuted, marginLeft: Spacing.xs },
  timestampUser: {
    color: Colors.textMuted,
    textAlign: "right",
    marginRight: Spacing.xs,
  },
  typingIndicator: {
    flexDirection: "row",
    alignItems: "center",
    gap: Spacing.sm,
    paddingVertical: Spacing.xs,
  },
  typingText: {
    fontFamily: Typography.fontFamily.medium,
    fontSize: Typography.size.xs,
    color: Colors.accentBlue,
  },
  sourceBadge: {
    flexDirection: "row",
    alignItems: "center",
    gap: 5,
    marginTop: 8,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: Radius.sm,
    borderWidth: 1,
    alignSelf: "flex-start",
  },
  sourceBadgeIcon: { fontSize: 12 },
  sourceBadgeText: {
    fontFamily: Typography.fontFamily.semiBold,
    fontSize: 11,
    maxWidth: 220,
  },
  suggestionsContainer: {
    paddingVertical: Spacing.xs,
    backgroundColor: "transparent",
  },
  suggestionsList: {
    paddingHorizontal: Spacing.lg,
    gap: Spacing.sm,
  },
  suggestionChip: {
    backgroundColor: Colors.bgSecondary,
    borderRadius: Radius.full,
    paddingVertical: 7,
    paddingHorizontal: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.borderGlass,
  },
  suggestionText: {
    fontFamily: Typography.fontFamily.medium,
    fontSize: Typography.size.xs,
    color: Colors.accentBlue,
  },
  inputContainer: {
    flexDirection: "row",
    alignItems: "flex-end",
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
    gap: Spacing.sm,
    borderTopWidth: 1,
    borderTopColor: Colors.borderGlass,
    backgroundColor: Colors.bgPrimary,
  },
  input: {
    flex: 1,
    backgroundColor: Colors.bgSecondary,
    borderRadius: Radius.lg,
    paddingHorizontal: Spacing.md,
    paddingVertical: Platform.OS === "ios" ? Spacing.md : Spacing.sm,
    color: Colors.textPrimary,
    fontFamily: Typography.fontFamily.regular,
    fontSize: Typography.size.body,
    maxHeight: 100,
    borderWidth: 1,
    borderColor: Colors.borderGlass,
  },
  sendBtn: {
    width: 48,
    height: 48,
    borderRadius: Radius.full,
    backgroundColor: Colors.accentBlue,
    alignItems: "center",
    justifyContent: "center",
    ...Shadows.button,
  },
  sendBtnDisabled: {
    backgroundColor: Colors.bgTertiary,
  },
  sendBtnText: {
    color: "#FFFFFF",
    fontSize: 18,
    fontWeight: "bold",
  },
});
