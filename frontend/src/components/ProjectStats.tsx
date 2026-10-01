import { Link } from "react-router-dom"
import { FILTERS, matchesFilter, type Filter } from "../projectFilters"
import type { ProjectSummary } from "../types"

export function ProjectStats({ projects, active }: { projects: ProjectSummary[]; active: Filter }) {
  return (
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-4" role="tablist" aria-label="Filter projects">
      {FILTERS.map((filter) => {
        const selected = filter.id === active
        const count = projects.filter((project) => matchesFilter(project, filter.id)).length
        return (
          <Link
            key={filter.id}
            to={filter.id === "all" ? "/" : `/?filter=${filter.id}`}
            role="tab"
            aria-selected={selected}
            className={`card px-4 py-3.5 transition ${selected ? "border-ember/50 bg-ember/[0.04] ring-1 ring-ember/20" : "hover:border-line-strong"}`}
          >
            <p className="label">{filter.label}</p>
            <p className="mt-1.5 text-2xl font-semibold tabular-nums tracking-tight">{count}</p>
          </Link>
        )
      })}
    </div>
  )
}
