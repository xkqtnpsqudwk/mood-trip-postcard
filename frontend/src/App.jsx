import { useState } from "react";
import MoodForm from "./components/MoodForm";
import RecommendationView from "./components/RecommendationView";
import PostcardCreator from "./components/PostcardCreator";
import Postcard from "./components/Postcard";
import ArchiveTab from "./components/ArchiveTab";
import { LanguageProvider, useLanguage } from "./LanguageContext";
import { analyzeMood, createPostcard } from "./api";

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
    <div className="min-h-screen px-4 py-10">
      <header className="relative mx-auto max-w-3xl text-center">
        <div className="absolute right-0 top-0 inline-flex rounded-full bg-white/70 p-1 text-xs font-medium shadow-sm">
          {["ko", "en"].map((code) => (
            <button
              key={code}
              onClick={() => setLang(code)}
              className={`rounded-full px-3 py-1 uppercase transition ${
                lang === code
                  ? "bg-stone-800 text-white"
                  : "text-stone-500 hover:text-stone-700"
              }`}
            >
              {code}
            </button>
          ))}
        </div>

        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-rose-400">
          {t.appTitle}
        </p>
        <h1 className="mt-2 font-[family-name:var(--font-display)] text-4xl text-stone-800">
          {t.appSubtitle}
        </h1>
        <nav className="mt-6 inline-flex rounded-full bg-white/70 p-1 shadow-sm">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`rounded-full px-5 py-2 text-sm font-medium transition ${
                activeTab === tab.id
                  ? "bg-rose-400 text-white shadow"
                  : "text-stone-500 hover:text-stone-700"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </header>

      <main className="mt-10">
        {error && (
          <p className="mx-auto mb-6 w-full max-w-xl rounded-xl bg-rose-50 px-4 py-3 text-center text-sm text-rose-500">
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
                <p className="mb-4 text-center text-sm text-stone-500">
                  {t.postcardArrived}
                </p>
                <Postcard postcard={createdPostcard} defaultFlipped={false} />
                <div className="mt-6 flex justify-center gap-4">
                  <button
                    onClick={resetFlow}
                    className="rounded-xl border border-stone-200 px-5 py-2 text-sm font-medium text-stone-500 hover:bg-white"
                  >
                    {t.planAnother}
                  </button>
                  <button
                    onClick={() => setActiveTab("archive")}
                    className="rounded-xl bg-rose-400 px-5 py-2 text-sm font-medium text-white hover:bg-rose-500"
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
    <LanguageProvider>
      <AppContent />
    </LanguageProvider>
  );
}
