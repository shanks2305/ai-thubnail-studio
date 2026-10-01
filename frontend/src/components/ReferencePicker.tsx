import { useEffect, useMemo, useState, type DragEvent } from "react"
import { Icon } from "./Icon"

export const MAX_REFERENCES = 6

type Props = {
  files: File[]
  onChange: (files: File[]) => void
}

export function ReferencePicker({ files, onChange }: Props) {
  const [dragging, setDragging] = useState(false)
  const previews = useMemo(() => files.map((file) => URL.createObjectURL(file)), [files])

  useEffect(() => () => previews.forEach((url) => URL.revokeObjectURL(url)), [previews])

  function add(list: FileList | null) {
    if (!list) return
    onChange([...files, ...Array.from(list)].slice(0, MAX_REFERENCES))
  }

  function onDrop(event: DragEvent) {
    event.preventDefault()
    setDragging(false)
    add(event.dataTransfer.files)
  }

  return (
    <div>
      <label
        onDragOver={(event: DragEvent) => {
          event.preventDefault()
          setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={`flex cursor-pointer flex-col items-center gap-2 rounded-lg border border-dashed px-4 py-7 text-center text-sm text-mist transition ${dragging ? "border-ember/60 bg-ember/5" : "border-line-strong bg-ink hover:border-mist/60"}`}
      >
        <input type="file" accept="image/png,image/jpeg,image/webp" multiple className="sr-only" onChange={(event) => add(event.target.files)} />
        <span className="grid h-9 w-9 place-items-center rounded-lg bg-panel-2 text-mist ring-1 ring-line">
          <Icon name="upload" />
        </span>
        <span>
          <span className="font-medium text-paper">Click to upload</span> or drag and drop
        </span>
        <span className="text-xs text-mist/70">PNG, JPG, or WebP · up to {MAX_REFERENCES}</span>
      </label>
      {files.length > 0 && (
        <ul className="mt-3 grid grid-cols-3 gap-3 sm:grid-cols-6">
          {files.map((file, index) => (
            <li key={`${file.name}-${file.lastModified}-${index}`} className="group relative">
              <img src={previews[index]} alt={file.name} className="aspect-video w-full rounded-lg border border-line object-cover" />
              <button
                type="button"
                onClick={() => onChange(files.filter((_, position) => position !== index))}
                aria-label={`Remove ${file.name}`}
                className="absolute -right-2 -top-2 grid h-5 w-5 place-items-center rounded-full border border-line bg-ink text-mist transition hover:border-ember hover:text-ember"
              >
                <Icon name="x" className="h-3 w-3" />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
