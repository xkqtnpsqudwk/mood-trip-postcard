import { useState } from "react";
import { useLanguage } from "../LanguageContext";

const CITY_KEYS = ["Paris", "Seoul"];
const COMPANIONS = ["solo", "friends", "couple", "family"];
const AVAILABLE_TIME = ["under_30min", "1h", "2_3h", "half_day"];
const MOBILITY = ["near", "moderate_walk", "far_walk"];
const ENVIRONMENT = ["indoor", "outdoor", "any"];
const SITUATION_AVOID = ["crowded", "far", "expensive", "complex_route"];
const EMOTIONS = ["calm", "excited", "tired", "depressed", "stuffy", "relaxed", "curious", "energetic"];
const EMOTION_INTENSITY = ["weak", "medium", "strong"];
const ACTIVITY_PREFERENCES = ["walking", "photo", "cafe", "exhibition", "shopping", "reading", "night_view", "history"];
const ATMOSPHERE_PREFERENCES = ["quiet", "sentimental", "lively", "exotic", "natural", "local", "artistic"];
const PLACE_PREFERENCES = ["riverside", "park", "alley", "bookstore", "gallery", "market", "viewpoint"];
const PREFERENCE_AVOID = ["crowded", "long_wait", "expensive", "long_distance", "too_touristy"];

function chipClass(isSelected) {
  return `rounded-full px-3 py-1.5 text-xs font-medium transition ${
    isSelected
      ? "bg-rose-400 text-white shadow-[0_4px_12px_-2px_rgba(251,113,133,0.5)] dark:bg-fuchsia-500 dark:shadow-[0_0_12px_rgba(232,68,255,0.5)]"
      : "bg-white text-stone-500 ring-1 ring-stone-200 hover:bg-stone-50 dark:bg-zinc-950/50 dark:text-zinc-400 dark:ring-fuchsia-500/20 dark:hover:bg-zinc-900"
  }`;
}

function ChipGroup({ options, labels, selected, onSelect, multi = false }) {
  const isSelected = (opt) => (multi ? selected.includes(opt) : selected === opt);
  return (
    <div className="mt-2 flex flex-wrap gap-2">
      {options.map((opt) => (
        <button
          type="button"
          key={opt}
          onClick={() => onSelect(opt)}
          className={chipClass(isSelected(opt))}
        >
          {labels[opt] ?? opt}
        </button>
      ))}
    </div>
  );
}

function FormSection({ label, children }) {
  return (
    <div className="mt-5">
      <p className="text-sm font-medium text-stone-600 dark:text-zinc-300">{label}</p>
      {children}
    </div>
  );
}

