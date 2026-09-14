// utils/session.ts
// ─────────────────────────────────────────────────────────────────────────────
// HeartCare Bot — Session Management
// Uses expo-secure-store for encrypted, device-local session persistence.
// Stage 1: One-time login (no token expiry, no server validation).
// ─────────────────────────────────────────────────────────────────────────────

import * as SecureStore from 'expo-secure-store';

const SESSION_KEY = 'heartcare_user_session';

export interface UserSession {
  patientName: string;
  loginTimestamp: number;
  sessionId: string;
}

/**
 * Generates a simple pseudo-unique session ID for Stage 1.
 * (Stage 4 will replace this with a proper UUID/server-issued token.)
 */
function generateSessionId(): string {
  return `${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
}

/**
 * Save a new user session to secure storage.
 * Called once after the user submits the login form.
 */
export async function saveSession(patientName: string): Promise<UserSession> {
  const session: UserSession = {
    patientName: patientName.trim(),
    loginTimestamp: Date.now(),
    sessionId: generateSessionId(),
  };

  try {
    await SecureStore.setItemAsync(SESSION_KEY, JSON.stringify(session));
  } catch (error) {
    // Fallback: log but don't crash. In Stage 4, surface this error to user.
    console.error('[Session] Failed to save session:', error);
  }

  return session;
}

/**
 * Retrieve the stored session. Returns null if no session exists.
 * Called on app startup to determine whether to show Login or Dashboard.
 */
export async function getSession(): Promise<UserSession | null> {
  try {
    const raw = await SecureStore.getItemAsync(SESSION_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as UserSession;
  } catch (error) {
    console.error('[Session] Failed to read session:', error);
    return null;
  }
}

/**
 * Clear the stored session. Used for logout functionality (Stage 2+).
 */
export async function clearSession(): Promise<void> {
  try {
    await SecureStore.deleteItemAsync(SESSION_KEY);
  } catch (error) {
    console.error('[Session] Failed to clear session:', error);
  }
}
