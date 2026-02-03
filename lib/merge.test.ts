import { describe, expect, it } from "vitest";

import { prepareSuggestion } from "./merge";

describe("prepareSuggestion", () => {
  it("adds a missing space when needed", () => {
    const result = prepareSuggestion("andhow", "the story ends.");
    expect(result?.merged).toBe("andhow the story ends.");
  });

  it("avoids double spaces", () => {
    const result = prepareSuggestion("Hello ", " world");
    expect(result?.merged).toBe("Hello world");
  });

  it("merges mid-word completions without adding a space", () => {
    const result = prepareSuggestion("bro", "thers are here.");
    expect(result?.merged).toBe("brothers are here.");
  });
});
