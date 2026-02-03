const MAX_LENGTH = 200;

const sanitizeSuggestion = (raw: string, contextText: string): string | null => {
  const compact = raw.replace(/[\r\n]+/g, " ").trim();
  if (!compact) {
    return null;
  }
  if (compact.length > MAX_LENGTH) {
    return null;
  }
  if (/["“”]/.test(compact)) {
    return null;
  }
  const sentenceEndings = (compact.match(/[.!?]/g) ?? []).length;
  if (sentenceEndings > 1) {
    return null;
  }
  if (contextText.trim().endsWith(compact)) {
    return null;
  }
  if (contextText.includes(compact)) {
    return null;
  }
  return compact;
};

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as { contextText?: string };
    const contextText = body.contextText?.slice(-300) ?? "";

    if (!contextText.trim()) {
      return Response.json({ suggestion: null });
    }

    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      return Response.json({ suggestion: null });
    }

    const prompt = `You are a quiet writing assistant. Continue the user's text with ONE concise sentence.\nRules: respond with only the continuation text, no quotes, no explanations. Keep it short.\nText: ${contextText}`;

    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents: [{ role: "user", parts: [{ text: prompt }] }],
          generationConfig: { maxOutputTokens: 120, temperature: 0.6 }
        })
      }
    );

    if (!response.ok) {
      return Response.json({ suggestion: null });
    }

    const data = (await response.json()) as {
      candidates?: Array<{ content?: { parts?: Array<{ text?: string }> } }>;
    };
    const responseText = data.candidates?.[0]?.content?.parts?.[0]?.text ?? "";
    const suggestion = sanitizeSuggestion(responseText, contextText);

    return Response.json({ suggestion });
  } catch {
    return Response.json({ suggestion: null });
  }
}
