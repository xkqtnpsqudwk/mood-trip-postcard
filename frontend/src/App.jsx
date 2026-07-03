import { useEffect, useState } from "react";
import Landing from "./components/Landing";
import MoodForm from "./components/MoodForm";
import RecommendationView from "./components/RecommendationView";
import PostcardCreator from "./components/PostcardCreator";
import Postcard from "./components/Postcard";
import SharePanel from "./components/SharePanel";
import ArchiveTab from "./components/ArchiveTab";
import AuthForm from "./components/AuthForm";
import PersonalizationSettings from "./components/PersonalizationSettings";
import { LanguageProvider, useLanguage } from "./LanguageContext";
import { ThemeProvider, useTheme } from "./ThemeContext";
import { AuthProvider, useAuth } from "./AuthContext";
import {
  analyzeMood,
  createFinalTripPostcard,
  createPostcard,
  updatePostcardNextPlace,
} from "./api";

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

function AccountControl({ onLoginClick }) {
  const { t } = useLanguage();
  const { user, logout } = useAuth();

  if (user) {
    return (
      <div className="inline-flex items-center gap-2 rounded-full bg-white/70 py-1 pl-3 pr-1 text-xs font-medium shadow-md ring-1 ring-white/60 dark:bg-zinc-900/70 dark:shadow-none dark:ring-fuchsia-500/20">
        <span className="text-stone-500 dark:text-zinc-400">{user.username}</span>
        <button
          onClick={logout}
          className="rounded-full px-2 py-1 text-stone-400 hover:text-stone-700 dark:text-zinc-500 dark:hover:text-zinc-200"
        >
          {t.auth.logout}
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={onLoginClick}
      className="rounded-full bg-white/70 px-3 py-1 text-xs font-medium text-stone-500 shadow-md ring-1 ring-white/60 hover:text-stone-700 dark:bg-zinc-900/70 dark:text-zinc-400 dark:ring-fuchsia-500/20 dark:hover:text-zinc-200"
    >
      {t.auth.loginHeading}
    </button>
  );
}

function AppContent() {
  const { lang, setLang, t } = useLanguage();
  const { user, isLoading: isAuthLoading } = useAuth();
  const [view, setView] = useState("landing");
  const [activeTab, setActiveTab] = useState("create");
  const [step, setStep] = useState("form");
  const [city, setCity] = useState("");
  const [analyzeResult, setAnalyzeResult] = useState(null);
  const [selectedPlace, setSelectedPlace] = useState(null);
  const [createdPostcard, setCreatedPostcard] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isCreatingPostcard, setIsCreatingPostcard] = useState(false);
  const [isFinalizingTrip, setIsFinalizingTrip] = useState(false);
  const [error, setError] = useState(null);
  const [archiveRefreshKey, setArchiveRefreshKey] = useState(0);
  const [tripId, setTripId] = useState(null);
  const [visitedPlaceIds, setVisitedPlaceIds] = useState([]);
  const [lastPostcardId, setLastPostcardId] = useState(null);
  const [finalTripPostcard, setFinalTripPostcard] = useState(null);

  useEffect(() => {
    if (!isAuthLoading && user) setView("app");
  }, [isAuthLoading, user]);

  const tabs = [
    { id: "create", label: t.tabCreate },
    { id: "archive", label: t.tabArchive },
    { id: "personalization", label: t.tabPersonalization },
  ];

  const resetFlow = () => {
    setStep("form");
    setAnalyzeResult(null);
    setSelectedPlace(null);
    setCreatedPostcard(null);
    setError(null);
    setTripId(null);
    setVisitedPlaceIds([]);
    setLastPostcardId(null);
    setFinalTripPostcard(null);
  };

  const handleMoodSubmit = async (formState) => {
    setError(null);
    setIsAnalyzing(true);
    try {
      const result = await analyzeMood({ ...formState, language: lang });
      setCity(formState.city);
      setAnalyzeResult(result);
      setTripId(crypto.randomUUID());
      setVisitedPlaceIds([]);
      setStep("recommend");
    } catch {
      setError(t.errors.analyze);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSelectPlace = (place) => {
    setSelectedPlace(place);
    setStep(user ? "review" : "loginRequired");
  };

  const handleReviewSubmit = async (review, photoBase64List = null) => {
    setError(null);
    setIsCreatingPostcard(true);
    try {
      const postcard = await createPostcard(
        city,
        selectedPlace.id,
        review,
        lang,
        tripId,
        photoBase64List
      );
      if (lastPostcardId) {
        try {
          // Now that we know where the traveler actually went next, backfill
          // the previous postcard's next-stop instead of showing a guess.
          await updatePostcardNextPlace(lastPostcardId, selectedPlace.id, lang);
        } catch {
          // Best-effort: the previous postcard just won't show a next stop.
        }
      }
      setCreatedPostcard(postcard);
      setLastPostcardId(postcard.id);
      setVisitedPlaceIds((ids) => [...ids, selectedPlace.id]);
      setStep("postcard");
      setArchiveRefreshKey((key) => key + 1);
    } catch {
      setError(t.errors.postcard);
    } finally {
      setIsCreatingPostcard(false);
    }
  };

  const handleContinueTrip = () => {
    setSelectedPlace(null);
    setCreatedPostcard(null);
    setStep("recommend");
  };

  const handleEndTrip = async () => {
    if (!tripId) {
      resetFlow();
      setActiveTab("archive");
      return;
    }

    setError(null);
    setIsFinalizingTrip(true);
    try {
      const finalPostcard = await createFinalTripPostcard(tripId, lang);
      setFinalTripPostcard(finalPostcard);
      setCreatedPostcard(null);
      setSelectedPlace(null);
      setStep("tripFinale");
      setActiveTab("create");
    } catch {
      setError(t.errors.finalPostcard);
    } finally {
      setIsFinalizingTrip(false);
    }
  };

  const handleDismissRecommendations = () => {
    resetFlow();
    setView("landing");
  };

  const hasRemainingStops = (analyzeResult?.places || []).some(
    (place) => !visitedPlaceIds.includes(place.id)
  );

  if (view === "landing") {
    return (
      <div className="flex min-h-dvh items-center justify-center px-4 py-10">
        <Landing onContinue={() => setView("app")} />
      </div>
    );
  }

  return (
    <div className="min-h-dvh px-4 py-6 sm:py-10">
      <header className="mx-auto max-w-3xl text-center sm:relative">
        <div className="flex items-center justify-between sm:block">
          <p className="neon-text text-xs font-semibold uppercase tracking-[0.2em] text-rose-400 sm:tracking-[0.3em] dark:text-fuchsia-400">
            {t.appTitle}
          </p>
          <div className="flex items-center gap-2 sm:absolute sm:right-0 sm:-top-2">
            <AccountControl onLoginClick={() => setActiveTab("personalization")} />
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

        <h1 className="neon-text mt-5 font-[family-name:var(--font-display)] text-3xl text-stone-800 sm:mt-6 sm:text-4xl dark:text-zinc-100">
          {t.appSubtitle}
        </h1>
        <nav className="mt-7 inline-flex rounded-full bg-white/70 p-1 shadow-md ring-1 ring-white/60 dark:bg-zinc-900/70 dark:shadow-none dark:ring-fuchsia-500/20">
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
              <MoodForm
                onSubmit={handleMoodSubmit}
                isLoading={isAnalyzing}
                onOpenPersonalization={() => setActiveTab("personalization")}
              />
            )}
            {step === "recommend" && (
              <RecommendationView
                result={analyzeResult}
                visitedPlaceIds={visitedPlaceIds}
                isContinuation={visitedPlaceIds.length > 0}
                requireLogin={!user}
                onSelectPlace={handleSelectPlace}
                onStartOver={resetFlow}
                onEndTrip={handleEndTrip}
                isEndingTrip={isFinalizingTrip}
                onDismiss={handleDismissRecommendations}
              />
            )}
            {step === "loginRequired" && selectedPlace && (
              <div className="mx-auto w-full max-w-md">
                <p className="mb-4 text-center text-sm text-stone-500 dark:text-zinc-400">
                  {t.auth.postcardLoginPrompt}
                </p>
                <AuthForm onSuccess={() => setStep("review")} />
                <button
                  onClick={() => setStep("recommend")}
                  className="mx-auto mt-4 block text-center text-sm font-medium text-stone-500 underline-offset-4 hover:text-stone-700 hover:underline dark:text-zinc-400 dark:hover:text-zinc-200"
                >
                  {t.postcardCreator.back}
                </button>
              </div>
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
                <div className="mt-6 flex flex-wrap justify-center gap-3">
                  {hasRemainingStops && (
                    <button
                      onClick={handleContinueTrip}
                      className="rounded-xl bg-rose-400 px-5 py-2 text-sm font-medium text-white shadow-[0_8px_20px_-4px_rgba(251,113,133,0.5)] transition hover:bg-rose-500 hover:shadow-[0_8px_24px_-2px_rgba(251,113,133,0.65)] dark:bg-fuchsia-500 dark:hover:bg-fuchsia-400 dark:shadow-[0_0_16px_rgba(232,68,255,0.5)]"
                    >
                      {t.findNextStop}
                    </button>
                  )}
                  <button
                    onClick={handleEndTrip}
                    disabled={isFinalizingTrip}
                    className="rounded-xl border border-stone-200 px-5 py-2 text-sm font-medium text-stone-500 hover:bg-white dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-900"
                  >
                    {isFinalizingTrip ? t.finalPostcard.loading : t.endTrip}
                  </button>
                  <button
                    onClick={resetFlow}
                    className="rounded-xl border border-stone-200 px-5 py-2 text-sm font-medium text-stone-500 hover:bg-white dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-900"
                  >
                    {t.planAnother}
                  </button>
                </div>
              </div>
            )}
            {step === "tripFinale" && finalTripPostcard && (
              <div className="mx-auto w-full max-w-md">
                <p className="mb-2 text-center text-sm font-medium text-stone-600 dark:text-zinc-300">
                  {t.finalPostcard.heading}
                </p>
                <p className="mb-4 text-center text-sm text-stone-500 dark:text-zinc-400">
                  {t.finalPostcard.subheading}
                </p>
                <Postcard postcard={finalTripPostcard} defaultFlipped={false} />
                <SharePanel postcard={finalTripPostcard} compact />
                <div className="mt-6 flex flex-wrap justify-center gap-3">
                  <button
                    onClick={() => {
                      resetFlow();
                      setActiveTab("archive");
                    }}
                    className="rounded-xl border border-stone-200 px-5 py-2 text-sm font-medium text-stone-500 hover:bg-white dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-900"
                  >
                    {t.viewArchive}
                  </button>
                  <button
                    onClick={resetFlow}
                    className="rounded-xl bg-rose-400 px-5 py-2 text-sm font-medium text-white shadow-[0_8px_20px_-4px_rgba(251,113,133,0.5)] transition hover:bg-rose-500 hover:shadow-[0_8px_24px_-2px_rgba(251,113,133,0.65)] dark:bg-fuchsia-500 dark:hover:bg-fuchsia-400 dark:shadow-[0_0_16px_rgba(232,68,255,0.5)]"
                  >
                    {t.planAnother}
                  </button>
                </div>
              </div>
            )}
          </>
        )}

        {activeTab === "archive" && <ArchiveTab refreshKey={archiveRefreshKey} />}

        {activeTab === "personalization" &&
          (user ? (
            <PersonalizationSettings />
          ) : (
            <div className="mx-auto w-full max-w-md">
              <p className="mb-4 text-center text-sm text-stone-500 dark:text-zinc-400">
                {t.personalization.loginRequired}
              </p>
              <AuthForm />
            </div>
          ))}
      </main>
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <LanguageProvider>
        <AuthProvider>
          <AppContent />
        </AuthProvider>
      </LanguageProvider>
    </ThemeProvider>
  );
}
