import { useLanguage } from "../LanguageContext";

const localized = (value, lang) => {
  if (value && typeof value === "object") {
    return value[lang] ?? value.en ?? value.ko ?? "";
  }
  return value ?? "";
};

const MAPS = {
  Paris: {
    src: "/maps/paris-map.png",
    aspect: "aspect-[900/636]",
    coordinates: {
      "Seine Riverside": [53, 56],
      "Pont des Arts": [52, 55],
      Montmartre: [45, 18],
      "Luxembourg Gardens": [50, 64],
      "Pere Lachaise Cemetery": [70, 51],
      "Tuileries Garden": [45, 52],
      "Canal Saint-Martin": [58, 38],
      "Sainte-Chapelle": [55, 56],
      "Le Marais": [61, 51],
      "Parc des Buttes-Chaumont": [68, 30],
      "Musee d'Orsay": [45, 56],
      "Place des Vosges": [63, 54],
      "Jardin des Plantes": [61, 65],
      "Rue Cremieux": [65, 60],
      "Passage des Panoramas": [49, 38],
      "Shakespeare and Company": [55, 59],
      "Butte aux Cailles": [58, 75],
      "Parc Monceau": [35, 29],
      "Parc Montsouris": [53, 82],
      Belleville: [73, 39],
      "Ile Saint-Louis": [59, 57],
      "Trocadero Gardens": [30, 56],
      "Village Saint-Paul": [63, 57],
      "Marche des Enfants Rouges": [60, 47],
      "Coulee Verte Rene-Dumont": [68, 62],
      "Musee Rodin Garden": [40, 64],
      "Parc de la Villette": [70, 20],
      Batignolles: [37, 21],
    },
  },
  Seoul: {
    src: "/maps/seoul-map.png",
    aspect: "aspect-[1200/848]",
    coordinates: {
      "Han River Park": [47, 56],
      "Bukchon Hanok Village": [50, 33],
      Hongdae: [31, 47],
      "Namsan Tower": [49, 47],
      "Seonyudo Park": [34, 57],
      "Seoul Forest": [63, 52],
      "Ikseon-dong Hanok Street": [52, 36],
      "Cheonggyecheon Stream": [54, 41],
      "Gyeongui Line Forest Park": [35, 45],
      "Dongdaemun Design Plaza": [58, 40],
      Insadong: [51, 36],
      "Gwangjang Market": [56, 39],
      Myeongdong: [50, 43],
      "Ihwa Mural Village": [57, 34],
      "Seochon Village": [45, 35],
      "Gyeongbokgung Palace": [48, 31],
      "Changdeokgung Secret Garden": [53, 32],
      "Deoksugung Stone Wall Road": [46, 41],
      "Naksan Park": [58, 33],
      "Yeouido Hangang Park": [32, 58],
      "Banpo Hangang Park": [48, 61],
      "Seongsu-dong Cafe Street": [64, 51],
      "Mangwon Market": [28, 50],
      "Jongmyo Shrine": [54, 36],
      "National Museum of Korea": [47, 63],
      "Leeum Museum of Art": [52, 52],
      "Gyeongridan-gil": [50, 51],
      "Ttukseom Hangang Park": [65, 55],
    },
  },
};

function placeKey(place, lang) {
  return localized(place.name_i18n, "en") || localized(place.name_i18n, lang) || place.name;
}

export default function CityMiniMap({ places, activePlaceId, onHover, onSelectMarker }) {
  const { t, lang } = useLanguage();
  const city = places?.[0]?.city;
  const map = MAPS[city];
  if (!map) return null;

  return (
    <div className="rounded-2xl border border-stone-200 bg-white/75 p-4 shadow-sm ring-1 ring-white/70 dark:border-zinc-800 dark:bg-zinc-900/55 dark:ring-fuchsia-500/15">
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
            const coordinate = map.coordinates[placeKey(place, lang)];
            if (!coordinate) return null;
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
                    ? "h-6 w-6 bg-fuchsia-400 text-white shadow-[0_0_18px_rgba(217,70,239,0.75)] ring-2 ring-white/80 dark:bg-cyan-300 dark:text-zinc-950 dark:ring-cyan-100/70"
                    : "h-5 w-5 bg-rose-400 text-white shadow-[0_0_10px_rgba(251,113,133,0.45)] ring-2 ring-white/75 dark:bg-fuchsia-400 dark:ring-zinc-950/70"
                }`}
                style={{ left: `${coordinate[0]}%`, top: `${coordinate[1]}%` }}
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