export default function MoodForm({ onSubmit, isLoading }) {
  const { t } = useLanguage();
  const f = t.moodForm;

  const [city, setCity] = useState(CITY_KEYS[0]);
  const [companions, setCompanions] = useState(null);
  const [availableTime, setAvailableTime] = useState(null);
  const [mobility, setMobility] = useState(null);
  const [environment, setEnvironment] = useState(null);
  const [situationAvoid, setSituationAvoid] = useState([]);
  const [emotion, setEmotion] = useState(null);
  const [emotionIntensity, setEmotionIntensity] = useState(null);
  const [preferences, setPreferences] = useState([]);
  const [preferenceAvoid, setPreferenceAvoid] = useState([]);
  const [moodText, setMoodText] = useState("");

  const togglePick = (setSingle) => (value) =>
    setSingle((prev) => (prev === value ? null : value));

  const toggleMulti = (setList) => (value) =>
    setList((prev) => (prev.includes(value) ? prev.filter((v) => v !== value) : [...prev, value]));

  const hasSelection = Boolean(emotion) || preferences.length > 0 || moodText.trim();

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!hasSelection || isLoading) return;

    const avoid = Array.from(new Set([...situationAvoid, ...preferenceAvoid]));

    onSubmit({
      city,
      companions,
      availableTime,
      mobility,
      environment,
      avoid,
      emotions: emotion ? [emotion] : [],
      emotionIntensity,
      preferences,
      moodText: moodText.trim(),
    });
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="mx-auto w-full max-w-xl rounded-3xl bg-white/70 p-6 shadow-[0_25px_60px_-15px_rgba(244,114,182,0.4)] ring-1 ring-white/60 backdrop-blur sm:p-8 dark:bg-zinc-900/60 dark:shadow-[0_0_40px_rgba(168,85,247,0.15)] dark:ring-fuchsia-500/20"
    >
      <h2 className="font-[family-name:var(--font-display)] text-2xl text-stone-800 dark:text-zinc-100">
        {f.heading}
      </h2>
      <p className="mt-1 text-sm text-stone-500 dark:text-zinc-400">{f.subheading}</p>

      <label className="mt-6 block text-sm font-medium text-stone-600 dark:text-zinc-300">
        {f.cityLabel}
        <div className="relative mt-2">
          <select
            value={city}
            onChange={(event) => setCity(event.target.value)}
            className="w-full appearance-none rounded-xl border border-stone-200 bg-white px-4 py-3 pr-10 text-stone-800 outline-none focus:border-rose-300 focus:ring-2 focus:ring-rose-100 dark:border-fuchsia-500/20 dark:bg-zinc-950/50 dark:text-zinc-100 dark:focus:border-fuchsia-400 dark:focus:ring-fuchsia-500/30"
          >
            {CITY_KEYS.map((cityKey) => (
              <option key={cityKey} value={cityKey}>
                {t.cities[cityKey]}
              </option>
            ))}
          </select>
          <svg
            className="pointer-events-none absolute right-4 top-1/2 h-4 w-4 -translate-y-1/2 text-stone-400 dark:text-fuchsia-400"
            viewBox="0 0 20 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M5 7.5L10 12.5L15 7.5"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
      </label>

      <div className="mt-6 border-t border-stone-200 pt-5 dark:border-zinc-700/60">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-rose-400 dark:text-fuchsia-400">
          {f.situationHeading}
        </h3>
        <FormSection label={f.companionsLabel}>
          <ChipGroup
            options={COMPANIONS}
            labels={f.companions}
            selected={companions}
            onSelect={togglePick(setCompanions)}
          />
        </FormSection>
        <FormSection label={f.availableTimeLabel}>
          <ChipGroup
            options={AVAILABLE_TIME}
            labels={f.availableTime}
            selected={availableTime}
            onSelect={togglePick(setAvailableTime)}
          />
        </FormSection>
        <FormSection label={f.mobilityLabel}>
          <ChipGroup
            options={MOBILITY}
            labels={f.mobility}
            selected={mobility}
            onSelect={togglePick(setMobility)}
          />
        </FormSection>
        <FormSection label={f.environmentLabel}>
          <ChipGroup
            options={ENVIRONMENT}
            labels={f.environment}
            selected={environment}
            onSelect={togglePick(setEnvironment)}
          />
        </FormSection>
        <FormSection label={f.situationAvoidLabel}>
          <ChipGroup
            options={SITUATION_AVOID}
            labels={f.avoid}
            selected={situationAvoid}
            onSelect={toggleMulti(setSituationAvoid)}
            multi
          />
        </FormSection>
      </div>

      <div className="mt-6 border-t border-stone-200 pt-5 dark:border-zinc-700/60">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-rose-400 dark:text-fuchsia-400">
          {f.emotionHeading}
        </h3>
        <ChipGroup
          options={EMOTIONS}
          labels={f.emotion}
          selected={emotion}
          onSelect={togglePick(setEmotion)}
        />
        <FormSection label={f.intensityLabel}>
          <ChipGroup
            options={EMOTION_INTENSITY}
            labels={f.intensity}
            selected={emotionIntensity}
            onSelect={togglePick(setEmotionIntensity)}
          />
        </FormSection>
      </div>

      <div className="mt-6 border-t border-stone-200 pt-5 dark:border-zinc-700/60">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-rose-400 dark:text-fuchsia-400">
          {f.preferenceHeading}
        </h3>
        <FormSection label={f.activityLabel}>
          <ChipGroup
            options={ACTIVITY_PREFERENCES}
            labels={f.activity}
            selected={preferences}
            onSelect={toggleMulti(setPreferences)}
            multi
          />
        </FormSection>
        <FormSection label={f.atmosphereLabel}>
          <ChipGroup
            options={ATMOSPHERE_PREFERENCES}
            labels={f.atmosphere}
            selected={preferences}
            onSelect={toggleMulti(setPreferences)}
            multi
          />
        </FormSection>
        <FormSection label={f.placeTypeLabel}>
          <ChipGroup
            options={PLACE_PREFERENCES}
            labels={f.placeType}
            selected={preferences}
            onSelect={toggleMulti(setPreferences)}
            multi
          />
        </FormSection>
        <FormSection label={f.preferenceAvoidLabel}>
          <ChipGroup
            options={PREFERENCE_AVOID}
            labels={f.avoid}
            selected={preferenceAvoid}
            onSelect={toggleMulti(setPreferenceAvoid)}
            multi
          />
        </FormSection>
      </div>

      <div className="mt-6 border-t border-stone-200 pt-5 dark:border-zinc-700/60">
        <label className="block text-sm font-medium text-stone-600 dark:text-zinc-300">
          {f.freeTextHeading}
          <textarea
            value={moodText}
            onChange={(event) => setMoodText(event.target.value)}
            placeholder={f.moodPlaceholder}
            rows={3}
            className="mt-2 w-full resize-none rounded-xl border border-stone-200 bg-white px-4 py-3 text-stone-800 outline-none focus:border-rose-300 focus:ring-2 focus:ring-rose-100 dark:border-fuchsia-500/20 dark:bg-zinc-950/50 dark:text-zinc-100 dark:placeholder:text-zinc-500 dark:focus:border-fuchsia-400 dark:focus:ring-fuchsia-500/30"
          />
        </label>
      </div>

      <button
        type="submit"
        disabled={isLoading || !hasSelection}
        className="mt-6 w-full rounded-xl bg-rose-400 px-6 py-3 font-medium text-white shadow-[0_8px_20px_-4px_rgba(251,113,133,0.5)] transition hover:bg-rose-500 hover:shadow-[0_8px_24px_-2px_rgba(251,113,133,0.65)] disabled:cursor-not-allowed disabled:bg-stone-300 disabled:shadow-none dark:bg-fuchsia-500 dark:hover:bg-fuchsia-400 dark:shadow-[0_0_20px_rgba(232,68,255,0.5)] dark:disabled:bg-zinc-700 dark:disabled:shadow-none"
      >
        {isLoading ? f.loading : f.submit}
      </button>
      {!hasSelection && !isLoading && (
        <p className="mt-3 text-center text-xs text-stone-400 dark:text-zinc-500">
          {f.validationHint}
        </p>
      )}
      {isLoading && (
        <p className="mt-3 text-center text-xs text-stone-400 dark:text-zinc-500">
          {f.loadingHint}
        </p>
      )}
    </form>
  );
}
