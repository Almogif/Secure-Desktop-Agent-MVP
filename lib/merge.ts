const COMMON_SHORT_WORDS = new Set([
  "a",
  "an",
  "and",
  "are",
  "as",
  "at",
  "be",
  "but",
  "by",
  "do",
  "for",
  "from",
  "had",
  "has",
  "have",
  "he",
  "her",
  "his",
  "how",
  "if",
  "in",
  "is",
  "it",
  "its",
  "me",
  "my",
  "no",
  "not",
  "of",
  "on",
  "or",
  "our",
  "she",
  "so",
  "that",
  "the",
  "their",
  "them",
  "they",
  "to",
  "us",
  "was",
  "we",
  "were",
  "with",
  "you",
  "your"
]);

const wordCharRegex = /[A-Za-z0-9]/;

const endsWithWordChar = (value: string): boolean => wordCharRegex.test(value.slice(-1));
const startsWithWordChar = (value: string): boolean => wordCharRegex.test(value[0] ?? "");

const getLastWord = (value: string): string => {
  const match = value.match(/([A-Za-z0-9]+)$/);
  return match ? match[1] : "";
};

const isMidWord = (value: string): boolean => {
  const lastWord = getLastWord(value).toLowerCase();
  if (!lastWord) {
    return false;
  }
  if (COMMON_SHORT_WORDS.has(lastWord)) {
    return false;
  }
  return lastWord.length <= 3;
};

const stripLeadingSpaces = (value: string): string => value.replace(/^\s+/, "");

export type MergeResult = {
  merged: string;
  ghost: string;
};

export const prepareSuggestion = (base: string, suggestion: string): MergeResult | null => {
  const trimmed = suggestion.replace(/\s+$/g, "");
  if (!trimmed) {
    return null;
  }

  const baseEndsWithSpace = /\s$/.test(base);
  const suggestionStartsWithSpace = /^\s/.test(trimmed);
  const baseEndsWithWord = endsWithWordChar(base);
  const suggestionStartsWithWord = startsWithWordChar(trimmed);

  let prefix = "";
  let normalized = trimmed;

  if (baseEndsWithSpace) {
    normalized = stripLeadingSpaces(trimmed);
  } else if (baseEndsWithWord && suggestionStartsWithWord) {
    prefix = isMidWord(base) ? "" : " ";
  } else if (!baseEndsWithSpace && !suggestionStartsWithSpace && base.length > 0) {
    prefix = " ";
  } else if (!baseEndsWithSpace && suggestionStartsWithSpace) {
    normalized = stripLeadingSpaces(trimmed);
  }

  if (prefix && normalized.startsWith(" ")) {
    normalized = stripLeadingSpaces(normalized);
  }

  const ghost = `${prefix}${normalized}`;
  const merged = `${base}${ghost}`;

  return {
    merged,
    ghost
  };
};
