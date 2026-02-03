import Editor from "../components/Editor";

export default function HomePage() {
  return (
    <div className="mx-auto flex w-full max-w-4xl flex-col gap-6">
      <header className="text-sm uppercase tracking-[0.3em] text-slate-400">
        Flow
      </header>
      <Editor />
    </div>
  );
}
