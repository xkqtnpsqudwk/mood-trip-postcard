import { useEffect, useState } from "react";
import { fetchArchive } from "../api";
import Postcard from "./Postcard";
import { useLanguage } from "../LanguageContext";

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
      <div className="w-full max-w-lg" onClick={(event) => event.stopPropagation()}>
        <Postcard postcard={postcard} />
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

  return (
    <>
      <div className="mx-auto grid w-full max-w-5xl gap-6 sm:grid-cols-2 lg:max-w-6xl lg:grid-cols-3 xl:max-w-7xl xl:grid-cols-4">
        {postcards.map((postcard) => (
          <Postcard
            key={postcard.id}
            postcard={postcard}
            onOpen={() => setSelectedPostcard(postcard)}
          />
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
