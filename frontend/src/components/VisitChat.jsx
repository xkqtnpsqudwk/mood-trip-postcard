import { useState } from "react";
import { sendPlaceChatMessage } from "../api";
import { useLanguage } from "../LanguageContext";

const localized = (value, lang) => {
  if (value && typeof value === "object") {
    return value[lang] ?? value.en ?? value.ko ?? "";
  }
  return value ?? "";
};

export default function VisitChat({
  city,
  place,
  moodText,
  clue,
  messages,
  onMessagesChange,
  onVisited,
  onBack,
}) {
  const { t, lang } = useLanguage();
  const placeName = localized(place.name_i18n, lang) || place.name;
  const visibleMessages =
    messages.length > 0 ? messages : [{ role: "assistant", content: t.visitChat.initial() }];
  const [draft, setDraft] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    const content = draft.trim();
    if (!content || isSending) return;

    const nextMessages = [...visibleMessages, { role: "user", content }];
    onMessagesChange(nextMessages);
    setDraft("");
    setError("");
    setIsSending(true);
    try {
      const response = await sendPlaceChatMessage({
        city,
        place,
        moodText,
        clue,
        messages: nextMessages.filter((message) => message.role !== "assistant" || message.content),
        language: lang,
      });
      onMessagesChange([...nextMessages, { role: "assistant", content: response.reply }]);
    } catch {
      setError(t.visitChat.error);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="mx-auto w-full max-w-3xl pb-[calc(6rem+env(safe-area-inset-bottom))]">
      <section className="rounded-3xl bg-white/90 p-5 shadow-[0_24px_60px_-18px_rgba(251,113,133,0.38)] ring-1 ring-rose-100/80 sm:p-6 dark:bg-zinc-950/70 dark:shadow-[0_0_36px_rgba(217,70,239,0.16)] dark:ring-fuchsia-500/20">
        <div className="flex flex-col gap-2 border-b border-rose-100 pb-4 dark:border-fuchsia-500/20">
          <p className="text-xs font-semibold uppercase tracking-widest text-rose-400 dark:text-fuchsia-300">
            {t.visitChat.eyebrow}
          </p>
          <h2 className="font-[family-name:var(--font-display)] text-2xl text-stone-800 dark:text-zinc-100">
            {t.visitChat.heading(placeName)}
          </h2>
          <p className="text-sm leading-relaxed text-stone-500 dark:text-zinc-400">
            {t.visitChat.subheading}
          </p>
        </div>

        <div className="mt-5 flex max-h-[420px] flex-col gap-3 overflow-y-auto pr-1">
          {visibleMessages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={`max-w-[86%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                message.role === "user"
                  ? "ml-auto bg-rose-400 text-white shadow-[0_8px_20px_-8px_rgba(251,113,133,0.8)] dark:bg-fuchsia-500"
                  : "bg-rose-50 text-stone-600 ring-1 ring-rose-100 dark:bg-zinc-900/80 dark:text-zinc-200 dark:ring-fuchsia-500/20"
              }`}
            >
              {message.content}
            </div>
          ))}
          {isSending && (
            <div className="max-w-[86%] rounded-2xl bg-rose-50 px-4 py-3 text-sm text-stone-400 ring-1 ring-rose-100 dark:bg-zinc-900/80 dark:text-zinc-500 dark:ring-fuchsia-500/20">
              {t.visitChat.loading}
            </div>
          )}
        </div>

        {error && (
          <p className="mt-4 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-500 dark:bg-fuchsia-950/40 dark:text-fuchsia-300 dark:ring-1 dark:ring-fuchsia-500/30">
            {error}
          </p>
        )}

        <form onSubmit={handleSubmit} className="mt-5 flex flex-col gap-3 sm:flex-row">
          <input
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder={t.visitChat.placeholder}
            className="min-h-12 flex-1 rounded-2xl border border-rose-100 bg-white px-4 text-sm text-stone-700 outline-none transition placeholder:text-stone-300 focus:border-rose-300 focus:ring-4 focus:ring-rose-100 dark:border-fuchsia-500/20 dark:bg-zinc-950 dark:text-zinc-100 dark:placeholder:text-zinc-600 dark:focus:border-fuchsia-400 dark:focus:ring-fuchsia-500/15"
          />
          <button
            type="submit"
            disabled={isSending || !draft.trim()}
            className="rounded-2xl bg-rose-400 px-5 py-3 text-sm font-semibold text-white shadow-[0_8px_20px_-6px_rgba(251,113,133,0.65)] transition hover:bg-rose-500 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-fuchsia-500 dark:hover:bg-fuchsia-400"
          >
            {t.visitChat.send}
          </button>
        </form>

        <div className="mt-5 grid gap-3 sm:grid-cols-2">
          <button
            onClick={onBack}
            className="rounded-xl border border-stone-200 px-4 py-2.5 text-sm font-medium text-stone-500 hover:bg-stone-50 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-900"
          >
            {t.visitChat.back}
          </button>
          <button
            onClick={onVisited}
            className="rounded-xl bg-rose-400 px-4 py-2.5 text-sm font-semibold text-white shadow-[0_8px_20px_-4px_rgba(251,113,133,0.5)] transition hover:bg-rose-500 dark:bg-fuchsia-500 dark:hover:bg-fuchsia-400"
          >
            {t.visitChat.visited}
          </button>
        </div>
      </section>
    </div>
  );
}
