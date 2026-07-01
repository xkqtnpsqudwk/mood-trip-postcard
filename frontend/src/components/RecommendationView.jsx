import { useLanguage } from "../LanguageContext";

export default function RecommendationView({ result, onSelectPlace, onStartOver }) {
  const { t } = useLanguage();
  if (!result) return null;
  const { clue, tags, places } = result;

  return (
    <div className="mx-auto w-full max-w-3xl">
      <div className="rounded-3xl bg-gradient-to-br from-rose-100 to-violet-100 p-8 text-center shadow-lg">
        <p className="text-xs font-semibold uppercase tracking-widest text-rose-400">
          {t.recommendation.clueLabel}
        </p>
        <p className="mt-3 font-[family-name:var(--font-display)] text-xl italic text-stone-700">
          &ldquo;{clue}&rdquo;
        </p>
        {tags?.length > 0 && (
          <div className="mt-4 flex flex-wrap justify-center gap-2">
            {tags.map((tag) => (
              <span
                key={tag}
                className="rounded-full bg-white/70 px-3 py-1 text-xs font-medium text-rose-500"
              >
                #{tag}
              </span>
            ))}
          </div>
        )}
      </div>

      <h3 className="mt-8 text-center text-lg font-medium text-stone-700">
        {t.recommendation.spotsHeading}
      </h3>
      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        {places.map((place) => (
          <button
            key={place.id}
            onClick={() => onSelectPlace(place)}
            className="group flex flex-col rounded-2xl border border-stone-200 bg-white p-5 text-left shadow-sm transition hover:-translate-y-1 hover:border-rose-200 hover:shadow-lg"
          >
            <span className="text-base font-semibold text-stone-800 group-hover:text-rose-500">
              {place.name}
            </span>
            <span className="mt-2 text-sm text-stone-500">{place.description}</span>
            <span className="mt-3 text-xs text-stone-400">{place.mood_tags}</span>
            <span className="mt-4 text-sm font-medium text-rose-400">
              {t.recommendation.visitCta}
            </span>
          </button>
        ))}
      </div>

      <div className="mt-6 text-center">
        <button
          onClick={onStartOver}
          className="text-sm text-stone-400 underline-offset-4 hover:text-stone-600 hover:underline"
        >
          {t.recommendation.startOver}
        </button>
      </div>
    </div>
  );
}
