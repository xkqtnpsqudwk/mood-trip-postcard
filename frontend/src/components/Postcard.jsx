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
  const title = localized(postcard.title_i18n, lang) || postcard.title;
  const message = localized(postcard.message_i18n, lang) || postcard.message;

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
        <div className="postcard-face absolute inset-0 flex flex-col justify-between rounded-2xl bg-gradient-to-br from-amber-50 via-rose-50 to-rose-200 p-6 shadow-[0_20px_45px_-12px_rgba(251,113,133,0.4)] ring-1 ring-white/60 dark:from-fuchsia-950/60 dark:via-transparent dark:to-cyan-950/40 dark:ring-fuchsia-500/20 dark:shadow-[0_0_30px_rgba(168,85,247,0.2)]">
          <p className="text-[10px] font-semibold uppercase tracking-widest text-rose-400 dark:text-fuchsia-400">
            {t.cities[postcard.city] ?? postcard.city} &middot; {placeName}
          </p>
          <div>
            <h3 className="font-[family-name:var(--font-display)] text-xl text-stone-800 dark:text-cyan-100">
              {title}
            </h3>
            <p className="mt-2 line-clamp-4 text-sm italic text-stone-600 dark:text-zinc-300">
              {message}
            </p>
          </div>
          <p className="text-[10px] text-stone-400 dark:text-zinc-500">
            {onOpen ? t.postcard.tapToOpen : t.postcard.tapToFlip}
          </p>
        </div>

        <div className="postcard-face postcard-face-back absolute inset-0 overflow-hidden rounded-2xl shadow-[0_20px_45px_-12px_rgba(167,139,250,0.4)] ring-1 ring-white/60 dark:ring-cyan-500/20 dark:shadow-[0_0_30px_rgba(34,211,238,0.2)]">
          {postcard.image_base64 ? (
            <>
              <img
                src={`data:image/jpeg;base64,${postcard.image_base64}`}
                alt={title}
                className="h-full w-full object-cover"
              />
              <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/70 to-transparent px-4 py-3">
                <p className="line-clamp-2 text-xs text-white/90">{postcard.review}</p>
                <p className="mt-1 text-right text-[10px] text-white/70">
                  {formatDate(postcard.created_at, t.postcard.locale)}
                </p>
              </div>
            </>
          ) : (
            <div className="flex h-full w-full flex-col justify-between bg-white p-6 dark:bg-zinc-900">
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-widest text-violet-400 dark:text-cyan-400">
                  {t.postcard.myReview}
                </p>
                <p className="mt-2 text-sm text-stone-600 dark:text-zinc-300">
                  {postcard.review}
                </p>
              </div>
              <p className="text-right text-[10px] text-stone-400 dark:text-zinc-500">
                {formatDate(postcard.created_at, t.postcard.locale)}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
