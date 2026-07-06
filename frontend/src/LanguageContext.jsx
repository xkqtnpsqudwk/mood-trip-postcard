import { createContext, useContext } from "react";
import { translations } from "./i18n";

const LanguageContext = createContext(null);
const APP_LANGUAGE = "ko";

export function LanguageProvider({ children }) {
  return (
    <LanguageContext.Provider value={{ lang: APP_LANGUAGE, t: translations.ko }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useLanguage must be used within a LanguageProvider");
  return ctx;
}
