import { useState } from "react";
import { useLanguage } from "../LanguageContext";

function formatDate(isoString, locale) {
  const date = new Date(isoString.replace(" ", "T") + "Z");
  if (Number.isNaN(date.getTime())) return isoString;
  return date.toLocaleDateString(locale, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

const localized = (value, lang) => {
  if (value && typeof value === "object") {
    return value[lang] ?? value.en ?? value.ko ?? "";
  }
  return value ?? "";
};

export default function Postcard({ postcard, defaultFlipped = false, onOpen }) {
  const { t, lang } = useLanguage();
  const [isFlipped, setIsFlipped] = useState(defaultFlipped);
  const placeName = localized(postcard.place_name_i18n, lang) || postcard.place_name;
  const isRecord = (postcard.artifact_type || "record") === "record";
  const nextPlaceName =
    localized(postcard.next_place_name_i18n, lang) || postcard.next_place_name;

  const handleClick = () => {
    if (onOpen) {
      onOpen();
    } else {
      setIsFlipped((flipped) => !flipped);
    }
  };

  return (
    <div
      className={`postcard-flip aspect-[3/2] w-full cursor-pointer ${isFlipped ? "is-flipped" : ""}`}
      onClick={handleClick}
    >
      <div className="postcard-flip-inner relative h-full w-full">
        <div className="postcard-face absolute inset-0 overflow-hidden rounded-2xl bg-rose-50 shadow-[0_20px_45px_-12px_rgba(251,113,133,0.32)] ring-1 ring-rose-100/80 dark:bg-zinc-900 dark:ring-fuchsia-500/20 dark:shadow-[0_0_30px_rgba(217,70,239,0.18)]">
          {postcard.image_url ? (
            <>
              <img
                src={postcard.image_url}
                alt={`${placeName} ${isRecord ? "moment" : "postcard"}`}
                className="h-full w-full object-cover"
              />
            </>
          ) : (
            <div className="h-full w-full bg-gradient-to-br from-rose-100 via-white to-pink-100 dark:from-zinc-900 dark:via-zinc-950 dark:to-fuchsia-950" />
          )}
          <div className="absolute inset-x-0 bottom-0 flex items-end justify-between bg-gradient-to-t from-black/60 to-transparent px-4 py-3">
            <p className="truncate text-[10px] font-semibold uppercase tracking-widest text-white/85">
              {t.cities[postcard.city] ?? postcard.city} &middot; {placeName}
            </p>
            <p className="shrink-0 pl-3 text-[10px] text-white/70">
              {onOpen ? t.postcard.tapToOpen : t.postcard.tapToFlip}
            </p>
          </div>
        </div>

        <div className="postcard-face postcard-face-back absolute inset-0 overflow-hidden rounded-2xl bg-[#fbf6ed] p-5 text-stone-700 shadow-[0_20px_45px_-12px_rgba(120,113,108,0.35)] ring-1 ring-stone-200 dark:bg-zinc-100 dark:text-stone-800 dark:ring-zinc-700">
          {isRecord ? (
            <div className="flex h-full flex-col">
              <p className="text-[10px] font-semibold uppercase tracking-[0.26em] text-stone-400">
                {t.record.cardLabel}
              </p>
              <h3 className="mt-2 line-clamp-2 font-[family-name:var(--font-display)] text-xl leading-tight text-stone-800">
                {t.record.momentTitle(placeName)}
              </h3>
              <p className="mt-4 line-clamp-5 text-sm leading-relaxed text-stone-600">
                {postcard.review}
              </p>
              <p className="mt-auto text-[10px] text-stone-400">
                {formatDate(postcard.created_at, t.postcard.locale)}
              </p>
            </div>
          ) : (
            <div className="flex h-full gap-4">
              <div className="flex flex-1 flex-col">
                <p className="text-[10px] font-semibold uppercase tracking-[0.26em] text-stone-400">
                  Post Card
                </p>
                <p className="mt-1 truncate text-[10px] text-stone-400">
                  {t.cities[postcard.city] ?? postcard.city} / {placeName}
                </p>
                <div className="mt-5 space-y-4">
                  <div className="h-px bg-stone-300" />
                  <div className="h-px bg-stone-300" />
                  <div className="h-px bg-stone-300" />
                  <div className="h-px bg-stone-300" />
                </div>
                {nextPlaceName && (
                  <p className="mt-auto truncate text-[10px] text-stone-400">
                    {t.postcard.nextPlaceLabel}: {nextPlaceName}
                  </p>
                )}
                <p className="mt-auto text-[10px] text-stone-400">
                  {formatDate(postcard.created_at, t.postcard.locale)}
                </p>
              </div>

              <div className="w-px bg-stone-300" />

              <div className="flex w-[42%] flex-col">
                <div className="ml-auto flex h-16 w-14 items-center justify-center border border-dashed border-stone-400 text-[9px] uppercase tracking-widest text-stone-400">
                  Stamp
                </div>
                <div className="mt-auto space-y-4">
                  <div className="h-px bg-stone-400" />
                  <div className="h-px bg-stone-400" />
                  <div className="h-px bg-stone-400" />
                  <div className="h-px bg-stone-400" />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
