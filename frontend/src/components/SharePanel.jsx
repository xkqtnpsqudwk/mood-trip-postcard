import { useMemo, useState } from "react";
import { useLanguage } from "../LanguageContext";

const localized = (value, lang) => {
  if (value && typeof value === "object") {
    return value[lang] ?? value.en ?? value.ko ?? "";
  }
  return value ?? "";
};

function shareFileName(postcard) {
  return `moodtrip-${postcard.id || postcard.trip_id || "trip"}.jpg`;
}

export default function SharePanel({ postcard, compact = false }) {
  const { t, lang } = useLanguage();
  const [status, setStatus] = useState("");

  const shareData = useMemo(() => {
    const placeName = localized(postcard.place_name_i18n, lang) || postcard.place_name;
    const title = localized(postcard.title_i18n, lang) || postcard.title;
    const message = localized(postcard.message_i18n, lang) || postcard.message;
    const cityName = t.cities[postcard.city] ?? postcard.city;
    const review = postcard.review || "";
    const moodText = postcard.mood_text || "";
    const clue = localized(postcard.clue_i18n, lang) || "";
    const caption = t.share.caption({
      title,
      city: cityName,
      place: placeName,
      message,
      review,
      moodText,
      clue,
    });
    return { placeName, title, message, cityName, review, moodText, clue, caption };
  }, [lang, postcard, t]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(shareData.caption);
      setStatus(t.share.copied);
    } catch {
      setStatus(t.share.copyFailed);
    }
  };

  const handleDownload = async () => {
    if (!postcard.image_url) return;
    setStatus(t.share.downloading);
    try {
      const response = await fetch(postcard.image_url);
      const blob = await response.blob();
      const objectUrl = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = objectUrl;
      link.download = shareFileName(postcard);
      link.click();
      URL.revokeObjectURL(objectUrl);
      setStatus(t.share.downloaded);
    } catch {
      setStatus(t.share.downloadFailed);
    }
  };

  const handleNativeShare = async () => {
    if (!navigator.share) return;
    const shareText = {
      title: `${shareData.cityName} / ${shareData.placeName}`,
      text: shareData.caption,
    };
    try {
      if (postcard.image_url && navigator.canShare) {
        try {
          const response = await fetch(postcard.image_url);
          const blob = await response.blob();
          const file = new File([blob], shareFileName(postcard), {
            type: blob.type || "image/jpeg",
          });
          if (navigator.canShare({ files: [file] })) {
            await navigator.share({ ...shareText, files: [file] });
            setStatus(t.share.shared);
            return;
          }
        } catch {
          // Fall back to a text-only share below.
        }
      }
      await navigator.share(shareText);
      setStatus(t.share.shared);
    } catch {
      setStatus("");
    }
  };

  return (
    <section
      className={`rounded-2xl border border-rose-100 bg-white/90 p-4 shadow-sm dark:border-fuchsia-500/20 dark:bg-zinc-950/80 ${
        compact ? "mt-4" : "mt-5"
      }`}
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-rose-400 dark:text-fuchsia-300">
            {t.share.label}
          </p>
          <h3 className="mt-1 text-sm font-semibold text-stone-800 dark:text-zinc-100">
            {t.share.heading}
          </h3>
        </div>
        <span className="rounded-full bg-rose-50 px-3 py-1 text-[11px] font-medium text-rose-500 dark:bg-fuchsia-950/50 dark:text-fuchsia-200">
          MoodTrip
        </span>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={handleDownload}
          className="rounded-xl bg-rose-400 px-4 py-2 text-xs font-medium text-white shadow-[0_8px_18px_-6px_rgba(251,113,133,0.6)] transition hover:bg-rose-500 dark:bg-fuchsia-500 dark:hover:bg-fuchsia-400"
        >
          {t.share.download}
        </button>
        <button
          type="button"
          onClick={handleCopy}
          className="rounded-xl border border-stone-200 px-4 py-2 text-xs font-medium text-stone-500 transition hover:bg-white dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-900"
        >
          {t.share.copy}
        </button>
        {typeof navigator !== "undefined" && navigator.share && (
          <button
            type="button"
            onClick={handleNativeShare}
            className="rounded-xl border border-stone-200 px-4 py-2 text-xs font-medium text-stone-500 transition hover:bg-white dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-900"
          >
            {t.share.native}
          </button>
        )}
      </div>
      {status && (
        <p className="mt-2 text-xs text-stone-400 dark:text-zinc-500">{status}</p>
      )}
    </section>
  );
}
