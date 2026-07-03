import { useState } from "react";
import { useLanguage } from "../LanguageContext";

const CITY_KEYS = ["Paris", "Seoul"];

export default function MoodForm({ onSubmit, isLoading, onOpenPersonalization }) {
  const { t } = useLanguage();
  const [city, setCity] = useState(CITY_KEYS[0]);
  const [moodText, setMoodText] = useState("");

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!moodText.trim() || isLoading) return;
    onSubmit({ city, moodText: moodText.trim() });
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="mx-auto w-full max-w-xl rounded-3xl bg-white/70 p-6 shadow-[0_25px_60px_-15px_rgba(244,114,182,0.4)] ring-1 ring-white/60 backdrop-blur sm:p-8 dark:bg-zinc-900/60 dark:shadow-[0_0_40px_rgba(168,85,247,0.15)] dark:ring-fuchsia-500/20"
    >
      <h2 className="font-[family-name:var(--font-display)] text-2xl text-stone-800 dark:text-zinc-100">
        {t.moodForm.heading}
      </h2>
      <p className="mt-1 text-sm text-stone-500 dark:text-zinc-400">
        {t.moodForm.subheading}
      </p>

      <label className="mt-6 block text-sm font-medium text-stone-600 dark:text-zinc-300">
        {t.moodForm.cityLabel}
        <div className="relative mt-2">
          <select
            value={city}
            onChange={(event) => setCity(event.target.value)}
            className="w-full appearance-none rounded-xl border border-stone-200 bg-white px-4 py-3 pr-10 text-stone-800 outline-none focus:border-rose-300 focus:ring-2 focus:ring-rose-100 dark:border-fuchsia-500/20 dark:bg-zinc-950/50 dark:text-zinc-100 dark:focus:border-fuchsia-400 dark:focus:ring-fuchsia-500/30"
          >
            {CITY_KEYS.map((cityKey) => (
              <option key={cityKey} value={cityKey}>
                {t.cities[cityKey]}
              </option>
            ))}
          </select>
          <svg
            className="pointer-events-none absolute right-4 top-1/2 h-4 w-4 -translate-y-1/2 text-stone-400 dark:text-fuchsia-400"
            viewBox="0 0 20 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M5 7.5L10 12.5L15 7.5"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
      </label>

      <label className="mt-4 block text-sm font-medium text-stone-600 dark:text-zinc-300">
        {t.moodForm.moodLabel}
        <textarea
          value={moodText}
          onChange={(event) => setMoodText(event.target.value)}
          placeholder={t.moodForm.moodPlaceholder}
          rows={4}
          className="mt-2 w-full resize-none rounded-xl border border-stone-200 bg-white px-4 py-3 text-stone-800 outline-none focus:border-rose-300 focus:ring-2 focus:ring-rose-100 dark:border-fuchsia-500/20 dark:bg-zinc-950/50 dark:text-zinc-100 dark:placeholder:text-zinc-500 dark:focus:border-fuchsia-400 dark:focus:ring-fuchsia-500/30"
        />
      </label>

      <button
        type="submit"
        disabled={isLoading || !moodText.trim()}
        className="mt-6 w-full rounded-xl bg-rose-400 px-6 py-3 font-medium text-white shadow-[0_8px_20px_-4px_rgba(251,113,133,0.5)] transition hover:bg-rose-500 hover:shadow-[0_8px_24px_-2px_rgba(251,113,133,0.65)] disabled:cursor-not-allowed disabled:bg-stone-300 disabled:shadow-none dark:bg-fuchsia-500 dark:hover:bg-fuchsia-400 dark:shadow-[0_0_20px_rgba(232,68,255,0.5)] dark:disabled:bg-zinc-700 dark:disabled:shadow-none"
      >
        {isLoading ? t.moodForm.loading : t.moodForm.submit}
      </button>
      {isLoading && (
        <p className="mt-4 rounded-xl bg-stone-50 px-4 py-3 text-center text-sm leading-relaxed text-stone-500 ring-1 ring-stone-100 dark:bg-zinc-950/50 dark:text-zinc-300 dark:ring-fuchsia-500/20">
          {t.moodForm.loadingHint}
        </p>
      )}
      {onOpenPersonalization && (
        <button
          type="button"
          onClick={onOpenPersonalization}
          className="mt-4 block w-full text-center text-sm font-medium text-stone-500 underline-offset-4 hover:text-stone-700 hover:underline dark:text-zinc-400 dark:hover:text-zinc-200"
        >
          {t.moodForm.personalizationHint}
        </button>
      )}
    </form>
  );
}
