import { useState } from "react";
import CityMiniMap from "./CityMiniMap";
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

export default function RecommendationView({
  result,
  visitedPlaceIds = [],
  isContinuation = false,
  requireLogin = false,
  onSelectPlace,
  onStartOver,
  onEndTrip,
  onDismiss,
}) {
  const { t, lang } = useLanguage();
  const [hoveredPlaceId, setHoveredPlaceId] = useState(null);
  const [selectedPlaceId, setSelectedPlaceId] = useState(null);
  if (!result) return null;
  const { clue, tags, avoid_tags: avoidTags, places: allPlaces } = result;
  const places = allPlaces.filter((place) => !visitedPlaceIds.includes(place.id));
  const selectedPlace =
    places.find((place) => place.id === selectedPlaceId) || places[0] || null;
  const activePlaceId = hoveredPlaceId || selectedPlace?.id || null;
  const actionButtons = (
    <div className="mt-3 flex flex-wrap justify-center gap-x-5 gap-y-2 text-center">
      {isContinuation && (
        <button
          onClick={onEndTrip}
          className="text-sm font-semibold text-rose-500 underline-offset-4 hover:text-rose-600 hover:underline dark:text-fuchsia-300 dark:hover:text-fuchsia-200"
        >
          {t.recommendation.endTrip}
        </button>
      )}
      <button
        onClick={onStartOver}
        className="text-sm font-medium text-stone-600 underline-offset-4 hover:text-stone-800 hover:underline dark:text-zinc-300 dark:hover:text-zinc-100"
      >
        {t.recommendation.startOver}
      </button>
      {!isContinuation && (
        <button
          onClick={onDismiss}
          className="text-sm font-medium text-stone-500 underline-offset-4 hover:text-stone-800 hover:underline dark:text-zinc-400 dark:hover:text-zinc-100"
        >
          {t.recommendation.dismiss}
        </button>
      )}
    </div>
  );

  return (
    <div className="mx-auto w-full max-w-3xl pb-[calc(6rem+env(safe-area-inset-bottom))] lg:max-w-5xl">
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
        {avoidTags?.length > 0 && (
          <div className="mt-4 text-xs text-stone-500 dark:text-zinc-400">
            <p>
              <span className="font-semibold text-stone-600 dark:text-zinc-300">
                {t.recommendation.avoidSummaryLabel}:
              </span>{" "}
              {avoidTags.map((tag) => localizedTag(tag, lang, t)).join(" · ")}
            </p>
          </div>
        )}
      </div>

      <h3 className="mt-8 text-center text-lg font-medium text-stone-700 dark:text-zinc-200">
        {isContinuation
          ? t.recommendation.continuationHeading
          : t.recommendation.spotsHeading}
      </h3>
      {actionButtons}
      {places.length > 0 ? (
        <div className="mt-4 grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
          <CityMiniMap
            places={places}
            activePlaceId={activePlaceId}
            onHover={setHoveredPlaceId}
            onSelectMarker={setSelectedPlaceId}
          />
          {selectedPlace && (
            <div className="flex min-h-full flex-col rounded-2xl border border-rose-200 bg-white p-5 text-left shadow-sm ring-2 ring-rose-100 dark:border-fuchsia-500/40 dark:bg-zinc-900/60 dark:ring-fuchsia-500/15">
              <div className="flex items-center justify-between gap-2">
                <span className="text-lg font-semibold text-stone-800 dark:text-zinc-100">
                  {localized(selectedPlace.name_i18n, lang) || selectedPlace.name}
                </span>
                {selectedPlace.type && (
                  <span className="shrink-0 rounded-full bg-violet-50 px-2 py-0.5 text-[10px] font-medium text-violet-500 dark:bg-cyan-950/50 dark:text-cyan-300">
                    {localized(selectedPlace.type_i18n, lang) || selectedPlace.type}
                  </span>
                )}
              </div>
              {(localized(selectedPlace.duration_label_i18n, lang) ||
                selectedPlace.duration_labels?.join(" / ")) && (
                <span className="mt-1 text-[11px] text-stone-400 dark:text-zinc-500">
                  {localized(selectedPlace.duration_label_i18n, lang) ||
                    selectedPlace.duration_labels.join(" / ")}
                </span>
              )}
              <span className="mt-3 text-sm leading-relaxed text-stone-500 dark:text-zinc-400">
                {localized(selectedPlace.description_i18n, lang) ||
                  selectedPlace.description}
              </span>
              {(localized(selectedPlace.reason_i18n, lang) || selectedPlace.reason) && (
                <p className="mt-3 text-xs italic leading-relaxed text-stone-500 dark:text-zinc-400">
                  {localized(selectedPlace.reason_i18n, lang) || selectedPlace.reason}
                </p>
              )}
              {(localized(selectedPlace.avoid_warning_i18n, lang) ||
                selectedPlace.avoid_warnings?.join(", ")) && (
                <p className="mt-2 text-[11px] text-amber-600 dark:text-amber-400">
                  {t.recommendation.avoidWarningPrefix}{" "}
                  {localized(selectedPlace.avoid_warning_i18n, lang) ||
                    selectedPlace.avoid_warnings.join(", ")}
                </p>
              )}
              <button
                onClick={() => onSelectPlace(selectedPlace)}
                className="mt-auto pt-5 text-left text-sm font-medium text-rose-400 hover:text-rose-500 dark:text-cyan-400 dark:hover:text-cyan-300"
              >
                {requireLogin ? t.recommendation.visitCtaGuest : t.recommendation.visitCta}
              </button>
            </div>
          )}
        </div>
      ) : (
        <p className="mx-auto mt-4 max-w-xl rounded-2xl bg-white/70 px-5 py-4 text-center text-sm text-stone-500 shadow-sm ring-1 ring-white/60 dark:bg-zinc-900/60 dark:text-zinc-400 dark:ring-fuchsia-500/20">
          {isContinuation ? t.recommendation.allVisited : t.recommendation.noMatches}
        </p>
      )}
    </div>
  );
}
