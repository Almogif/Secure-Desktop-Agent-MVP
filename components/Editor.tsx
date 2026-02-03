"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { prepareSuggestion } from "../lib/merge";
import type { Annotation } from "../lib/types";
import { loadState, saveState } from "../lib/storage";
import AnnotationPopover from "./AnnotationPopover";
import CopyMenu from "./CopyMenu";
import GhostSuggestion from "./GhostSuggestion";

const SUGGESTION_DELAY_MS = 700;
const CONTEXT_WINDOW = 300;

const clampAnnotations = (text: string, annotations: Annotation[]): Annotation[] =>
  annotations.filter((annotation) => annotation.start < annotation.end && annotation.end <= text.length);

type PopoverState = {
  x: number;
  y: number;
  start: number;
  end: number;
};

export default function Editor() {
  const [text, setText] = useState("");
  const [annotations, setAnnotations] = useState<Annotation[]>([]);
  const [suggestion, setSuggestion] = useState<string | null>(null);
  const [ghostText, setGhostText] = useState("");
  const [popover, setPopover] = useState<PopoverState | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const overlayRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const stored = loadState();
    if (stored) {
      setText(stored.text);
      setAnnotations(stored.annotations);
    }
  }, []);

  useEffect(() => {
    saveState({ text, annotations });
  }, [text, annotations]);

  useEffect(() => {
    setSuggestion(null);
    setGhostText("");
    if (!text.trim()) {
      return;
    }

    const handle = window.setTimeout(async () => {
      try {
        const contextText = text.slice(-CONTEXT_WINDOW);
        const response = await fetch("/api/suggest", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ contextText })
        });

        if (!response.ok) {
          setSuggestion(null);
          setGhostText("");
          return;
        }

        const data = (await response.json()) as { suggestion: string | null };
        if (!data.suggestion) {
          setSuggestion(null);
          setGhostText("");
          return;
        }

        const prepared = prepareSuggestion(text, data.suggestion);
        if (!prepared) {
          setSuggestion(null);
          setGhostText("");
          return;
        }

        setSuggestion(data.suggestion);
        setGhostText(prepared.ghost);
      } catch {
        setSuggestion(null);
        setGhostText("");
      }
    }, SUGGESTION_DELAY_MS);

    return () => window.clearTimeout(handle);
  }, [text]);

  const annotatedSegments = useMemo(() => {
    const safeAnnotations = clampAnnotations(text, annotations).sort((a, b) => a.start - b.start);
    const segments: Array<{ text: string; annotation?: Annotation }> = [];
    let cursor = 0;

    safeAnnotations.forEach((annotation) => {
      if (annotation.start > cursor) {
        segments.push({ text: text.slice(cursor, annotation.start) });
      }
      segments.push({ text: text.slice(annotation.start, annotation.end), annotation });
      cursor = annotation.end;
    });

    if (cursor < text.length) {
      segments.push({ text: text.slice(cursor) });
    }

    return segments;
  }, [text, annotations]);

  const handleAcceptSuggestion = useCallback(() => {
    if (!suggestion) {
      return;
    }
    const prepared = prepareSuggestion(text, suggestion);
    if (!prepared) {
      setSuggestion(null);
      setGhostText("");
      return;
    }
    setText(prepared.merged);
    setSuggestion(null);
    setGhostText("");

    requestAnimationFrame(() => {
      const textarea = textareaRef.current;
      if (textarea) {
        textarea.selectionStart = prepared.merged.length;
        textarea.selectionEnd = prepared.merged.length;
      }
    });
  }, [suggestion, text]);

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Tab" && suggestion) {
      event.preventDefault();
      handleAcceptSuggestion();
      return;
    }
    if (event.key === "Escape" && suggestion) {
      event.preventDefault();
      setSuggestion(null);
      setGhostText("");
    }
  };

  const handleChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(event.target.value);
    setSuggestion(null);
    setGhostText("");
  };

  const handleContextMenu = (event: React.MouseEvent<HTMLTextAreaElement>) => {
    const textarea = event.currentTarget;
    const start = textarea.selectionStart ?? 0;
    const end = textarea.selectionEnd ?? 0;
    if (start === end) {
      return;
    }
    event.preventDefault();
    setPopover({ x: event.clientX, y: event.clientY, start, end });
  };

  const handleScroll = (event: React.UIEvent<HTMLTextAreaElement>) => {
    if (overlayRef.current) {
      overlayRef.current.scrollTop = event.currentTarget.scrollTop;
      overlayRef.current.scrollLeft = event.currentTarget.scrollLeft;
    }
  };

  const handleSaveAnnotation = (note: string) => {
    if (!popover) {
      return;
    }
    if (!note) {
      setPopover(null);
      return;
    }
    const newAnnotation: Annotation = {
      id: `${Date.now()}-${popover.start}-${popover.end}`,
      start: popover.start,
      end: popover.end,
      note
    };
    setAnnotations((prev) => [...prev, newAnnotation]);
    setPopover(null);
  };

  const handleCopyClean = async () => {
    await navigator.clipboard.writeText(text);
  };

  const handleCopyWithComments = async () => {
    const safeAnnotations = clampAnnotations(text, annotations);
    const metaLines = safeAnnotations.map((annotation) => {
      const anchor = text.slice(annotation.start, annotation.end);
      return `• “${anchor}” → ${annotation.note}`;
    });

    const output =
      metaLines.length > 0
        ? `${text}\n\n---\nMeta:\n${metaLines.join("\n")}`
        : text;

    await navigator.clipboard.writeText(output);
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="rounded-3xl border border-slate-800 bg-slate-950/80 p-6">
        <div className="relative min-h-[360px] text-base leading-relaxed">
          <div
            ref={overlayRef}
            className="pointer-events-none absolute inset-0 whitespace-pre-wrap break-words text-slate-100"
            aria-hidden="true"
          >
            {annotatedSegments.map((segment, index) => (
              <span key={`${segment.text}-${index}`}>
                {segment.annotation ? (
                  <span className="font-semibold text-red-400">
                    {segment.text}
                    <span className="ml-1 align-top text-xs font-normal text-slate-400">
                      {segment.annotation.note}
                    </span>
                  </span>
                ) : (
                  <span>{segment.text}</span>
                )}
              </span>
            ))}
            <GhostSuggestion text={ghostText} />
          </div>
          <textarea
            ref={textareaRef}
            className="relative z-10 h-full min-h-[360px] w-full resize-none bg-transparent text-transparent caret-slate-100 outline-none placeholder:text-slate-600"
            value={text}
            placeholder="Start writing..."
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            onContextMenu={handleContextMenu}
            onScroll={handleScroll}
            spellCheck={false}
          />
        </div>
      </div>
      <CopyMenu onCopyClean={handleCopyClean} onCopyWithComments={handleCopyWithComments} />
      {popover ? (
        <AnnotationPopover
          x={popover.x}
          y={popover.y}
          onSave={handleSaveAnnotation}
          onCancel={() => setPopover(null)}
        />
      ) : null}
    </div>
  );
}
