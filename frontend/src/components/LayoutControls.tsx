import type { EditorDraft } from "../editorState"
import type { TextSpec } from "../types"

const FONTS: TextSpec["font"][] = ["anton", "bebas"]
const VERTICAL: TextSpec["vertical"][] = ["top", "middle", "bottom"]

export function LayoutControls({ draft, onChange }: { draft: EditorDraft; onChange: (draft: EditorDraft) => void }) {
  const text = draft.text
  function setText(patch: Partial<TextSpec>) {
    onChange({ ...draft, text: { ...text, ...patch } })
  }

  return (
    <div>
      <fieldset className="border-t border-line px-4 py-4">
        <legend className="label mb-2.5">Font and outline</legend>
        <div className="segmented flex w-full">
          {FONTS.map((font) => (
            <button key={font} type="button" aria-pressed={text.font === font} onClick={() => setText({ font })} className={`chip flex-1 justify-center capitalize ${text.font === font ? "chip-active" : ""}`}>
              {font}
            </button>
          ))}
        </div>
        <label className="mt-3 flex items-center gap-2 text-sm">
          <input type="checkbox" checked={text.stroke} onChange={(event) => setText({ stroke: event.target.checked })} />
          Stroke
        </label>
      </fieldset>
      <fieldset className="border-t border-line px-4 py-4">
        <legend className="label mb-2.5">Vertical</legend>
        <div className="segmented flex w-full">
          {VERTICAL.map((vertical) => (
            <button key={vertical} type="button" aria-pressed={text.vertical === vertical} onClick={() => setText({ vertical })} className={`chip flex-1 justify-center capitalize ${text.vertical === vertical ? "chip-active" : ""}`}>
              {vertical}
            </button>
          ))}
        </div>
      </fieldset>
      <fieldset className="border-t border-line px-4 py-4">
        <legend className="label mb-2.5">Scrim {Math.round(draft.scrimStrength * 100)}%</legend>
        <input
          type="range"
          min={0}
          max={100}
          value={Math.round(draft.scrimStrength * 100)}
          aria-label="Scrim strength"
          onChange={(event) => onChange({ ...draft, scrimStrength: Number(event.target.value) / 100 })}
          className="w-full"
        />
      </fieldset>
      <fieldset className="border-t border-line px-4 py-4">
        <legend className="label mb-2.5">Palette</legend>
        <div className="flex gap-2">
          {draft.palette.slice(0, 3).map((color, index) => (
            <input
              key={index}
              type="color"
              aria-label={`Palette color ${index + 1}`}
              value={color}
              onChange={(event) => {
                const palette = draft.palette.slice(0, 3)
                palette[index] = event.target.value
                onChange({ ...draft, palette, recolor: true })
              }}
            />
          ))}
        </div>
      </fieldset>
    </div>
  )
}
