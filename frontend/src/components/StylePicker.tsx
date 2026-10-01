const STYLES = [
  { id: "cinematic", label: "Cinematic" },
  { id: "ghibli", label: "Ghibli" },
  { id: "anime", label: "Anime" },
  { id: "cartoon", label: "Cartoon" },
  { id: "gaming", label: "Gaming" },
  { id: "tech", label: "Tech" },
  { id: "comic", label: "Comic" },
  { id: "documentary", label: "Documentary" },
  { id: "neon", label: "Neon" },
  { id: "minimal", label: "Minimal" },
] as const

export type CreativeStyleId = (typeof STYLES)[number]["id"]

export function styleLabel(id: string | null | undefined) {
  return STYLES.find((style) => style.id === id)?.label ?? "Cinematic"
}

export function StylePicker({
  value,
  onChange,
  disabled = false,
}: {
  value: string
  onChange: (id: CreativeStyleId) => void
  disabled?: boolean
}) {
  return (
    <div className="flex flex-wrap gap-2" role="radiogroup" aria-label="Creative style">
      {STYLES.map((style) => {
        const selected = style.id === value
        return (
          <button
            key={style.id}
            type="button"
            role="radio"
            aria-checked={selected}
            disabled={disabled}
            onClick={() => onChange(style.id)}
            className={selected ? "chip chip-active" : "chip ring-1 ring-line"}
          >
            {style.label}
          </button>
        )
      })}
    </div>
  )
}
