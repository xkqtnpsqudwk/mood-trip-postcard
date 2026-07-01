import { useState } from "react";
import MoodForm from "./components/MoodForm";
import RecommendationView from "./components/RecommendationView";
import PostcardCreator from "./components/PostcardCreator";
import Postcard from "./components/Postcard";
import ArchiveTab from "./components/ArchiveTab";
import { LanguageProvider, useLanguage } from "./LanguageContext";
import { ThemeProvider, useTheme } from "./ThemeContext";
import { analyzeMood, createPostcard } from "./api";

function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === "dark";

  return (
    <button
      onClick={toggleTheme}
      aria-label="Toggle theme"
      className="flex h-7 w-7 items-center justify-center rounded-full text-stone-500 transition hover:text-stone-700 dark:text-fuchsia-300 dark:hover:text-fuchsia-200"
    >
      {isDark ? (
        <svg viewBox="0 0 20 20" fill="currentColor" className="h-4 w-4">
          <path d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4.22 2.05a1 1 0 011.41 0l.71.71a1 1 0 11-1.42 1.41l-.7-.7a1 1 0 010-1.42zM17 9a1 1 0 110 2h-1a1 1 0 110-2h1zM4.22 4.05a1 1 0 000 1.42l.7.7a1 1 0 101.42-1.41l-.71-.71a1 1 0 00-1.41 0zM3 9a1 1 0 100 2H2a1 1 0 100-2h1zm11 4.24a5 5 0 10-8 0A6.98 6.98 0 0110 17a6.98 6.98 0 014-3.76zM5.64 15.36a1 1 0 011.41 0l.01.01a1 1 0 01-1.42 1.42l-.01-.01a1 1 0 010-1.42zm7.31 0a1 1 0 000 1.42l.01.01a1 1 0 001.42-1.42l-.01-.01a1 1 0 00-1.42 0zM10 6a4 4 0 100 8 4 4 0 000-8z" />
        </svg>
      ) : (
        <svg viewBox="0 0 20 20" fill="currentColor" className="h-4 w-4">
          <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
        </svg>
      )}
    </button>
  );
}

