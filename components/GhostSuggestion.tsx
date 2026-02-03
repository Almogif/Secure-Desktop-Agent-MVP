type GhostSuggestionProps = {
  text: string;
};

export default function GhostSuggestion({ text }: GhostSuggestionProps) {
  if (!text) {
    return null;
  }

  return <span className="text-slate-500">{text}</span>;
}
