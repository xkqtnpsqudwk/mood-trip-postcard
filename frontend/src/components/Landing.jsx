import { useState } from "react";
import { useLanguage } from "../LanguageContext";
import AuthForm from "./AuthForm";

export default function Landing({ onContinue }) {
  const { t } = useLanguage();
  const [showAuth, setShowAuth] = useState(false);

  if (showAuth) {
    return (
      <div>
        <AuthForm onSuccess={onContinue} />
        <button
          type="button"
          onClick={() => setShowAuth(false)}
          className="mx-auto mt-4 block text-center text-sm text-stone-400 underline-offset-4 hover:text-stone-600 hover:underline dark:text-zinc-500 dark:hover:text-zinc-300"
        >
          {t.landing.backToIntro}
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-2xl text-center">
      <h1 className="font-[family-name:var(--font-display)] text-4xl text-stone-800 sm:text-5xl dark:text-zinc-100">
        {t.landing.title}
      </h1>
      <p className="mt-3 text-lg text-rose-400 dark:text-fuchsia-400">{t.landing.tagline}</p>
      <p className="mx-auto mt-6 max-w-xl text-stone-600 dark:text-zinc-300">
        {t.landing.description}
      </p>
      <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
        <button
          type="button"
          onClick={onContinue}
          className="rounded-xl border border-stone-200 px-6 py-3 font-medium text-stone-600 transition hover:bg-white dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-900"
        >
          {t.landing.startGuestCta}
        </button>
        <button
          type="button"
          onClick={() => setShowAuth(true)}
          className="rounded-xl bg-rose-400 px-6 py-3 font-medium text-white shadow-[0_8px_20px_-4px_rgba(251,113,133,0.5)] transition hover:bg-rose-500 hover:shadow-[0_8px_24px_-2px_rgba(251,113,133,0.65)] dark:bg-fuchsia-500 dark:hover:bg-fuchsia-400 dark:shadow-[0_0_20px_rgba(232,68,255,0.5)]"
        >
          {t.landing.loginCta}
        </button>
      </div>
    </div>
  );
}
