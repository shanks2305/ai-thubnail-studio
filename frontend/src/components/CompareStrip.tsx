import { Link } from "react-router-dom"
import type { Concept, Generation } from "../types"

export function CompareStrip({ projectId, generations, concepts }: { projectId: string; generations: Generation[]; concepts: Concept[] }) {
  return (
    <section>
      <h2 className="text-base font-semibold">Passes</h2>
      <div className="mt-3 flex gap-3 overflow-x-auto pb-1">
        {generations.map((generation) => {
          const concept = concepts.find((item) => item.id === generation.concept_id)
          return (
            <Link key={generation.id} to={`/projects/${projectId}/editor/${generation.id}`} className="card w-56 shrink-0 overflow-hidden">
              {generation.image_url && <img src={generation.image_url} alt="" className="aspect-video w-full object-cover" />}
              <p className="truncate px-3 py-2 text-xs text-mist">
                {concept?.name ?? "Thumbnail"} · {generation.critique?.overall ?? "—"}
                {generation.variation_axis ? ` · ${generation.variation_axis}` : ""}
              </p>
            </Link>
          )
        })}
      </div>
    </section>
  )
}
