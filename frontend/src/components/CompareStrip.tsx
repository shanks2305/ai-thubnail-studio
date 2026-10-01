import { Link } from "react-router-dom"
import type { Concept, Generation } from "../types"
import { DeleteButton } from "./DeleteButton"

export function CompareStrip({
  projectId,
  generations,
  concepts,
  deleteDisabled,
  onDelete,
}: {
  projectId: string
  generations: Generation[]
  concepts: Concept[]
  deleteDisabled: boolean
  onDelete: (generationId: string) => void
}) {
  return (
    <section>
      <h2 className="text-base font-semibold">Passes</h2>
      <div className="mt-3 flex gap-3 overflow-x-auto pb-1">
        {generations.map((generation) => {
          const concept = concepts.find((item) => item.id === generation.concept_id)
          return (
            <div key={generation.id} className="card relative w-56 shrink-0 overflow-hidden">
              <DeleteButton label="thumbnail" disabled={deleteDisabled} onDelete={() => onDelete(generation.id)} className="absolute right-1 top-1 bg-ink/80" />
              <Link to={`/projects/${projectId}/editor/${generation.id}`} className="block">
                {generation.image_url && <img src={generation.image_url} alt="" className="aspect-video w-full object-cover" />}
                <p className="truncate px-3 py-2 text-xs text-mist">
                  {concept?.name ?? "Thumbnail"} · {generation.critique?.overall ?? "—"}
                  {generation.variation_axis ? ` · ${generation.variation_axis}` : ""}
                </p>
              </Link>
            </div>
          )
        })}
      </div>
    </section>
  )
}
