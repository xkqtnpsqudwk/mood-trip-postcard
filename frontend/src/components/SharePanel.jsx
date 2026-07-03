import { useMemo, useState } from "react";
import { useLanguage } from "../LanguageContext";

const localized = (value, lang) => {
  if (value && typeof value === "object") {
    return value[lang] ?? value.en ?? value.ko ?? "";
  }
  return value ?? "";
};

function wrapText(context, text, x, y, maxWidth, lineHeight, maxLines) {
  const words = String(text || "").split(/\s+/).filter(Boolean);
  let line = "";
  let lines = 0;

  for (let index = 0; index < words.length; index += 1) {
    const word = words[index];
    const nextLine = line ? `${line} ${word}` : word;
    if (context.measureText(nextLine).width > maxWidth && line) {
      context.fillText(line, x, y);
      y += lineHeight;
      lines += 1;
      line = word;
      if (lines >= maxLines - 1) {
        const rest = [word, ...words.slice(index + 1)].join(" ");
        let clipped = rest;
        while (context.measureText(`${clipped}...`).width > maxWidth && clipped.length > 0) {
          clipped = clipped.slice(0, -1);
        }
        context.fillText(`${clipped}...`, x, y);
        return y + lineHeight;
      }
    } else {
      line = nextLine;
    }
  }

  if (line) {
    context.fillText(line, x, y);
    y += lineHeight;
  }
  return y;
}

function loadImage(src) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = reject;
    image.src = src;
  });
}

function drawRoundedRect(context, x, y, width, height, radius) {
  context.beginPath();
  context.moveTo(x + radius, y);
  context.arcTo(x + width, y, x + width, y + height, radius);
  context.arcTo(x + width, y + height, x, y + height, radius);
  context.arcTo(x, y + height, x, y, radius);
  context.arcTo(x, y, x + width, y, radius);
  context.closePath();
}

async function downloadShareImage({ postcard, placeName, cityName, t }) {
  const canvas = document.createElement("canvas");
  canvas.width = 1080;
  canvas.height = 1350;
  const context = canvas.getContext("2d");

  const gradient = context.createLinearGradient(0, 0, 1080, 1350);
  gradient.addColorStop(0, "#fff1f2");
  gradient.addColorStop(0.55, "#ffffff");
  gradient.addColorStop(1, "#e0f2fe");
  context.fillStyle = gradient;
  context.fillRect(0, 0, 1080, 1350);

  context.fillStyle = "#111827";
  context.font = "700 34px Arial, sans-serif";
  context.fillText("MoodTrip", 80, 88);
  context.font = "500 26px Arial, sans-serif";
  context.fillStyle = "#8b5cf6";
  context.fillText(`${cityName} · ${placeName}`, 80, 140);

  const imageTop = 190;
  const imageHeight = 760;
  drawRoundedRect(context, 80, imageTop, 920, imageHeight, 36);
  context.save();
  context.clip();
  if (postcard.image_url) {
    try {
      const image = await loadImage(postcard.image_url);
      const scale = Math.max(920 / image.width, imageHeight / image.height);
      const width = image.width * scale;
      const height = image.height * scale;
      context.drawImage(image, 80 + (920 - width) / 2, imageTop + (imageHeight - height) / 2, width, height);
    } catch {
      context.fillStyle = "#f5f3ff";
      context.fillRect(80, imageTop, 920, imageHeight);
    }
  } else {
    const placeholder = context.createLinearGradient(80, imageTop, 1000, imageTop + imageHeight);
    placeholder.addColorStop(0, "#fce7f3");
    placeholder.addColorStop(1, "#cffafe");
    context.fillStyle = placeholder;
    context.fillRect(80, imageTop, 920, imageHeight);
  }
  context.restore();

  const cardTop = imageTop + imageHeight + 70;
  drawRoundedRect(context, 80, cardTop, 920, 210, 28);
  context.fillStyle = "#fffaf0";
  context.fill();
  context.strokeStyle = "#d6d3d1";
  context.lineWidth = 2;
  context.stroke();

  context.fillStyle = "#111827";
  context.font = "700 30px Arial, sans-serif";
  context.fillText("POST CARD", 120, cardTop + 58);
  context.strokeStyle = "#a8a29e";
  context.lineWidth = 2;
  context.beginPath();
  context.moveTo(540, cardTop + 34);
  context.lineTo(540, cardTop + 176);
  context.stroke();
  context.strokeRect(850, cardTop + 34, 90, 70);
  for (let index = 0; index < 4; index += 1) {
    const y = cardTop + 120 + index * 24;
    context.beginPath();
    context.moveTo(600, y);
    context.lineTo(940, y);
    context.stroke();
  }

  context.fillStyle = "#8b5cf6";
  context.font = "700 28px Arial, sans-serif";
  context.fillText(t.share.footer, 80, 1268);

  const link = document.createElement("a");
  link.download = `moodtrip-${postcard.id || postcard.trip_id || "trip"}.png`;
  link.href = canvas.toDataURL("image/png");
  link.click();
}

