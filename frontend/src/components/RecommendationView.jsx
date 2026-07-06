import { useState } from "react";
import CityMiniMap from "./CityMiniMap";
import { useLanguage } from "../LanguageContext";

const localized = (value, lang) => {
  if (value && typeof value === "object") {
    return value[lang] ?? value.en ?? value.ko ?? "";
  }
  return value ?? "";
};

export default function RecommendationView({
  result,
  isContinuation = false,
  requireLogin = false,
  onSelectPlace,
  onStartOver,
  onEndTrip,
  isEndingTrip = false,
}) {
  const { t, lang } = useLanguage();
  const [hoveredPlaceId, setHoveredPlaceId] = useState(null);
  const [selectedPlaceId, setSelectedPlaceId] = useState(null);
  if (!result) return null;
  const { clue, places: allPlaces } = result;
  const places = allPlaces;
  const selectedPlace =
    places.find((place) => place.id === selectedPlaceId) || places[0] || null;
  const activePlaceId = hoveredPlaceId || selectedPlace?.id || null;
  const actionButtons = (
    <div className="mt-3 flex flex-wrap justify-center gap-x-5 gap-y-2 text-center">
      <button
        onClick={onEndTrip}
        disabled={isEndingTrip}
        className="text-sm font-semibold text-rose-500 underline-offset-4 hover:text-rose-600 hover:underline dark:text-fuchsia-300 dark:hover:text-fuchsia-200"
      >
        {isEndingTrip ? t.finalPostcard.loading : t.recommendation.endTrip}
      </button>
      <button
        onClick={onStartOver}
        className="text-sm font-medium text-stone-600 underline-offset-4 hover:text-stone-800 hover:underline dark:text-zinc-300 dark:hover:text-zinc-100"
      >
        {t.recommendation.startOver}
      </button>
    </div>
  );

  return (
    <div className="mx-auto w-full max-w-3xl pb-[calc(6rem+env(safe-area-inset-bottom))] lg:max-w-5xl">
      <div className="rounded-3xl bg-gradient-to-br from-rose-100 via-white to-pink-100 p-6 text-center shadow-[0_25px_60px_-15px_rgba(251,113,133,0.35)] ring-1 ring-rose-100/80 sm:p-8 dark:from-fuchsia-950/45 dark:via-zinc-950/75 dark:to-violet-950/45 dark:shadow-[0_0_40px_rgba(217,70,239,0.14)] dark:ring-fuchsia-500/20">
        <p className="text-xs font-semibold uppercase tracking-widest text-rose-400 dark:text-fuchsia-400">
          {t.recommendation.clueLabel}
        </p>
        <p className="mt-3 font-[family-name:var(--font-display)] text-lg italic text-stone-700 sm:text-xl dark:text-fuchsia-50">
          &ldquo;{localized(clue, lang)}&rdquo;
        </p>
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
            <div className="flex min-h-full flex-col rounded-2xl border border-rose-100 bg-white/90 p-5 text-left shadow-sm ring-2 ring-rose-100/80 dark:border-fuchsia-500/30 dark:bg-zinc-950/65 dark:ring-fuchsia-500/15">
              <div className="flex items-center justify-between gap-2">
                <span className="text-lg font-semibold text-stone-800 dark:text-zinc-100">
                  {localized(selectedPlace.name_i18n, lang) || selectedPlace.name}
                </span>
                {selectedPlace.type && (
                  <span className="shrink-0 rounded-full bg-rose-50 px-2 py-0.5 text-[10px] font-medium text-rose-500 dark:bg-fuchsia-950/50 dark:text-fuchsia-200">
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
              <button
                onClick={() => onSelectPlace(selectedPlace)}
                className="mt-auto pt-5 text-left text-sm font-medium text-rose-500 hover:text-rose-600 dark:text-fuchsia-300 dark:hover:text-fuchsia-200"
              >
                {requireLogin ? t.recommendation.visitCtaGuest : t.recommendation.visitCta}
              </button>
            </div>
          )}
        </div>
      ) : (
        <p className="mx-auto mt-4 max-w-xl rounded-2xl bg-white/80 px-5 py-4 text-center text-sm text-stone-500 shadow-sm ring-1 ring-rose-100/80 dark:bg-zinc-950/60 dark:text-zinc-400 dark:ring-fuchsia-500/20">
          {isContinuation ? t.recommendation.allVisited : t.recommendation.noMatches}
        </p>
      )}
      <p className="mx-auto mt-4 max-w-xl text-center text-[11px] leading-relaxed text-stone-400 dark:text-zinc-500">
        {t.recommendation.sourceDisclaimer}
      </p>
    </div>
  );
}
