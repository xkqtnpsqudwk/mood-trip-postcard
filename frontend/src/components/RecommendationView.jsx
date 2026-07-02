import { useLanguage } from "../LanguageContext";

const normalizeTag = (tag) => String(tag).trim().toLowerCase().replace(/[\s_]+/g, "-");

const localized = (value, lang) => {
  if (value && typeof value === "object") {
    return value[lang] ?? value.en ?? value.ko ?? "";
  }
  return value ?? "";
};

const localizedTag = (tag, lang, t) => {
  if (tag && typeof tag === "object") {
    return localized(tag, lang);
  }
  return t.tagLabels?.[normalizeTag(tag)] ?? tag;
};

export default function RecommendationView({ result, onSelectPlace, onStartOver }) {
  const { t, lang } = useLanguage();
  if (!result) return null;
  const { clue, tags, places } = result;

  return (
    <div className="mx-auto w-full max-w-3xl lg:max-w-5xl">
      <div className="rounded-3xl bg-gradient-to-br from-rose-200 via-rose-100 to-violet-200 p-6 text-center shadow-[0_25px_60px_-15px_rgba(216,180,254,0.5)] ring-1 ring-white/60 sm:p-8 dark:from-fuchsia-950/50 dark:via-transparent dark:to-cyan-950/40 dark:shadow-[0_0_40px_rgba(168,85,247,0.15)] dark:ring-fuchsia-500/20">
        <p className="text-xs font-semibold uppercase tracking-widest text-rose-400 dark:text-fuchsia-400">
          {t.recommendation.clueLabel}
        </p>
        <p className="mt-3 font-[family-name:var(--font-display)] text-lg italic text-stone-700 sm:text-xl dark:text-cyan-100">
          &ldquo;{localized(clue, lang)}&rdquo;
        </p>
        {tags?.length > 0 && (
          <div className="mt-4 flex flex-wrap justify-center gap-2">
            {tags.map((tag, index) => (
              <span
                key={`${localizedTag(tag, "en", t)}-${index}`}
                className="rounded-full bg-white/70 px-3 py-1 text-xs font-medium text-rose-500 dark:bg-zinc-900/70 dark:text-fuchsia-300 dark:ring-1 dark:ring-fuchsia-500/20"
              >
                #{localizedTag(tag, lang, t)}
              </span>
            ))}
          </div>
        )}
      </div>

      <h3 className="mt-8 text-center text-lg font-medium text-stone-700 dark:text-zinc-200">
        {t.recommendation.spotsHeading}
      </h3>
      {places.length > 0 ? (
        <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {places.map((place) => (
            <button
              key={place.id}
              onClick={() => onSelectPlace(place)}
              className="group flex flex-col rounded-2xl border border-stone-200 bg-white p-5 text-left shadow-sm transition hover:-translate-y-1 hover:border-rose-200 hover:shadow-[0_16px_30px_-10px_rgba(251,113,133,0.35)] dark:border-zinc-800 dark:bg-zinc-900/60 dark:hover:border-fuchsia-500/50 dark:hover:shadow-[0_0_20px_rgba(232,68,255,0.25)]"
            >
              <span className="text-base font-semibold text-stone-800 group-hover:text-rose-500 dark:text-zinc-100 dark:group-hover:text-fuchsia-300">
                {localized(place.name_i18n, lang) || place.name}
              </span>
              <span className="mt-2 text-sm text-stone-500 dark:text-zinc-400">
                {localized(place.description_i18n, lang) || place.description}
              </span>
              <span className="mt-3 text-xs text-stone-400 dark:text-zinc-500">
                {localized(place.mood_tags_i18n, lang) || place.mood_tags}
              </span>
              <span className="mt-4 text-sm font-medium text-rose-400 dark:text-cyan-400">
                {t.recommendation.visitCta}
              </span>
            </button>
          ))}
        </div>
      ) : (
        <p className="mx-auto mt-4 max-w-xl rounded-2xl bg-white/70 px-5 py-4 text-center text-sm text-stone-500 shadow-sm ring-1 ring-white/60 dark:bg-zinc-900/60 dark:text-zinc-400 dark:ring-fuchsia-500/20">
          {t.recommendation.noMatches}
        </p>
      )}

      <div className="mt-6 text-center">
        <button
          onClick={onStartOver}
          className="text-sm text-stone-400 underline-offset-4 hover:text-stone-600 hover:underline dark:text-zinc-500 dark:hover:text-zinc-300"
        >
          {t.recommendation.startOver}
        </button>
      </div>
    </div>
  );
}
