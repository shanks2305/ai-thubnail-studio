import { Icon } from "./Icon"
import { Spinner } from "./Spinner"

const EXPORT_FORMATS = [
  ["png", "PNG"],
  ["jpeg", "JPG"],
  ["webp", "WebP"],
] as const

export type SaveState = { status: "idle" | "saving" | "saved" } | { status: "error"; message: string }

function SaveIndicator({ save }: { save: SaveState }) {
  if (save.status === "idle") return null
  if (save.status === "error") return <span className="text-xs text-ember">{save.message}</span>
  return (
    <span className="flex items-center gap-1.5 text-xs text-mist">
      {save.status === "saving" ? <Spinner className="border-mist/30 border-t-mist" /> : <Icon name="check" className="h-3.5 w-3.5 text-emerald-300" />}
      {save.status === "saving" ? "Saving…" : "Saved"}
    </span>
  )
}

export function EditorToolbar({ save, generationId }: { save: SaveState; generationId: string }) {
  return (
    <>
      <span aria-live="polite" className="mr-2">
        <SaveIndicator save={save} />
      </span>
      <span className="label hidden sm:inline">Export</span>
      <div className="segmented">
        {EXPORT_FORMATS.map(([format, label]) => (
          <a key={format} href={`/api/generations/${generationId}/export?format=${format}`} className="chip">
            {format === "png" && <Icon name="download" className="h-3.5 w-3.5" />}
            {label}
          </a>
        ))}
      </div>
    </>
  )
}
