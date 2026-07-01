import { createContext, useContext, useEffect, useState } from "react";
import { translations } from "./i18n";

const LanguageContext = createContext(null);
const STORAGE_KEY = "mood-trip-postcard:lang";

export function LanguageProvider({ children }) {
  const [lang, setLang] = useState(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored === "en" || stored === "ko" ? stored : "ko";
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, lang);
  }, [lang]);

  return (
    <LanguageContext.Provider value={{ lang, setLang, t: translations[lang] }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useLanguage must be used within a LanguageProvider");
  return ctx;
}
