import { useLanguage } from "../LanguageContext";

const MAP_IMAGES = {
  Paris: "/maps/paris-map.png",
  Seoul: "/maps/seoul-map.png",
};

const localized = (value, lang) => {
  if (value && typeof value === "object") {
    return value[lang] ?? value.en ?? value.ko ?? "";
  }
  return value ?? "";
};

function clampPercent(value) {
  const number = Number(value);
  if (Number.isNaN(number)) return 50;
  return Math.min(96, Math.max(4, number));
}

export default function CityMiniMap({ places, activePlaceId, onHover, onSelectMarker }) {
  const { t, lang } = useLanguage();
  const city = places?.[0]?.city;
  const mapImage = MAP_IMAGES[city];
  const validPlaces = (places || []).filter((place) => place.map_position);

  if (!city || !mapImage) return null;

  return (
    <div className="rounded-2xl border border-rose-100 bg-white/80 p-4 shadow-sm ring-1 ring-rose-100/80 dark:border-fuchsia-500/20 dark:bg-zinc-950/60 dark:ring-fuchsia-500/15">
      <div className="flex items-center justify-between gap-3">
        <p className="text-xs font-semibold uppercase tracking-widest text-rose-400 dark:text-fuchsia-300">
          {t.recommendation.mapTitle}
        </p>
        <span className="text-[11px] text-stone-400 dark:text-zinc-500">
          {t.cities[city] ?? city}
        </span>
      </div>

      <div className="relative mt-3 aspect-[4/3] w-full overflow-hidden rounded-xl bg-stone-50 dark:bg-zinc-950">
        <img
          src={mapImage}
          alt={`${t.cities[city] ?? city} ${t.recommendation.mapTitle}`}
          className="h-full w-full object-contain opacity-80 grayscale contrast-110 dark:opacity-55 dark:invert"
          draggable="false"
        />
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-white/10 via-transparent to-white/15 dark:from-zinc-950/20 dark:to-zinc-950/35" />
        {validPlaces.map((place, index) => {
          const isActive = place.id === activePlaceId;
          const x = clampPercent(place.map_position.x);
          const y = clampPercent(place.map_position.y);
          const placeName = localized(place.name_i18n, lang) || place.name;
          return (
            <button
              key={place.id}
              type="button"
              title={placeName}
              aria-label={placeName}
              onClick={() => onSelectMarker?.(place.id)}
              onMouseEnter={() => onHover?.(place.id)}
              onMouseLeave={() => onHover?.(null)}
              className={`absolute flex -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border-2 border-white text-[10px] font-bold text-white shadow-lg transition ${
                isActive
                  ? "h-7 w-7 bg-rose-500 shadow-rose-400/50 dark:bg-fuchsia-400 dark:shadow-fuchsia-400/50"
                  : "h-6 w-6 bg-rose-400 shadow-rose-300/40 hover:scale-110 dark:bg-fuchsia-500 dark:shadow-fuchsia-500/40"
              }`}
              style={{ left: `${x}%`, top: `${y}%` }}
            >
              {index + 1}
            </button>
          );
        })}
      </div>
      <p className="mt-2 text-[11px] leading-relaxed text-stone-400 dark:text-zinc-500">
        {t.recommendation.mapHint}
      </p>
    </div>
  );
}
