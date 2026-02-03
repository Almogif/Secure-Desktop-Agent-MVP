import type { StoredState } from "./types";

const STORAGE_KEY = "flow-v0";

export const loadState = (): StoredState | null => {
  if (typeof window === "undefined") {
    return null;
  }
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return null;
    }
    const parsed = JSON.parse(raw) as StoredState;
    if (typeof parsed.text !== "string" || !Array.isArray(parsed.annotations)) {
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
};

export const saveState = (state: StoredState): void => {
  if (typeof window === "undefined") {
    return;
  }
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    return;
  }
};
