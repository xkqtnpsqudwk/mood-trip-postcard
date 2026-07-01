import { useState } from "react";
import { useLanguage } from "../LanguageContext";

export default function PostcardCreator({ place, city, onSubmit, onCancel, isLoading }) {
  const { t } = useLanguage();
  const [review, setReview] = useState("");

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!review.trim() || isLoading) return;
    onSubmit(review.trim());
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="mx-auto w-full max-w-xl rounded-3xl bg-white/70 p-6 shadow-[0_25px_60px_-15px_rgba(167,139,250,0.4)] ring-1 ring-white/60 backdrop-blur sm:p-8 dark:bg-zinc-900/60 dark:shadow-[0_0_40px_rgba(34,211,238,0.15)] dark:ring-cyan-500/20"
    >
      <p className="text-xs font-semibold uppercase tracking-widest text-violet-400 dark:text-cyan-400">
        {t.cities[city] ?? city} &middot; {place.name}
      </p>
      <h2 className="mt-1 font-[family-name:var(--font-display)] text-2xl text-stone-800 dark:text-zinc-100">
        {t.postcardCreator.heading}
      </h2>
      <p className="mt-1 text-sm text-stone-500 dark:text-zinc-400">
        {t.postcardCreator.subheading}
      </p>

      <textarea
        value={review}
        onChange={(event) => setReview(event.target.value)}
        placeholder={t.postcardCreator.placeholder}
        rows={4}
        className="mt-6 w-full resize-none rounded-xl border border-stone-200 bg-white px-4 py-3 text-stone-800 outline-none focus:border-violet-300 focus:ring-2 focus:ring-violet-100 dark:border-cyan-500/20 dark:bg-zinc-950/50 dark:text-zinc-100 dark:placeholder:text-zinc-500 dark:focus:border-cyan-400 dark:focus:ring-cyan-500/30"
      />

      <div className="mt-6 flex gap-3">
        <button
          type="button"
          onClick={onCancel}
          disabled={isLoading}
          className="flex-1 rounded-xl border border-stone-200 px-6 py-3 font-medium text-stone-500 transition hover:bg-stone-50 disabled:cursor-not-allowed dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-900"
        >
          {t.postcardCreator.back}
        </button>
        <button
          type="submit"
          disabled={isLoading || !review.trim()}
          className="flex-[2] rounded-xl bg-violet-400 px-6 py-3 font-medium text-white shadow-[0_8px_20px_-4px_rgba(167,139,250,0.5)] transition hover:bg-violet-500 hover:shadow-[0_8px_24px_-2px_rgba(167,139,250,0.65)] disabled:cursor-not-allowed disabled:bg-stone-300 disabled:shadow-none dark:bg-cyan-500 dark:hover:bg-cyan-400 dark:shadow-[0_0_20px_rgba(34,211,238,0.5)] dark:disabled:bg-zinc-700 dark:disabled:shadow-none"
        >
          {isLoading ? t.postcardCreator.loading : t.postcardCreator.submit}
        </button>
      </div>
      {isLoading && (
        <p className="mt-3 text-center text-xs text-stone-400 dark:text-zinc-500">
          {t.postcardCreator.loadingHint}
        </p>
      )}
    </form>
  );
}
