import { useLanguage } from "../LanguageContext";

const localized = (value, lang) => {
  if (value && typeof value === "object") {
    return value[lang] ?? value.en ?? value.ko ?? "";
  }
  return value ?? "";
};

// Places are recommended live by AI now (no fixed catalog), so marker
// positions come from each place's own map_position instead of a
// name-keyed lookup table. Only the background art stays per-city.
const MAP_IMAGES = {
  Paris: { src: "/maps/paris-map.png", aspect: "aspect-[900/636]" },
  Seoul: { src: "/maps/seoul-map.png", aspect: "aspect-[1200/848]" },
};

export default function CityMiniMap({ places, activePlaceId, onHover, onSelectMarker }) {
  const { t, lang } = useLanguage();
  const city = places?.[0]?.city;
  const map = MAP_IMAGES[city];
  if (!map) return null;

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

      <div className={`relative mt-3 w-full overflow-hidden rounded-xl ${map.aspect}`}>
        <img
          src={map.src}
          alt=""
          className="absolute inset-0 h-full w-full object-contain opacity-80 dark:opacity-70 dark:invert"
          draggable="false"
        />
        <div className="absolute inset-0">
          {places.map((place, index) => {
            const position = place.map_position;
            if (!position) return null;
            const isActive = place.id === activePlaceId;
            return (
              <button
                key={place.id}
                type="button"
                onClick={() => onSelectMarker?.(place.id)}
                onMouseEnter={() => onHover?.(place.id)}
                onMouseLeave={() => onHover?.(null)}
                onFocus={() => onHover?.(place.id)}
                onBlur={() => onHover?.(null)}
                title={localized(place.name_i18n, lang) || place.name}
                className={`absolute flex -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full text-[10px] font-semibold transition ${
                  isActive
                    ? "h-6 w-6 bg-rose-500 text-white shadow-[0_0_18px_rgba(244,63,94,0.55)] ring-2 ring-white/80 dark:bg-fuchsia-300 dark:text-zinc-950 dark:ring-fuchsia-100/70"
                    : "h-5 w-5 bg-rose-400 text-white shadow-[0_0_10px_rgba(251,113,133,0.45)] ring-2 ring-white/75 dark:bg-fuchsia-500 dark:ring-zinc-950/70"
                }`}
                style={{ left: `${position.x}%`, top: `${position.y}%` }}
              >
                {index + 1}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
