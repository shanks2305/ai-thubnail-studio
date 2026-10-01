import { Link } from "react-router-dom"
import { Icon } from "./Icon"
import { StatusPill } from "./StatusPill"
import type { ProjectSummary } from "../types"

const relativeTime = new Intl.RelativeTimeFormat(undefined, { numeric: "auto" })
const UNITS: [Intl.RelativeTimeFormatUnit, number][] = [
  ["day", 86_400],
  ["hour", 3_600],
  ["minute", 60],
]

function formatUpdated(iso: string) {
  const seconds = (new Date(iso).getTime() - Date.now()) / 1000
  for (const [unit, size] of UNITS) {
    if (Math.abs(seconds) >= size) return relativeTime.format(Math.round(seconds / size), unit)
  }
  return "just now"
}

type Props = {
  project: ProjectSummary
  onToggleFavorite: (project: ProjectSummary) => void
}

export function ProjectCard({ project, onToggleFavorite }: Props) {
  const href = `/projects/${project.id}`

  return (
    <article className="group card overflow-hidden transition hover:border-line-strong hover:shadow-xl hover:shadow-black/40">
      <Link to={href} className="relative block overflow-hidden border-b border-line bg-ink" tabIndex={-1} aria-hidden>
        {project.cover_url ? (
          <img src={project.cover_url} alt="" className="aspect-video w-full object-cover transition duration-500 group-hover:scale-[1.02]" />
        ) : (
          <div className="grid aspect-video place-items-center bg-dots text-mist/60">
            <Icon name="sparkles" className="h-6 w-6" />
          </div>
        )}
      </Link>
      <div className="flex items-start justify-between gap-3 p-3.5">
        <div className="min-w-0">
          <Link to={href} className="line-clamp-1 text-sm font-medium hover:text-ember">
            {project.title}
          </Link>
          <div className="mt-2 flex items-center gap-2">
            <StatusPill status={project.status} />
            <span className="text-xs text-mist">{formatUpdated(project.updated_at)}</span>
          </div>
        </div>
        <button
          type="button"
          onClick={() => onToggleFavorite(project)}
          aria-pressed={project.favorite}
          aria-label={project.favorite ? "Remove from saved" : "Save project"}
          className={`grid h-8 w-8 shrink-0 place-items-center rounded-md transition ${project.favorite ? "text-gold" : "text-mist/60 hover:bg-panel-2 hover:text-paper"}`}
        >
          <Icon name="star" filled={project.favorite} />
        </button>
      </div>
    </article>
  )
}

export function ProjectCardSkeleton() {
  return (
    <div className="card overflow-hidden">
      <div className="aspect-video animate-pulse bg-panel-2" />
      <div className="space-y-2 p-3.5">
        <div className="h-4 w-3/4 animate-pulse rounded bg-panel-2" />
        <div className="h-3 w-1/3 animate-pulse rounded bg-panel-2" />
      </div>
    </div>
  )
}
