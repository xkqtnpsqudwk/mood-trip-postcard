import { useEffect, useState } from "react";
import { useLanguage } from "../LanguageContext";
import { fetchPreferences, savePreferences } from "../api";

export default function PersonalizationSettings() {
  const { t } = useLanguage();
  const p = t.personalization;

  const [styleText, setStyleText] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [justSaved, setJustSaved] = useState(false);

  useEffect(() => {
    let isCancelled = false;
    fetchPreferences()
      .then((data) => {
        if (isCancelled) return;
        setStyleText(data.style_text || "");
      })
      .catch(() => {});
    return () => {
      isCancelled = true;
    };
  }, []);

  const handleSave = async () => {
    setIsSaving(true);
    setJustSaved(false);
    try {
      await savePreferences(styleText.trim());
      setJustSaved(true);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="mx-auto w-full max-w-xl rounded-3xl bg-white/80 p-6 shadow-[0_25px_60px_-15px_rgba(244,114,182,0.35)] ring-1 ring-rose-100/80 backdrop-blur sm:p-8 dark:bg-zinc-950/65 dark:shadow-[0_0_40px_rgba(217,70,239,0.14)] dark:ring-fuchsia-500/20">
      <h2 className="font-[family-name:var(--font-display)] text-2xl text-stone-800 dark:text-zinc-100">
        {p.heading}
      </h2>
      <p className="mt-1 text-sm text-stone-500 dark:text-zinc-400">{p.subheading}</p>

      <textarea
        value={styleText}
        onChange={(event) => setStyleText(event.target.value)}
        placeholder={p.placeholder}
        rows={6}
        className="mt-6 w-full resize-none rounded-xl border border-stone-200 bg-white px-4 py-3 text-stone-800 outline-none focus:border-rose-300 focus:ring-2 focus:ring-rose-100 dark:border-fuchsia-500/20 dark:bg-zinc-950/50 dark:text-zinc-100 dark:placeholder:text-zinc-500 dark:focus:border-fuchsia-400 dark:focus:ring-fuchsia-500/30"
      />

      <button
        type="button"
        onClick={handleSave}
        disabled={isSaving}
        className="mt-6 w-full rounded-xl bg-rose-400 px-6 py-3 font-medium text-white shadow-[0_8px_20px_-4px_rgba(251,113,133,0.5)] transition hover:bg-rose-500 hover:shadow-[0_8px_24px_-2px_rgba(251,113,133,0.65)] disabled:cursor-not-allowed disabled:bg-stone-300 disabled:shadow-none dark:bg-fuchsia-500 dark:hover:bg-fuchsia-400 dark:shadow-[0_0_20px_rgba(232,68,255,0.5)] dark:disabled:bg-zinc-700 dark:disabled:shadow-none"
      >
        {isSaving ? p.saving : p.save}
      </button>
      {justSaved && (
        <p className="mt-3 text-center text-xs text-emerald-500 dark:text-emerald-400">
          {p.saved}
        </p>
      )}
    </div>
  );
}
