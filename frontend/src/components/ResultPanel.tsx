import { Link } from "react-router-dom"
import type { Concept, Generation } from "../types"

export function ResultPanel({
  projectId,
  generations,
  concepts,
}: {
  projectId: string
  generations: Generation[]
  concepts: Concept[]
}) {
  const latest = generations[generations.length - 1]
  if (!latest?.image_url) return null
  const concept = concepts.find((item) => item.id === latest.concept_id)
  const critique = latest.critique

  return (
    <section className="mt-10 grid gap-6 rounded-3xl border border-line bg-panel p-4 md:grid-cols-[minmax(0,1.4fr)_minmax(16rem,0.8fr)] md:p-5">
      <img src={latest.image_url} alt={concept?.hook ?? "Generated thumbnail"} className="aspect-video w-full rounded-2xl bg-ink object-cover" />
      <div className="flex flex-col justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.16em] text-gold">{concept?.name ?? "Thumbnail"}</p>
          <h2 className="mt-2 font-serif text-3xl">{latest.design_spec.text.content}</h2>
          {critique && (
            <p className="mt-3 text-sm text-mist">
              Quality review {critique.overall}/100{critique.passed ? "" : " — still has issues"}
              {generations.length > 1 ? ` after ${generations.length} passes` : ""}.
            </p>
          )}
          {critique?.issues.map((issue) => (
            <p key={issue.type} className="mt-2 text-sm text-paper">
              {issue.message}
            </p>
          ))}
        </div>
        <div className="flex flex-wrap gap-2">
          <Link to={`/projects/${projectId}/editor/${latest.id}`} className="rounded-full bg-paper px-4 py-2 text-sm font-medium text-ink">
            Edit type
          </Link>
          <a href={`/api/generations/${latest.id}/export?format=png`} className="rounded-full border border-line px-4 py-2 text-sm">
            Download PNG
          </a>
        </div>
      </div>
    </section>
  )
}
