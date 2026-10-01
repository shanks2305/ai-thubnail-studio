import { useState } from "react"
import type { Concept } from "../types"
import { DeleteButton } from "./DeleteButton"
import { Icon } from "./Icon"
import { Spinner } from "./Spinner"

type Props = {
  concepts: Concept[]
  busy: boolean
  pendingId: string | null
  renderedIds: string[]
  onGenerate: (conceptId: string, prompt: string) => void
  onDelete: (conceptId: string) => void
}

export function ConceptGrid({ concepts, busy, pendingId, renderedIds, onGenerate, onDelete }: Props) {
  const visible = concepts.filter((concept) => !concept.archived)
  return (
    <section>
      <div className="flex items-center gap-2">
        <h2 className="text-base font-semibold">Concepts</h2>
        <span className="rounded-md bg-panel-2 px-1.5 py-0.5 text-xs tabular-nums text-mist ring-1 ring-line">{visible.length}</span>
      </div>
      <p className="mt-1 text-sm text-mist">Pick a direction to render. You can render the others too, or edit the image prompt first.</p>
      <div className="mt-4 grid gap-3 xl:grid-cols-2">
        {visible.map((concept, index) => (
          <ConceptCard
            key={concept.id}
            concept={concept}
            index={index}
            busy={busy}
            pending={pendingId === concept.id}
            rendered={renderedIds.includes(concept.id)}
            onGenerate={onGenerate}
            onDelete={() => onDelete(concept.id)}
          />
        ))}
      </div>
    </section>
  )
}

function ConceptCard({
  concept,
  index,
  busy,
  pending,
  rendered,
  onGenerate,
  onDelete,
}: {
  concept: Concept
  index: number
  busy: boolean
  pending: boolean
  rendered: boolean
  onGenerate: Props["onGenerate"]
  onDelete: () => void
}) {
  const [prompt, setPrompt] = useState(concept.image_prompt ?? "")
  return (
    <article className={`card flex flex-col p-4 transition ${rendered ? "border-ember/50 ring-1 ring-ember/20" : "hover:border-line-strong"}`}>
      <div className="flex items-center justify-between gap-3">
        <span className="truncate text-xs font-medium text-gold">
          <span className="mr-1.5 tabular-nums text-mist/60">{String(index + 1).padStart(2, "0")}</span>
          {concept.name}
        </span>
        <span className="flex items-center gap-1">
          {rendered && <span className="rounded-md bg-ember/10 px-1.5 py-0.5 text-[11px] font-medium text-ember ring-1 ring-ember/25 ring-inset">Rendered</span>}
          <DeleteButton label="concept" disabled={busy} onDelete={onDelete} />
        </span>
      </div>
      <h3 className="mt-2.5 text-base font-semibold leading-snug">{concept.hook}</h3>
      <p className="mt-2 line-clamp-3 text-sm leading-6 text-mist">{concept.visual_story}</p>
      <label className="mt-3 block">
        <span className="label">Image prompt</span>
        <textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} className="field mt-1.5 min-h-16 text-xs" placeholder="Optional. Used the next time this concept renders." />
      </label>
      <div className="mt-auto pt-4">
        <button type="button" disabled={busy} onClick={() => onGenerate(concept.id, prompt)} className={rendered ? "btn-outline" : "btn-primary"}>
          {pending ? <Spinner /> : <Icon name="sparkles" />}
          {pending ? "Starting…" : rendered ? "Render again" : "Render"}
        </button>
      </div>
    </article>
  )
}
