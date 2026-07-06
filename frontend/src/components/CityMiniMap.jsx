import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useLanguage } from "../LanguageContext";
import { useTheme } from "../ThemeContext";

const localized = (value, lang) => {
  if (value && typeof value === "object") {
    return value[lang] ?? value.en ?? value.ko ?? "";
  }
  return value ?? "";
};

// Free, no-API-key tile sources. CARTO's dark tiles keep the map legible in
// dark mode without needing a Google/Mapbox key or billing account.
const TILE_LAYERS = {
  light: {
    url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  },
  dark: {
    url: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
  },
};

function markerIcon(index, isActive) {
  const size = isActive ? 26 : 22;
  return L.divIcon({
    className: "mood-map-marker",
    html: `<span style="
      display:flex;align-items:center;justify-content:center;
      width:${size}px;height:${size}px;border-radius:9999px;
      background:${isActive ? "#f43f5e" : "#fb7185"};
      color:#fff;font-size:11px;font-weight:600;
      box-shadow:0 0 ${isActive ? 18 : 10}px rgba(244,63,94,0.5);
      border:2px solid rgba(255,255,255,0.85);
    ">${index}</span>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
  });
}

export default function CityMiniMap({ places, activePlaceId, onHover, onSelectMarker }) {
  const { t, lang } = useLanguage();
  const { theme } = useTheme();
  const containerRef = useRef(null);
  const mapRef = useRef(null);
  const tileLayerRef = useRef(null);
  const markersRef = useRef([]);

  const city = places?.[0]?.city;
  const validPlaces = (places || []).filter((place) => place.coordinates);

  // Map init/teardown once per mount.
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    const map = L.map(containerRef.current, {
      zoomControl: false,
      attributionControl: true,
      scrollWheelZoom: false,
    });
    map.setView([48.8566, 2.3522], 12);
    mapRef.current = map;
    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // Swap tile layer with theme.
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    const config = TILE_LAYERS[theme] ?? TILE_LAYERS.light;
    if (tileLayerRef.current) {
      map.removeLayer(tileLayerRef.current);
    }
    tileLayerRef.current = L.tileLayer(config.url, {
      attribution: config.attribution,
      maxZoom: 19,
    }).addTo(map);
  }, [theme]);

  // Redraw markers and refit view whenever the recommended places change.
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    markersRef.current.forEach((marker) => marker.remove());
    markersRef.current = [];

    if (validPlaces.length === 0) return;

    validPlaces.forEach((place, index) => {
      const { lat, lng } = place.coordinates;
      const marker = L.marker([lat, lng], {
        icon: markerIcon(index + 1, place.id === activePlaceId),
      })
        .addTo(map)
        .bindTooltip(localized(place.name_i18n, lang) || place.name)
        .on("click", () => onSelectMarker?.(place.id))
        .on("mouseover", () => onHover?.(place.id))
        .on("mouseout", () => onHover?.(null));
      markersRef.current.push(marker);
    });

    if (validPlaces.length === 1) {
      map.setView([validPlaces[0].coordinates.lat, validPlaces[0].coordinates.lng], 14);
    } else {
      const bounds = L.latLngBounds(
        validPlaces.map((place) => [place.coordinates.lat, place.coordinates.lng])
      );
      map.fitBounds(bounds, { padding: [32, 32] });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [validPlaces, activePlaceId, lang]);

  if (!city) return null;

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

      <div
        ref={containerRef}
        className="relative mt-3 aspect-[4/3] w-full overflow-hidden rounded-xl"
      />
    </div>
  );
}
