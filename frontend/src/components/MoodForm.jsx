import { useState } from "react";
import { useLanguage } from "../LanguageContext";

const CITY_KEYS = ["Paris", "Seoul"];

export default function MoodForm({ onSubmit, isLoading }) {
  const { t } = useLanguage();
  const [city, setCity] = useState(CITY_KEYS[0]);
  const [moodText, setMoodText] = useState("");

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!moodText.trim() || isLoading) return;
    onSubmit(city, moodText.trim());
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="mx-auto w-full max-w-xl rounded-3xl bg-white/70 p-8 shadow-xl shadow-rose-100 backdrop-blur"
    >
      <h2 className="font-[family-name:var(--font-display)] text-2xl text-stone-800">
        {t.moodForm.heading}
      </h2>
      <p className="mt-1 text-sm text-stone-500">{t.moodForm.subheading}</p>

      <label className="mt-6 block text-sm font-medium text-stone-600">
        {t.moodForm.cityLabel}
        <select
          value={city}
          onChange={(event) => setCity(event.target.value)}
          className="mt-2 w-full rounded-xl border border-stone-200 bg-white px-4 py-3 text-stone-800 outline-none focus:border-rose-300 focus:ring-2 focus:ring-rose-100"
        >
          {CITY_KEYS.map((cityKey) => (
            <option key={cityKey} value={cityKey}>
              {t.cities[cityKey]}
            </option>
          ))}
        </select>
      </label>

      <label className="mt-4 block text-sm font-medium text-stone-600">
        {t.moodForm.moodLabel}
        <textarea
          value={moodText}
          onChange={(event) => setMoodText(event.target.value)}
          placeholder={t.moodForm.moodPlaceholder}
          rows={4}
          className="mt-2 w-full resize-none rounded-xl border border-stone-200 bg-white px-4 py-3 text-stone-800 outline-none focus:border-rose-300 focus:ring-2 focus:ring-rose-100"
        />
      </label>

      <button
        type="submit"
        disabled={isLoading || !moodText.trim()}
        className="mt-6 w-full rounded-xl bg-rose-400 px-6 py-3 font-medium text-white transition hover:bg-rose-500 disabled:cursor-not-allowed disabled:bg-stone-300"
      >
        {isLoading ? t.moodForm.loading : t.moodForm.submit}
      </button>
      {isLoading && (
        <p className="mt-3 text-center text-xs text-stone-400">
          {t.moodForm.loadingHint}
        </p>
      )}
    </form>
  );
}