function AppContent() {
  const { lang, setLang, t } = useLanguage();
  const [activeTab, setActiveTab] = useState("create");
  const [step, setStep] = useState("form");
  const [city, setCity] = useState("");
  const [analyzeResult, setAnalyzeResult] = useState(null);
  const [selectedPlace, setSelectedPlace] = useState(null);
  const [createdPostcard, setCreatedPostcard] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isCreatingPostcard, setIsCreatingPostcard] = useState(false);
  const [error, setError] = useState(null);
  const [archiveRefreshKey, setArchiveRefreshKey] = useState(0);

  const tabs = [
    { id: "create", label: t.tabCreate },
    { id: "archive", label: t.tabArchive },
  ];

  const resetFlow = () => {
    setStep("form");
    setAnalyzeResult(null);
    setSelectedPlace(null);
    setCreatedPostcard(null);
    setError(null);
  };

  const handleMoodSubmit = async (selectedCity, moodText) => {
    setError(null);
    setIsAnalyzing(true);
    try {
      const result = await analyzeMood(selectedCity, moodText, lang);
      setCity(selectedCity);
      setAnalyzeResult(result);
      setStep("recommend");
    } catch {
      setError(t.errors.analyze);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSelectPlace = (place) => {
    setSelectedPlace(place);
    setStep("review");
  };

  const handleReviewSubmit = async (review) => {
    setError(null);
    setIsCreatingPostcard(true);
    try {
      const postcard = await createPostcard(city, selectedPlace.id, review, lang);
      setCreatedPostcard(postcard);
      setStep("postcard");
      setArchiveRefreshKey((key) => key + 1);
    } catch {
      setError(t.errors.postcard);
    } finally {
      setIsCreatingPostcard(false);
    }
  };

  return (
    <div className="min-h-dvh px-4 py-6 sm:py-10">
      <header className="mx-auto max-w-3xl text-center sm:relative">
        <div className="flex items-center justify-between sm:block">
          <p className="neon-text text-xs font-semibold uppercase tracking-[0.2em] text-rose-400 sm:tracking-[0.3em] dark:text-fuchsia-400">
            {t.appTitle}
          </p>
          <div className="flex items-center gap-2 sm:absolute sm:right-0 sm:top-0">
            <ThemeToggle />
            <div className="inline-flex rounded-full bg-white/70 p-1 text-xs font-medium shadow-md ring-1 ring-white/60 dark:bg-zinc-900/70 dark:shadow-none dark:ring-fuchsia-500/20">
              {["ko", "en"].map((code) => (
                <button
                  key={code}
                  onClick={() => setLang(code)}
                  className={`rounded-full px-3 py-1 uppercase transition ${
                    lang === code
                      ? "bg-stone-800 text-white shadow-[0_2px_10px_rgba(41,37,36,0.35)] dark:bg-fuchsia-500 dark:text-white dark:shadow-none"
                      : "text-stone-500 hover:text-stone-700 dark:text-zinc-400 dark:hover:text-zinc-200"
                  }`}
                >
                  {code}
                </button>
              ))}
            </div>
          </div>
        </div>

        <h1 className="neon-text mt-2 font-[family-name:var(--font-display)] text-3xl text-stone-800 sm:text-4xl dark:text-zinc-100">
          {t.appSubtitle}
        </h1>
        <nav className="mt-6 inline-flex rounded-full bg-white/70 p-1 shadow-md ring-1 ring-white/60 dark:bg-zinc-900/70 dark:shadow-none dark:ring-fuchsia-500/20">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`rounded-full px-5 py-2 text-sm font-medium transition ${
                activeTab === tab.id
                  ? "bg-rose-400 text-white shadow-[0_6px_16px_-2px_rgba(251,113,133,0.55)] dark:bg-fuchsia-500 dark:shadow-[0_0_16px_rgba(232,68,255,0.5)]"
                  : "text-stone-500 hover:text-stone-700 dark:text-zinc-400 dark:hover:text-zinc-200"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </header>

      <main className="mt-8 sm:mt-10">
        {error && (
          <p className="mx-auto mb-6 w-full max-w-xl rounded-xl bg-rose-50 px-4 py-3 text-center text-sm text-rose-500 dark:bg-fuchsia-950/40 dark:text-fuchsia-300 dark:ring-1 dark:ring-fuchsia-500/30">
            {error}
          </p>
        )}

        {activeTab === "create" && (
          <>
            {step === "form" && (
              <MoodForm onSubmit={handleMoodSubmit} isLoading={isAnalyzing} />
            )}
            {step === "recommend" && (
              <RecommendationView
                result={analyzeResult}
                onSelectPlace={handleSelectPlace}
                onStartOver={resetFlow}
              />
            )}
            {step === "review" && selectedPlace && (
              <PostcardCreator
                place={selectedPlace}
                city={city}
                onSubmit={handleReviewSubmit}
                onCancel={() => setStep("recommend")}
                isLoading={isCreatingPostcard}
              />
            )}
            {step === "postcard" && createdPostcard && (
              <div className="mx-auto w-full max-w-md">
                <p className="mb-4 text-center text-sm text-stone-500 dark:text-zinc-400">
                  {t.postcardArrived}
                </p>
                <Postcard postcard={createdPostcard} defaultFlipped={false} />
                <div className="mt-6 flex justify-center gap-4">
                  <button
                    onClick={resetFlow}
                    className="rounded-xl border border-stone-200 px-5 py-2 text-sm font-medium text-stone-500 hover:bg-white dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-900"
                  >
                    {t.planAnother}
                  </button>
                  <button
                    onClick={() => setActiveTab("archive")}
                    className="rounded-xl bg-rose-400 px-5 py-2 text-sm font-medium text-white shadow-[0_8px_20px_-4px_rgba(251,113,133,0.5)] transition hover:bg-rose-500 hover:shadow-[0_8px_24px_-2px_rgba(251,113,133,0.65)] dark:bg-fuchsia-500 dark:hover:bg-fuchsia-400 dark:shadow-[0_0_16px_rgba(232,68,255,0.5)]"
                  >
                    {t.viewArchive}
                  </button>
                </div>
              </div>
            )}
          </>
        )}

        {activeTab === "archive" && <ArchiveTab refreshKey={archiveRefreshKey} />}
      </main>
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <LanguageProvider>
        <AppContent />
      </LanguageProvider>
    </ThemeProvider>
  );
}
