import { useState } from "react";

type AnnotationPopoverProps = {
  x: number;
  y: number;
  onSave: (note: string) => void;
  onCancel: () => void;
};

export default function AnnotationPopover({ x, y, onSave, onCancel }: AnnotationPopoverProps) {
  const [note, setNote] = useState("");

  return (
    <div
      className="fixed z-20 w-64 rounded-lg border border-slate-700 bg-slate-900 p-3 shadow-xl"
      style={{ left: x, top: y }}
      role="dialog"
      aria-label="Add annotation"
    >
      <label className="text-xs uppercase tracking-wide text-slate-400">Note</label>
      <textarea
        className="mt-2 w-full resize-none rounded-md border border-slate-700 bg-slate-950 p-2 text-sm text-slate-100 focus:border-slate-500 focus:outline-none"
        rows={3}
        value={note}
        onChange={(event) => setNote(event.target.value)}
      />
      <div className="mt-3 flex items-center justify-end gap-2">
        <button
          type="button"
          className="rounded-md px-3 py-1 text-xs uppercase tracking-wide text-slate-400 hover:text-slate-200"
          onClick={onCancel}
        >
          Cancel
        </button>
        <button
          type="button"
          className="rounded-md bg-slate-200 px-3 py-1 text-xs uppercase tracking-wide text-slate-900"
          onClick={() => onSave(note.trim())}
        >
          Save
        </button>
      </div>
    </div>
  );
}
