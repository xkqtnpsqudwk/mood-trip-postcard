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
  const trips = Array.from(tripsById.entries()).map(([key, tripPostcards]) => {
    const sorted = [...tripPostcards].sort(
      (a, b) => new Date(a.created_at) - new Date(b.created_at)
    );
    return { tripId: sorted[0].trip_id, key, city: sorted[0].city, postcards: sorted };
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
  const isRecord = (postcard.artifact_type || "record") === "record";

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
        {!isRecord && <SharePanel postcard={postcard} />}
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
  const [archiveType, setArchiveType] = useState("records");
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

  const recordTrips = groupByTrip(
    postcards.filter((postcard) => (postcard.artifact_type || "record") === "record")
  );
  const finalPostcards = postcards.filter(
    (postcard) => postcard.artifact_type === "postcard"
  );
  const archiveTabs = [
    {
      id: "records",
      label: t.archive.recordsHeading,
      count: recordTrips.reduce((sum, trip) => sum + trip.postcards.length, 0),
    },
    {
      id: "postcards",
      label: t.archive.postcardsHeading,
      count: finalPostcards.length,
    },
  ];

  return (
    <>
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 xl:max-w-7xl">
        <div className="flex justify-center">
          <div className="inline-flex max-w-full overflow-x-auto rounded-full bg-white/80 p-1 text-sm font-medium shadow-md ring-1 ring-rose-100/80 dark:bg-zinc-950/70 dark:shadow-none dark:ring-fuchsia-500/20">
            {archiveTabs.map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setArchiveType(tab.id)}
                className={`shrink-0 rounded-full px-5 py-2 transition ${
                  archiveType === tab.id
                    ? "bg-rose-400 text-white shadow-[0_6px_16px_-2px_rgba(251,113,133,0.55)] dark:bg-fuchsia-500 dark:shadow-[0_0_16px_rgba(232,68,255,0.42)]"
                    : "text-stone-500 hover:text-stone-700 dark:text-zinc-400 dark:hover:text-zinc-200"
                }`}
              >
                {tab.label}
                <span className="ml-2 text-xs opacity-75">{tab.count}</span>
              </button>
            ))}
          </div>
        </div>

        {archiveType === "records" && (
          <section>
            <div className="mb-4 border-b border-stone-200 pb-2 dark:border-zinc-800">
              <h2 className="font-[family-name:var(--font-display)] text-xl text-stone-800 dark:text-zinc-100">
                {t.archive.recordsHeading}
              </h2>
              <p className="mt-1 text-sm text-stone-400 dark:text-zinc-500">
                {t.archive.recordsSubheading}
              </p>
            </div>
            {recordTrips.length > 0 ? (
              <div className="flex flex-col gap-10">
                {recordTrips.map((trip) => (
                  <section key={trip.key}>
                    <div className="mb-3 flex flex-wrap items-baseline gap-x-3 gap-y-1 border-b border-stone-200 pb-2 dark:border-zinc-800">
                      <h3 className="font-[family-name:var(--font-display)] text-lg text-stone-800 dark:text-zinc-100">
                        {t.cities[trip.city] ?? trip.city}
                      </h3>
                      <span className="text-xs text-stone-400 dark:text-zinc-500">
                        {formatDate(trip.postcards[0].created_at, t.postcard.locale)}
                      </span>
                      <span className="text-xs text-stone-400 dark:text-zinc-500">
                        {t.archive.recordsCount(trip.postcards.length)}
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
            ) : (
              <p className="mt-12 text-center text-stone-400 dark:text-zinc-500">
                {t.archive.recordsEmpty}
              </p>
            )}
          </section>
        )}

        {archiveType === "postcards" && (
          <section>
            <div className="mb-3 flex flex-wrap items-baseline gap-x-3 gap-y-1 border-b border-stone-200 pb-2 dark:border-zinc-800">
              <h2 className="font-[family-name:var(--font-display)] text-xl text-stone-800 dark:text-zinc-100">
                {t.archive.postcardsHeading}
              </h2>
              <span className="text-xs text-stone-400 dark:text-zinc-500">
                {t.archive.postcardsCount(finalPostcards.length)}
              </span>
            </div>
            {finalPostcards.length > 0 ? (
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {finalPostcards.map((postcard) => (
                  <Postcard
                    key={postcard.id}
                    postcard={postcard}
                    onOpen={() => setSelectedPostcard(postcard)}
                  />
                ))}
              </div>
            ) : (
              <p className="mt-12 text-center text-stone-400 dark:text-zinc-500">
                {t.archive.postcardsEmpty}
              </p>
            )}
          </section>
        )}
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
