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

export default function Postcard({ postcard, defaultFlipped = false }) {
  const { t } = useLanguage();
  const [isFlipped, setIsFlipped] = useState(defaultFlipped);

  return (
    <div
      className={`postcard-flip aspect-[3/2] w-full cursor-pointer ${isFlipped ? "is-flipped" : ""}`}
      onClick={() => setIsFlipped((flipped) => !flipped)}
    >
      <div className="postcard-flip-inner relative h-full w-full">
        <div className="postcard-face absolute inset-0 flex flex-col justify-between rounded-2xl bg-gradient-to-br from-amber-50 to-rose-100 p-6 shadow-lg ring-1 ring-stone-200">
          <p className="text-[10px] font-semibold uppercase tracking-widest text-rose-400">
            {t.cities[postcard.city] ?? postcard.city} &middot; {postcard.place_name}
          </p>
          <div>
            <h3 className="font-[family-name:var(--font-display)] text-xl text-stone-800">
              {postcard.title}
            </h3>
            <p className="mt-2 line-clamp-4 text-sm italic text-stone-600">
              {postcard.message}
            </p>
          </div>
          <p className="text-[10px] text-stone-400">{t.postcard.tapToFlip}</p>
        </div>

        <div className="postcard-face postcard-face-back absolute inset-0 overflow-hidden rounded-2xl shadow-lg ring-1 ring-stone-200">
          {postcard.image_base64 ? (
            <>
              <img
                src={`data:image/jpeg;base64,${postcard.image_base64}`}
                alt={postcard.title}
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
            <div className="flex h-full w-full flex-col justify-between bg-white p-6">
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-widest text-violet-400">
                  {t.postcard.myReview}
                </p>
                <p className="mt-2 text-sm text-stone-600">{postcard.review}</p>
              </div>
              {postcard.next_recommendation && (
                <p className="text-xs text-stone-500">
                  {t.postcard.nextStop}{" "}
                  <span className="font-medium">{postcard.next_recommendation}</span>
                </p>
              )}
              <p className="text-right text-[10px] text-stone-400">
                {formatDate(postcard.created_at, t.postcard.locale)}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
