import type { ProjectSummary } from "./types"

export const FILTERS = [
  { id: "all", label: "All projects" },
  { id: "open", label: "In progress" },
  { id: "ready", label: "Ready" },
  { id: "saved", label: "Saved" },
] as const

export type Filter = (typeof FILTERS)[number]["id"]

export function parseFilter(value: string | null): Filter {
  return FILTERS.find((filter) => filter.id === value)?.id ?? "all"
}

export function matchesFilter(project: ProjectSummary, filter: Filter) {
  if (filter === "ready") return project.status === "ready"
  if (filter === "saved") return project.favorite
  if (filter === "open") return project.status !== "ready"
  return true
}
