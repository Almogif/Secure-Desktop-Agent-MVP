type CopyMenuProps = {
  onCopyClean: () => void;
  onCopyWithComments: () => void;
};

export default function CopyMenu({ onCopyClean, onCopyWithComments }: CopyMenuProps) {
  return (
    <div className="flex flex-wrap gap-3">
      <button
        type="button"
        className="rounded-full border border-slate-700 px-4 py-2 text-xs uppercase tracking-[0.2em] text-slate-300 hover:border-slate-500 hover:text-slate-100"
        onClick={onCopyClean}
      >
        Copy clean
      </button>
      <button
        type="button"
        className="rounded-full border border-slate-700 px-4 py-2 text-xs uppercase tracking-[0.2em] text-slate-300 hover:border-slate-500 hover:text-slate-100"
        onClick={onCopyWithComments}
      >
        Copy with comments
      </button>
    </div>
  );
}
