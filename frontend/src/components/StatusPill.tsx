import type { ProjectStatus } from "../types"
import { STATUS_LABEL } from "../types"

const TONE: Record<ProjectStatus, string> = {
  draft: "text-mist border-line",
  analyzing: "text-gold border-gold/40",
  concepts_ready: "text-paper border-line",
  generating: "text-gold border-gold/40",
  ready: "text-paper border-ember/50",
  failed: "text-ember border-ember/40",
}

export function StatusPill({ status }: { status: ProjectStatus }) {
  return (
    <span className={`rounded-full border px-2.5 py-1 text-xs uppercase tracking-[0.14em] ${TONE[status]}`}>
      {STATUS_LABEL[status]}
    </span>
  )
}
