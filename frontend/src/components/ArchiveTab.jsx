import { useEffect, useState } from "react";
import { fetchArchive } from "../api";
import Postcard from "./Postcard";
import { useLanguage } from "../LanguageContext";

export default function ArchiveTab({ refreshKey }) {
  const { t, lang } = useLanguage();
  const [postcards, setPostcards] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

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
    <div className="mx-auto grid w-full max-w-5xl gap-6 sm:grid-cols-2 lg:max-w-6xl lg:grid-cols-3 xl:max-w-7xl xl:grid-cols-4">
      {postcards.map((postcard) => (
        <Postcard key={postcard.id} postcard={postcard} />
      ))}
    </div>
  );
}
