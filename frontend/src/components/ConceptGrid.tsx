import { Icon } from "./Icon"
import { Spinner } from "./Spinner"
import type { Concept } from "../types"

type Props = {
  concepts: Concept[]
  busy: boolean
  pendingId: string | null
  selectedId: string | null
  onGenerate: (conceptId: string) => void
}

export function ConceptGrid({ concepts, busy, pendingId, selectedId, onGenerate }: Props) {
  return (
    <section>
      <div className="flex items-center gap-2">
        <h2 className="text-base font-semibold">Concepts</h2>
        <span className="rounded-md bg-panel-2 px-1.5 py-0.5 text-xs tabular-nums text-mist ring-1 ring-line">{concepts.length}</span>
      </div>
      <p className="mt-1 text-sm text-mist">Pick a direction to render. The others stay here for another pass.</p>
      <div className="mt-4 grid gap-3 xl:grid-cols-2">
        {concepts.map((concept, index) => {
          const selected = concept.id === selectedId
          const pending = pendingId === concept.id
          return (
            <article key={concept.id} className={`card flex flex-col p-4 transition ${selected ? "border-ember/50 ring-1 ring-ember/20" : "hover:border-line-strong"}`}>
              <div className="flex items-center justify-between gap-3">
                <span className="truncate text-xs font-medium text-gold">
                  <span className="mr-1.5 tabular-nums text-mist/60">{String(index + 1).padStart(2, "0")}</span>
                  {concept.name}
                </span>
                {selected && <span className="rounded-md bg-ember/10 px-1.5 py-0.5 text-[11px] font-medium text-ember ring-1 ring-ember/25 ring-inset">Rendered</span>}
              </div>
              <h3 className="mt-2.5 text-base font-semibold leading-snug">{concept.hook}</h3>
              <p className="mt-2 line-clamp-3 text-sm leading-6 text-mist">{concept.visual_story}</p>
              <p className="mt-3 rounded-lg bg-ink/60 px-3 py-2 text-xs leading-5 text-mist ring-1 ring-line ring-inset">
                <span className="font-medium text-paper">Why it works · </span>
                {concept.why_it_works}
              </p>
              <div className="mt-auto pt-4">
                <button type="button" disabled={busy} onClick={() => onGenerate(concept.id)} className={selected ? "btn-outline" : "btn-primary"}>
                  {pending ? <Spinner /> : <Icon name="sparkles" />}
                  {pending ? "Starting…" : selected ? "Render again" : "Render"}
                </button>
              </div>
            </article>
          )
        })}
      </div>
    </section>
  )
}
