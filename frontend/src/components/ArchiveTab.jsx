import { useEffect, useState } from "react";
import { fetchArchive } from "../api";
import Postcard from "./Postcard";
import SharePanel from "./SharePanel";
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

function groupByTrip(postcards) {
  const tripsById = new Map();
  for (const postcard of postcards) {
    const key = postcard.trip_id || `untitled-${postcard.id}`;
    if (!tripsById.has(key)) {
      tripsById.set(key, []);
    }
    tripsById.get(key).push(postcard);
  }
  const trips = Array.from(tripsById.values()).map((tripPostcards) => {
    const sorted = [...tripPostcards].sort(
      (a, b) => new Date(a.created_at) - new Date(b.created_at)
    );
    return { tripId: sorted[0].trip_id, city: sorted[0].city, postcards: sorted };
  });
  trips.sort(
    (a, b) =>
      new Date(b.postcards[b.postcards.length - 1].created_at) -
      new Date(a.postcards[a.postcards.length - 1].created_at)
  );
  return trips;
}

function PostcardModal({ postcard, onClose }) {
  const { t } = useLanguage();

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="max-h-[92dvh] w-full max-w-lg overflow-y-auto rounded-3xl p-1"
        onClick={(event) => event.stopPropagation()}
      >
        <Postcard postcard={postcard} />
        <SharePanel postcard={postcard} />
        <button
          onClick={onClose}
          className="mx-auto mt-4 block rounded-full bg-white/90 px-5 py-2 text-sm font-medium text-stone-600 shadow-md transition hover:bg-white dark:bg-zinc-900/90 dark:text-zinc-300 dark:ring-1 dark:ring-fuchsia-500/20 dark:hover:bg-zinc-800"
        >
          {t.archive.close}
        </button>
      </div>
    </div>
  );
}

export default function ArchiveTab({ refreshKey }) {
  const { t, lang } = useLanguage();
  const [postcards, setPostcards] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [selectedPostcard, setSelectedPostcard] = useState(null);

  useEffect(() => {
    let isCancelled = false;
    setIsLoading(true);
    setHasError(false);
    fetchArchive(lang)
      .then((data) => {
        if (!isCancelled) setPostcards(data);
      })
      .catch(() => {
        if (!isCancelled) setHasError(true);
      })
      .finally(() => {
        if (!isCancelled) setIsLoading(false);
      });
    return () => {
      isCancelled = true;
    };
  }, [refreshKey, lang]);

  if (isLoading) {
    return (
      <p className="mt-12 text-center text-stone-400 dark:text-zinc-500">
        {t.archive.loading}
      </p>
    );
  }

  if (hasError) {
    return (
      <p className="mt-12 text-center text-rose-400 dark:text-fuchsia-400">
        {t.archive.error}
      </p>
    );
  }

  if (postcards.length === 0) {
    return (
      <p className="mt-12 text-center text-stone-400 dark:text-zinc-500">
        {t.archive.empty}
      </p>
    );
  }

  const trips = groupByTrip(postcards);

  return (
    <>
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-10 xl:max-w-7xl">
        {trips.map((trip) => (
          <section key={trip.tripId}>
            <div className="mb-3 flex flex-wrap items-baseline gap-x-3 gap-y-1 border-b border-stone-200 pb-2 dark:border-zinc-800">
              <h3 className="font-[family-name:var(--font-display)] text-lg text-stone-800 dark:text-zinc-100">
                {t.cities[trip.city] ?? trip.city}
              </h3>
              <span className="text-xs text-stone-400 dark:text-zinc-500">
                {formatDate(trip.postcards[0].created_at, t.postcard.locale)}
              </span>
              <span className="text-xs text-stone-400 dark:text-zinc-500">
                {t.archive.stopsCount(trip.postcards.length)}
              </span>
            </div>
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {trip.postcards.map((postcard) => (
                <Postcard
                  key={postcard.id}
                  postcard={postcard}
                  onOpen={() => setSelectedPostcard(postcard)}
                />
              ))}
            </div>
          </section>
        ))}
      </div>
      {selectedPostcard && (
        <PostcardModal
          postcard={selectedPostcard}
          onClose={() => setSelectedPostcard(null)}
        />
      )}
    </>
  );
}
