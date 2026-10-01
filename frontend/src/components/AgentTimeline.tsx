import { Spinner } from "./Spinner"
import { Icon } from "./Icon"
import type { AgentRun, ProjectStatus } from "../types"

const STEPS = [
  ["video_analyst", "Understanding the video"],
  ["audience_analyst", "Reading the audience"],
  ["researcher", "Researching the video"],
  ["reference_analyst", "Studying references"],
  ["hook_strategist", "Writing hooks"],
  ["creative_director", "Directing concepts"],
  ["visual_director", "Framing the shot"],
  ["image_generator", "Rendering"],
  ["critic", "Quality review"],
] as const

const STATE_LABEL: Record<string, string> = {
  completed: "Done",
  running: "Running",
  failed: "Failed",
  pending: "Queued",
}

function Mark({ state }: { state: string }) {
  if (state === "running") return <Spinner className="border-gold/30 border-t-gold" />
  if (state === "completed") return <Icon name="check" className="h-3 w-3 text-emerald-300" />
  if (state === "failed") return <Icon name="x" className="h-3 w-3 text-ember" />
  return <span className="h-1.5 w-1.5 rounded-full bg-line-strong" />
}

export function AgentTimeline({ runs, status }: { runs: AgentRun[]; status: ProjectStatus }) {
  const latest = new Map<string, AgentRun>()
  for (const run of runs) {
    latest.set(run.agent, run)
  }
  const showRender =
    status === "generating" ||
    status === "ready" ||
    runs.some((run) => run.agent === "visual_director" || run.agent === "image_generator" || run.agent === "critic")
  const steps = STEPS.filter(([id], index) => {
    if (id === "audience_analyst" || id === "researcher") return latest.has(id) || status === "analyzing"
    return index < 6 || showRender || latest.has(id)
  })
  const done = steps.filter(([id]) => latest.get(id)?.status === "completed").length

  return (
    <section className="card p-4" aria-label="Pipeline progress">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-medium">Pipeline</h2>
        <span className="text-xs tabular-nums text-mist">{done} of {steps.length}</span>
      </div>
      <div className="mt-3 h-1 overflow-hidden rounded-full bg-panel-2">
        <div className="h-full rounded-full bg-gradient-to-r from-ember to-gold transition-all duration-700" style={{ width: `${(done / steps.length) * 100}%` }} />
      </div>
      <ol className="mt-4">
        {steps.map(([id, label], index) => {
          const run = latest.get(id)
          const state = run?.status ?? "pending"
          return (
            <li key={id} className="relative flex gap-3 pb-3.5 last:pb-0">
              {index < steps.length - 1 && <span aria-hidden className="absolute bottom-0 left-[11px] top-6 w-px bg-line" />}
              <span className={`relative grid h-6 w-6 shrink-0 place-items-center rounded-full border bg-ink ${state === "running" ? "border-gold/50" : state === "failed" ? "border-ember/50" : "border-line"}`}>
                <Mark state={state} />
              </span>
              <div className="min-w-0 pt-0.5">
                <p className={`text-sm ${state === "pending" ? "text-mist" : "text-paper"}`}>{label}</p>
                <p className="mt-0.5 text-xs text-mist/70">
                  {STATE_LABEL[state] ?? state}
                  {run?.duration_ms != null && ` · ${(run.duration_ms / 1000).toFixed(1)}s`}
                  {run?.provider && <span className="font-mono"> · {run.provider}</span>}
                </p>
              </div>
            </li>
          )
        })}
      </ol>
    </section>
  )
}
