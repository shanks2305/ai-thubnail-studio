import { Link } from "react-router-dom"
import { DeleteButton } from "./DeleteButton"
import { Icon } from "./Icon"
import { Spinner } from "./Spinner"
import type { Concept, Generation } from "../types"

function scoreTone(score: number, passed: boolean) {
  if (!passed) return "bg-ember/10 text-ember ring-ember/30"
  return score >= 80 ? "bg-emerald-400/10 text-emerald-300 ring-emerald-400/25" : "bg-gold/10 text-gold ring-gold/25"
}

export function EmptyCanvas({ message, busy }: { message: string; busy: boolean }) {
  return (
    <section className="card bg-dots grid aspect-[16/7] place-items-center p-6">
      <div className="flex items-center gap-2.5 rounded-lg border border-line bg-panel px-4 py-2.5 text-sm text-mist shadow-lg shadow-black/40">
        {busy ? <Spinner className="border-gold/30 border-t-gold" /> : <Icon name="layers" className="h-4 w-4" />}
        {message}
      </div>
    </section>
  )
}

type Props = {
  projectId: string
  generation: Generation
  imageUrl: string
  passes: number
  concept: Concept | undefined
  onDelete: () => void
  deleteDisabled: boolean
}

export function ResultPanel({ projectId, generation, imageUrl, passes, concept, onDelete, deleteDisabled }: Props) {
  const critique = generation.critique

  return (
    <section className="card overflow-hidden">
      <div className="bg-dots grid place-items-center border-b border-line bg-ink/50 p-6">
        <img src={imageUrl} alt={concept?.hook ?? "Generated thumbnail"} className="aspect-video w-full max-w-3xl rounded-lg object-cover shadow-2xl shadow-black/60 ring-1 ring-line" />
      </div>
      <div className="flex flex-wrap items-center justify-between gap-4 px-4 py-3">
        <div className="flex min-w-0 items-center gap-3">
          {critique && (
            <span title="Quality score" className={`grid h-9 w-9 shrink-0 place-items-center rounded-lg text-sm font-semibold tabular-nums ring-1 ring-inset ${scoreTone(critique.overall, critique.passed)}`}>
              {critique.overall}
            </span>
          )}
          <div className="min-w-0">
            <p className="truncate text-sm font-medium">{generation.design_spec.text.content}</p>
            <p className="truncate text-xs text-mist">
              {concept?.name ?? "Thumbnail"}
              {critique && ` · review ${critique.passed ? "passed" : "has issues"}`}
              {passes > 1 && ` · ${passes} passes`}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Link to={`/projects/${projectId}/editor/${generation.id}`} className="btn-light">
            <Icon name="pen" /> Edit
          </Link>
          <a href={`/api/generations/${generation.id}/export?format=png`} className="btn-outline">
            <Icon name="download" /> PNG
          </a>
          <DeleteButton label="thumbnail" disabled={deleteDisabled} onDelete={onDelete} />
        </div>
      </div>
      {critique && critique.issues.length > 0 && (
        <ul className="space-y-1.5 border-t border-line bg-ink/30 px-4 py-3">
          {critique.issues.map((issue) => (
            <li key={issue.type} className="flex gap-2 text-xs text-mist">
              <span aria-hidden className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-ember" />
              {issue.message}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
