function chipClass(isSelected) {
  return `rounded-full px-3 py-1.5 text-xs font-medium transition ${
    isSelected
      ? "bg-rose-400 text-white shadow-[0_4px_12px_-2px_rgba(251,113,133,0.5)] dark:bg-fuchsia-500 dark:shadow-[0_0_12px_rgba(232,68,255,0.5)]"
      : "bg-white text-stone-500 ring-1 ring-stone-200 hover:bg-stone-50 dark:bg-zinc-950/50 dark:text-zinc-400 dark:ring-fuchsia-500/20 dark:hover:bg-zinc-900"
  }`;
}

export function ChipGroup({ options, labels, selected, onSelect, multi = false }) {
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

export function FormSection({ label, children }) {
  return (
    <div className="mt-5">
      <p className="text-sm font-medium text-stone-600 dark:text-zinc-300">{label}</p>
      {children}
    </div>
  );
}
