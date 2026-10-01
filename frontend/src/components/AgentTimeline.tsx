import type { AgentRun, ProjectStatus } from "../types"

const STEPS = [
  ["video_analyst", "Understanding the video"],
  ["reference_analyst", "Studying references"],
  ["hook_strategist", "Writing hooks"],
  ["creative_director", "Directing concepts"],
  ["visual_director", "Framing the shot"],
  ["image_generator", "Rendering"],
  ["critic", "Quality review"],
] as const

export function AgentTimeline({ runs, status }: { runs: AgentRun[]; status: ProjectStatus }) {
  const latest = new Map<string, AgentRun>()
  for (const run of runs) {
    latest.set(run.agent, run)
  }
  const showRender =
    status === "generating" ||
    status === "ready" ||
    runs.some((run) => run.agent === "visual_director" || run.agent === "image_generator" || run.agent === "critic")

  return (
    <ol className="mt-8 grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
      {STEPS.map(([id, label], index) => {
        const run = latest.get(id)
        const hidden = index >= 4 && !showRender && !run
        if (hidden) return null
        const state = run?.status ?? "pending"
        const mark = state === "completed" ? "✓" : state === "failed" ? "!" : state === "running" ? "●" : "○"
        return (
          <li key={id} className="flex items-center gap-3 rounded-xl border border-line bg-panel px-3 py-3">
            <span className={state === "running" ? "text-gold" : state === "failed" ? "text-ember" : "text-mist"}>
              {mark}
            </span>
            <span className="text-sm">{label}</span>
          </li>
        )
      })}
    </ol>
  )
}
