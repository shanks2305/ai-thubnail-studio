import type { ProjectStatus } from "../types"
import { STATUS_LABEL } from "../types"

const TONE: Record<ProjectStatus, string> = {
  draft: "bg-panel-2 text-mist ring-line",
  analyzing: "bg-gold/10 text-gold ring-gold/25",
  concepts_ready: "bg-sky-400/10 text-sky-300 ring-sky-400/25",
  generating: "bg-gold/10 text-gold ring-gold/25",
  ready: "bg-emerald-400/10 text-emerald-300 ring-emerald-400/25",
  failed: "bg-ember/10 text-ember ring-ember/30",
}

const PULSING: ProjectStatus[] = ["analyzing", "generating"]

export function StatusPill({ status }: { status: ProjectStatus }) {
  return (
    <span className={`inline-flex h-6 items-center gap-1.5 rounded-md px-2 text-xs font-medium ring-1 ring-inset ${TONE[status]}`}>
      <span aria-hidden className={`h-1.5 w-1.5 rounded-full bg-current ${PULSING.includes(status) ? "animate-pulse" : ""}`} />
      {STATUS_LABEL[status]}
    </span>
  )
}
