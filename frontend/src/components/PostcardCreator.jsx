import { useState } from "react";
import { useLanguage } from "../LanguageContext";

const localized = (value, lang) => {
  if (value && typeof value === "object") {
    return value[lang] ?? value.en ?? value.ko ?? "";
  }
  return value ?? "";
};

const MAX_PHOTOS = 4;

function readFileAsDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

async function createPhotoPayload(files) {
  if (!files.length) return null;
  return Promise.all(files.slice(0, MAX_PHOTOS).map(readFileAsDataUrl));
}

export default function PostcardCreator({ place, city, onSubmit, onCancel, isLoading }) {
  const { t, lang } = useLanguage();
  const [review, setReview] = useState("");
  const [photos, setPhotos] = useState([]);
  const [photoError, setPhotoError] = useState("");
  const [isPreparingCollage, setIsPreparingCollage] = useState(false);
  const placeName = localized(place.name_i18n, lang) || place.name;
  const isSubmitting = isLoading || isPreparingCollage;

  const handlePhotoChange = (event) => {
    const selected = Array.from(event.target.files || []);
    setPhotoError("");
    setPhotos(selected.slice(0, MAX_PHOTOS));
    if (selected.length > MAX_PHOTOS) {
      setPhotoError(t.postcardCreator.photoLimit);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!review.trim() || isSubmitting) return;
    setIsPreparingCollage(true);
    let photoBase64List = null;
    try {
      photoBase64List = await createPhotoPayload(photos);
    } catch {
      setPhotoError(t.postcardCreator.photoError);
      setIsPreparingCollage(false);
      return;
    }

    try {
      await onSubmit(review.trim(), photoBase64List);
    } finally {
      setIsPreparingCollage(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="mx-auto w-full max-w-xl rounded-3xl bg-white/80 p-6 shadow-[0_25px_60px_-15px_rgba(251,113,133,0.35)] ring-1 ring-rose-100/80 backdrop-blur sm:p-8 dark:bg-zinc-950/70 dark:shadow-[0_24px_60px_-24px_rgba(217,70,239,0.42)] dark:ring-fuchsia-500/20"
    >
      <p className="text-xs font-semibold uppercase tracking-widest text-rose-400 dark:text-fuchsia-300">
        {t.cities[city] ?? city} &middot; {placeName}
      </p>
      <h2 className="mt-1 font-[family-name:var(--font-display)] text-2xl text-stone-800 dark:text-zinc-100">
        {t.postcardCreator.heading}
      </h2>
      <p className="mt-1 text-sm text-stone-500 dark:text-zinc-400">
        {t.postcardCreator.subheading}
      </p>

      <textarea
        value={review}
        onChange={(event) => setReview(event.target.value)}
        placeholder={t.postcardCreator.placeholder}
        rows={4}
        className="mt-6 w-full resize-none rounded-xl border border-stone-200 bg-white px-4 py-3 text-stone-800 outline-none focus:border-rose-300 focus:ring-2 focus:ring-rose-100 dark:border-zinc-700/80 dark:bg-zinc-900/75 dark:text-zinc-100 dark:placeholder:text-zinc-500 dark:focus:border-fuchsia-400/70 dark:focus:ring-fuchsia-500/20"
      />

      <div className="mt-5">
        <label className="block text-xs font-semibold uppercase tracking-widest text-stone-400 dark:text-zinc-500">
          {t.postcardCreator.photoLabel}
        </label>
        <p className="mt-1 text-sm leading-relaxed text-stone-500 dark:text-zinc-400">
          {t.postcardCreator.photoHint}
        </p>
        <label className="mt-3 flex cursor-pointer flex-col items-center justify-center rounded-2xl border border-dashed border-rose-200 bg-rose-50/50 px-4 py-5 text-center text-sm text-rose-500 transition hover:bg-rose-50 dark:border-fuchsia-500/30 dark:bg-fuchsia-950/15 dark:text-fuchsia-200 dark:hover:bg-fuchsia-950/25">
          <span>{t.postcardCreator.photoButton}</span>
          <input
            type="file"
            accept="image/*"
            multiple
            onChange={handlePhotoChange}
            disabled={isSubmitting}
            className="sr-only"
          />
        </label>
        {photos.length > 0 && (
          <div className="mt-3 grid grid-cols-4 gap-2">
            {photos.map((photo) => (
              <div
                key={`${photo.name}-${photo.lastModified}`}
                className="truncate rounded-lg bg-white px-2 py-1 text-[11px] text-stone-500 ring-1 ring-stone-200 dark:bg-zinc-900 dark:text-zinc-400 dark:ring-zinc-700"
                title={photo.name}
              >
                {photo.name}
              </div>
            ))}
          </div>
        )}
        {photoError && (
          <p className="mt-2 text-xs text-rose-500 dark:text-fuchsia-300">{photoError}</p>
        )}
      </div>

      <div className="mt-6 flex gap-3">
        <button
          type="button"
          onClick={onCancel}
          disabled={isSubmitting}
          className="flex-1 rounded-xl border border-stone-200 px-6 py-3 font-medium text-stone-500 transition hover:bg-stone-50 disabled:cursor-not-allowed dark:border-zinc-700/80 dark:bg-zinc-900/40 dark:text-zinc-300 dark:hover:border-fuchsia-500/30 dark:hover:bg-zinc-900"
        >
          {t.postcardCreator.back}
        </button>
        <button
          type="submit"
          disabled={isSubmitting || !review.trim()}
          className="flex-[2] rounded-xl bg-rose-400 px-6 py-3 font-medium text-white shadow-[0_8px_20px_-4px_rgba(251,113,133,0.5)] transition hover:bg-rose-500 hover:shadow-[0_8px_24px_-2px_rgba(251,113,133,0.65)] disabled:cursor-not-allowed disabled:bg-stone-300 disabled:shadow-none dark:bg-fuchsia-500 dark:shadow-[0_12px_28px_-10px_rgba(217,70,239,0.75)] dark:hover:bg-fuchsia-400 dark:hover:shadow-[0_14px_32px_-10px_rgba(217,70,239,0.85)] dark:disabled:bg-zinc-700 dark:disabled:shadow-none"
        >
          {isSubmitting ? t.postcardCreator.loading : t.postcardCreator.submit}
        </button>
      </div>
      {isSubmitting && (
        <p className="mt-4 rounded-xl bg-stone-50 px-4 py-3 text-center text-sm leading-relaxed text-stone-500 ring-1 ring-stone-100 dark:bg-zinc-950/50 dark:text-zinc-300 dark:ring-fuchsia-500/20">
          {t.postcardCreator.loadingHint}
        </p>
      )}
    </form>
  );
}
