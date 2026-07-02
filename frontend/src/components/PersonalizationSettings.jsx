import { useEffect, useState } from "react";
import { useLanguage } from "../LanguageContext";
import { fetchPreferences, savePreferences } from "../api";
import { ChipGroup, FormSection } from "./ChipGroup";

const AVAILABLE_TIME = ["under_30min", "1h", "2_3h", "half_day"];
const MOBILITY = ["near", "moderate_walk", "far_walk"];
const ENVIRONMENT = ["indoor", "outdoor", "any"];
const ACTIVITY_PREFERENCES = ["walking", "photo", "cafe", "exhibition", "shopping", "reading", "night_view", "history"];
const ATMOSPHERE_PREFERENCES = ["quiet", "sentimental", "lively", "exotic", "natural", "local", "artistic"];
const PLACE_PREFERENCES = ["riverside", "park", "alley", "bookstore", "gallery", "market", "viewpoint"];
const AVOID = ["crowded", "far", "expensive", "complex_route", "long_wait", "long_distance", "too_touristy"];

export default function PersonalizationSettings() {
  const { t } = useLanguage();
  const p = t.personalization;

  const [availableTime, setAvailableTime] = useState(null);
  const [mobility, setMobility] = useState(null);
  const [environment, setEnvironment] = useState(null);
  const [avoid, setAvoid] = useState([]);
  const [preferences, setPreferences] = useState([]);
  const [isSaving, setIsSaving] = useState(false);
  const [justSaved, setJustSaved] = useState(false);

  useEffect(() => {
    let isCancelled = false;
    fetchPreferences()
      .then((data) => {
        if (isCancelled) return;
        setAvailableTime(data.available_time || null);
        setMobility(data.mobility || null);
        setEnvironment(data.environment || null);
        setAvoid(data.avoid || []);
        setPreferences(data.preferences || []);
      })
      .catch(() => {});
    return () => {
      isCancelled = true;
    };
  }, []);

  const togglePick = (setSingle) => (value) =>
    setSingle((prev) => (prev === value ? null : value));

  const toggleMulti = (setList) => (value) =>
    setList((prev) => (prev.includes(value) ? prev.filter((v) => v !== value) : [...prev, value]));

  const handleSave = async () => {
    setIsSaving(true);
    setJustSaved(false);
    try {
      await savePreferences({ availableTime, mobility, environment, avoid, preferences });
      setJustSaved(true);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="mx-auto w-full max-w-xl rounded-3xl bg-white/70 p-6 shadow-[0_25px_60px_-15px_rgba(244,114,182,0.4)] ring-1 ring-white/60 backdrop-blur sm:p-8 dark:bg-zinc-900/60 dark:shadow-[0_0_40px_rgba(168,85,247,0.15)] dark:ring-fuchsia-500/20">
      <h2 className="font-[family-name:var(--font-display)] text-2xl text-stone-800 dark:text-zinc-100">
        {p.heading}
      </h2>
      <p className="mt-1 text-sm text-stone-500 dark:text-zinc-400">{p.subheading}</p>

      <FormSection label={p.availableTimeLabel}>
        <ChipGroup
          options={AVAILABLE_TIME}
          labels={p.availableTime}
          selected={availableTime}
          onSelect={togglePick(setAvailableTime)}
        />
      </FormSection>
      <FormSection label={p.mobilityLabel}>
        <ChipGroup
          options={MOBILITY}
          labels={p.mobility}
          selected={mobility}
          onSelect={togglePick(setMobility)}
        />
      </FormSection>
      <FormSection label={p.environmentLabel}>
        <ChipGroup
          options={ENVIRONMENT}
          labels={p.environment}
          selected={environment}
          onSelect={togglePick(setEnvironment)}
        />
      </FormSection>
      <FormSection label={p.avoidLabel}>
        <ChipGroup
          options={AVOID}
          labels={p.avoid}
          selected={avoid}
          onSelect={toggleMulti(setAvoid)}
          multi
        />
      </FormSection>

      <div className="mt-6 border-t border-stone-200 pt-5 dark:border-zinc-700/60">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-rose-400 dark:text-fuchsia-400">
          {p.preferenceHeading}
        </h3>
        <FormSection label={p.activityLabel}>
          <ChipGroup
            options={ACTIVITY_PREFERENCES}
            labels={p.activity}
            selected={preferences}
            onSelect={toggleMulti(setPreferences)}
            multi
          />
        </FormSection>
        <FormSection label={p.atmosphereLabel}>
          <ChipGroup
            options={ATMOSPHERE_PREFERENCES}
            labels={p.atmosphere}
            selected={preferences}
            onSelect={toggleMulti(setPreferences)}
            multi
          />
        </FormSection>
        <FormSection label={p.placeTypeLabel}>
          <ChipGroup
            options={PLACE_PREFERENCES}
            labels={p.placeType}
            selected={preferences}
            onSelect={toggleMulti(setPreferences)}
            multi
          />
        </FormSection>
      </div>

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