export default function SharePanel({ postcard, compact = false }) {
  const { t, lang } = useLanguage();
  const [status, setStatus] = useState("");

  const shareData = useMemo(() => {
    const placeName = localized(postcard.place_name_i18n, lang) || postcard.place_name;
    const title = localized(postcard.title_i18n, lang) || postcard.title;
    const message = localized(postcard.message_i18n, lang) || postcard.message;
    const cityName = t.cities[postcard.city] ?? postcard.city;
    const review = postcard.review || "";
    const caption = t.share.caption({ title, city: cityName, place: placeName, message, review });
    return { placeName, title, message, cityName, review, caption };
  }, [lang, postcard, t]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(shareData.caption);
      setStatus(t.share.copied);
    } catch {
      setStatus(t.share.copyFailed);
    }
  };

  const handleDownload = async () => {
    setStatus(t.share.downloading);
    try {
      await downloadShareImage({ postcard, ...shareData, t });
      setStatus(t.share.downloaded);
    } catch {
      setStatus(t.share.downloadFailed);
    }
  };

  const handleNativeShare = async () => {
    if (!navigator.share) return;
    try {
      await navigator.share({
        title: `${shareData.cityName} / ${shareData.placeName}`,
        text: shareData.caption,
      });
      setStatus(t.share.shared);
    } catch {
      setStatus("");
    }
  };

  return (
    <section
      className={`rounded-2xl border border-rose-100 bg-white/90 p-4 shadow-sm dark:border-cyan-500/20 dark:bg-zinc-950/80 ${
        compact ? "mt-4" : "mt-5"
      }`}
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-rose-400 dark:text-cyan-300">
            {t.share.label}
          </p>
          <h3 className="mt-1 text-sm font-semibold text-stone-800 dark:text-zinc-100">
            {t.share.heading}
          </h3>
        </div>
        <span className="rounded-full bg-violet-50 px-3 py-1 text-[11px] font-medium text-violet-500 dark:bg-cyan-950/50 dark:text-cyan-300">
          MoodTrip
        </span>
      </div>

      <div className="mt-3 rounded-xl bg-gradient-to-br from-rose-50 via-white to-cyan-50 p-4 text-left ring-1 ring-rose-100 dark:from-zinc-900 dark:via-zinc-950 dark:to-cyan-950/40 dark:ring-cyan-500/20">
        <p className="text-[11px] font-medium text-violet-500 dark:text-cyan-300">
          {shareData.cityName} · {shareData.placeName}
        </p>
        <p className="mt-2 break-keep font-[family-name:var(--font-display)] text-lg leading-snug text-stone-800 dark:text-zinc-100">
          POST CARD
        </p>
        <p className="mt-2 text-sm leading-relaxed text-stone-500 dark:text-zinc-400">
          {t.share.blankPostcardHint}
        </p>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={handleDownload}
          className="rounded-xl bg-rose-400 px-4 py-2 text-xs font-medium text-white shadow-[0_8px_18px_-6px_rgba(251,113,133,0.6)] transition hover:bg-rose-500 dark:bg-cyan-500 dark:hover:bg-cyan-400"
        >
          {t.share.download}
        </button>
        <button
          type="button"
          onClick={handleCopy}
          className="rounded-xl border border-stone-200 px-4 py-2 text-xs font-medium text-stone-500 transition hover:bg-white dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-900"
        >
          {t.share.copy}
        </button>
        {typeof navigator !== "undefined" && navigator.share && (
          <button
            type="button"
            onClick={handleNativeShare}
            className="rounded-xl border border-stone-200 px-4 py-2 text-xs font-medium text-stone-500 transition hover:bg-white dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-900"
          >
            {t.share.native}
          </button>
        )}
      </div>
      {status && (
        <p className="mt-2 text-xs text-stone-400 dark:text-zinc-500">{status}</p>
      )}
    </section>
  );
}
