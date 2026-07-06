import { useState } from "react";
import { useLanguage } from "../LanguageContext";
import { useAuth } from "../AuthContext";

export default function AuthForm({ onSuccess }) {
  const { t } = useLanguage();
  const { login, signup } = useAuth();
  const [mode, setMode] = useState("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const isLogin = mode === "login";

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!username.trim() || !password || isLoading) return;
    setError(null);
    setIsLoading(true);
    try {
      if (isLogin) {
        await login(username.trim(), password);
      } else {
        await signup(username.trim(), password);
      }
      onSuccess?.();
    } catch {
      setError(isLogin ? t.auth.loginError : t.auth.signupError);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="mx-auto w-full max-w-md rounded-3xl bg-white/80 p-6 shadow-[0_25px_60px_-15px_rgba(244,114,182,0.35)] ring-1 ring-rose-100/80 backdrop-blur sm:p-8 dark:bg-zinc-950/65 dark:shadow-[0_0_40px_rgba(217,70,239,0.14)] dark:ring-fuchsia-500/20"
    >
      <h2 className="font-[family-name:var(--font-display)] text-2xl text-stone-800 dark:text-zinc-100">
        {isLogin ? t.auth.loginHeading : t.auth.signupHeading}
      </h2>

      <label className="mt-6 block text-sm font-medium text-stone-600 dark:text-zinc-300">
        {t.auth.usernameLabel}
        <input
          type="text"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          autoComplete="username"
          className="mt-2 w-full rounded-xl border border-stone-200 bg-white px-4 py-3 text-stone-800 outline-none focus:border-rose-300 focus:ring-2 focus:ring-rose-100 dark:border-fuchsia-500/20 dark:bg-zinc-950/50 dark:text-zinc-100 dark:focus:border-fuchsia-400 dark:focus:ring-fuchsia-500/30"
        />
      </label>

      <label className="mt-4 block text-sm font-medium text-stone-600 dark:text-zinc-300">
        {t.auth.passwordLabel}
        <input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete={isLogin ? "current-password" : "new-password"}
          className="mt-2 w-full rounded-xl border border-stone-200 bg-white px-4 py-3 text-stone-800 outline-none focus:border-rose-300 focus:ring-2 focus:ring-rose-100 dark:border-fuchsia-500/20 dark:bg-zinc-950/50 dark:text-zinc-100 dark:focus:border-fuchsia-400 dark:focus:ring-fuchsia-500/30"
        />
      </label>

      {error && (
        <p className="mt-3 text-sm text-rose-500 dark:text-fuchsia-400">{error}</p>
      )}

      <button
        type="submit"
        disabled={isLoading || !username.trim() || !password}
        className="mt-6 w-full rounded-xl bg-rose-400 px-6 py-3 font-medium text-white shadow-[0_8px_20px_-4px_rgba(251,113,133,0.5)] transition hover:bg-rose-500 hover:shadow-[0_8px_24px_-2px_rgba(251,113,133,0.65)] disabled:cursor-not-allowed disabled:bg-stone-300 disabled:shadow-none dark:bg-fuchsia-500 dark:hover:bg-fuchsia-400 dark:shadow-[0_0_20px_rgba(232,68,255,0.5)] dark:disabled:bg-zinc-700 dark:disabled:shadow-none"
      >
        {isLoading ? t.auth.loading : isLogin ? t.auth.loginSubmit : t.auth.signupSubmit}
      </button>

      <button
        type="button"
        onClick={() => {
          setMode(isLogin ? "signup" : "login");
          setError(null);
        }}
        className="mt-4 block w-full text-center text-sm font-medium text-stone-500 underline-offset-4 hover:text-stone-700 hover:underline dark:text-zinc-400 dark:hover:text-zinc-200"
      >
        {isLogin ? t.auth.switchToSignup : t.auth.switchToLogin}
      </button>
    </form>
  );
}
