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
      className="mx-auto w-full max-w-xl rounded-3xl bg-white/70 p-8 shadow-xl shadow-violet-100 backdrop-blur"
    >
      <p className="text-xs font-semibold uppercase tracking-widest text-violet-400">
        {t.cities[city] ?? city} &middot; {place.name}
      </p>
      <h2 className="mt-1 font-[family-name:var(--font-display)] text-2xl text-stone-800">
        {t.postcardCreator.heading}
      </h2>
      <p className="mt-1 text-sm text-stone-500">{t.postcardCreator.subheading}</p>

      <textarea
        value={review}
        onChange={(event) => setReview(event.target.value)}
        placeholder={t.postcardCreator.placeholder}
        rows={4}
        className="mt-6 w-full resize-none rounded-xl border border-stone-200 bg-white px-4 py-3 text-stone-800 outline-none focus:border-violet-300 focus:ring-2 focus:ring-violet-100"
      />

      <div className="mt-6 flex gap-3">
        <button
          type="button"
          onClick={onCancel}
          disabled={isLoading}
          className="flex-1 rounded-xl border border-stone-200 px-6 py-3 font-medium text-stone-500 transition hover:bg-stone-50 disabled:cursor-not-allowed"
        >
          {t.postcardCreator.back}
        </button>
        <button
          type="submit"
          disabled={isLoading || !review.trim()}
          className="flex-[2] rounded-xl bg-violet-400 px-6 py-3 font-medium text-white transition hover:bg-violet-500 disabled:cursor-not-allowed disabled:bg-stone-300"
        >
          {isLoading ? t.postcardCreator.loading : t.postcardCreator.submit}
        </button>
      </div>
      {isLoading && (
        <p className="mt-3 text-center text-xs text-stone-400">
          {t.postcardCreator.loadingHint}
        </p>
      )}
    </form>
  );
}
