import type { ReactNode } from "react"
import type { TextSpec } from "../types"

const SWATCHES = ["#ffffff", "#111111", "#f2c14e", "#ff4d2e"]
const POSITIONS: TextSpec["position"][] = ["left", "center", "right"]
const SIZES: TextSpec["size"][] = ["medium", "large", "very large"]
const MAX_HEADLINE = 80

function Group({ label, children }: { label: string; children: ReactNode }) {
  return (
    <fieldset className="border-t border-line px-4 py-4">
      <legend className="label float-left mb-2.5 w-full">{label}</legend>
      <div className="clear-both">{children}</div>
    </fieldset>
  )
}

export function HeadlineControls({ text, onChange }: { text: TextSpec; onChange: (text: TextSpec) => void }) {
  return (
    <div>
      <label className="block px-4 py-4">
        <span className="label flex items-baseline justify-between">
          Headline
          <span className="tabular-nums text-mist/70">{text.content.length}/{MAX_HEADLINE}</span>
        </span>
        <textarea
          value={text.content}
          maxLength={MAX_HEADLINE}
          onChange={(event) => onChange({ ...text, content: event.target.value })}
          className="field mt-2.5 min-h-24 resize-none text-base font-semibold leading-snug"
        />
      </label>
      <Group label="Position">
        <div className="segmented flex w-full">
          {POSITIONS.map((position) => (
            <button key={position} type="button" aria-pressed={text.position === position} onClick={() => onChange({ ...text, position })} className={`chip flex-1 justify-center capitalize ${text.position === position ? "chip-active" : ""}`}>
              {position}
            </button>
          ))}
        </div>
      </Group>
      <Group label="Size">
        <div className="segmented flex w-full">
          {SIZES.map((size) => (
            <button key={size} type="button" aria-pressed={text.size === size} onClick={() => onChange({ ...text, size })} className={`chip flex-1 justify-center capitalize ${text.size === size ? "chip-active" : ""}`}>
              {size}
            </button>
          ))}
        </div>
      </Group>
      <Group label="Color">
        <div className="flex items-center gap-2">
          {SWATCHES.map((color) => (
            <button
              key={color}
              type="button"
              aria-label={color}
              aria-pressed={text.color.toLowerCase() === color}
              onClick={() => onChange({ ...text, color })}
              className={`h-7 w-7 rounded-md transition hover:scale-110 ${text.color.toLowerCase() === color ? "ring-2 ring-ember ring-offset-2 ring-offset-panel" : "ring-1 ring-line-strong"}`}
              style={{ background: color }}
            />
          ))}
          <label className="relative grid h-7 w-7 cursor-pointer place-items-center overflow-hidden rounded-md border border-dashed border-mist/60 text-xs text-mist transition hover:border-paper" title="Custom color">
            +
            <input type="color" value={text.color} onChange={(event) => onChange({ ...text, color: event.target.value })} aria-label="Custom color" className="absolute inset-0 cursor-pointer opacity-0" />
          </label>
          <span className="ml-auto font-mono text-xs uppercase text-mist">{text.color}</span>
        </div>
      </Group>
    </div>
  )
}
