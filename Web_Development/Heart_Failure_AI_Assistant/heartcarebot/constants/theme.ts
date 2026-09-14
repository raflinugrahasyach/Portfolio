// constants/theme.ts
// ─────────────────────────────────────────────────────────────────────────────
// HeartCare Bot — Design System
// Modern Industrial Minimalism × Swiss Style
// High-contrast palette for elderly accessibility (WCAG AA+)
// ─────────────────────────────────────────────────────────────────────────────

export const Colors = {
  // ── Backgrounds ──────────────────────────────────────────────────────────
  bgPrimary: '#0A0F1E',        // Deep navy-black
  bgSecondary: '#111827',      // Card background
  bgTertiary: '#1C2333',       // Input fields, secondary cards
  bgGlass: 'rgba(255,255,255,0.06)',  // Glassmorphism layer

  // ── Brand / Primary ───────────────────────────────────────────────────────
  accentBlue: '#3B82F6',       // Electric blue — primary actions
  accentBlueDark: '#2563EB',   // Pressed state
  accentBluePale: 'rgba(59,130,246,0.15)', // Subtle highlights

  accentRed: '#EF4444',        // Heart / critical alerts
  accentRedPale: 'rgba(239,68,68,0.12)',

  accentGreen: '#22C55E',      // Success / online status
  accentGreenPale: 'rgba(34,197,94,0.12)',

  accentAmber: '#F59E0B',      // Warning / schedule
  accentAmberPale: 'rgba(245,158,11,0.12)',

  // ── Text ─────────────────────────────────────────────────────────────────
  textPrimary: '#F8FAFC',      // White-ish — main body text (≥4.5:1)
  textSecondary: '#CBD5E1',    // Subtitles, captions (≥4.5:1 on bgSecondary)
  textMuted: '#94A3B8',        // Timestamps, hints
  textOnAccent: '#FFFFFF',     // Text on coloured buttons

  // ── Borders & Dividers ────────────────────────────────────────────────────
  borderGlass: 'rgba(255,255,255,0.12)',
  borderStrong: 'rgba(255,255,255,0.20)',
  divider: 'rgba(255,255,255,0.08)',

  // ── Gradients (linear stops) ─────────────────────────────────────────────
  gradientHero: ['#0A0F1E', '#0D1B3E', '#0A0F1E'] as const,
  gradientCard: ['rgba(59,130,246,0.15)', 'rgba(59,130,246,0.03)'] as const,
  gradientButton: ['#3B82F6', '#2563EB'] as const,
  gradientDanger: ['#EF4444', '#DC2626'] as const,
  gradientAmber: ['#F59E0B', '#D97706'] as const,
} as const;

export const Typography = {
  // ── Font Family (loaded via expo-font + @expo-google-fonts/inter) ─────────
  fontFamily: {
    regular: 'Inter_400Regular',
    medium: 'Inter_500Medium',
    semiBold: 'Inter_600SemiBold',
    bold: 'Inter_700Bold',
    extraBold: 'Inter_800ExtraBold',
  },

  // ── Font Sizes — all ≥ 18px for elderly accessibility ─────────────────────
  size: {
    xs: 14,        // Timestamps only
    sm: 16,        // Small labels (use sparingly)
    body: 18,      // Minimum body text (RULE: never go below this)
    lg: 20,        // Card descriptions, secondary info
    xl: 24,        // Section headers
    xxl: 30,       // Page titles
    xxxl: 38,      // Hero numbers / display
    display: 48,   // Full-screen display text
  },

  // ── Line Heights ──────────────────────────────────────────────────────────
  lineHeight: {
    tight: 1.2,
    normal: 1.55,
    relaxed: 1.75,
  },

  // ── Letter Spacing ────────────────────────────────────────────────────────
  tracking: {
    tighter: -0.5,
    normal: 0,
    wider: 0.5,
    widest: 1.5,
  },
} as const;

export const Spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
  xxxl: 64,
} as const;

export const Radius = {
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  full: 9999,
} as const;

export const Shadows = {
  card: {
    shadowColor: '#3B82F6',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.18,
    shadowRadius: 20,
    elevation: 8,
  },
  button: {
    shadowColor: '#3B82F6',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.30,
    shadowRadius: 16,
    elevation: 12,
  },
  glow: {
    shadowColor: '#3B82F6',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.50,
    shadowRadius: 24,
    elevation: 16,
  },
} as const;
