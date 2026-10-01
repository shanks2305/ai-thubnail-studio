import { useQuery } from "@tanstack/react-query"
import { systemQuery } from "../queries"

export function SystemStatusCard() {
  const system = useQuery(systemQuery)
  const dot = system.isError ? "bg-ember" : system.data ? "bg-emerald-400" : "animate-pulse bg-mist"
  const headline = system.isError ? "API offline" : system.data ? "Providers connected" : "Connecting…"
  const rows = system.data
    ? [
        ["Concepts", system.data.chat_provider],
        ["Judge", system.data.judge_provider],
        ["Images", system.data.image_provider],
      ]
    : []

  return (
    <div className="rounded-lg border border-line bg-ink/60 p-3 text-xs" title={system.data?.message}>
      <p className="flex items-center gap-2 font-medium text-paper">
        <span aria-hidden className={`h-1.5 w-1.5 rounded-full ${dot}`} />
        {headline}
        {system.data && <span className="ml-auto rounded bg-panel-2 px-1.5 py-0.5 text-[10px] uppercase text-mist">{system.data.environment === "production" ? "prod" : "dev"}</span>}
      </p>
      {rows.length > 0 && (
        <dl className="mt-2.5 space-y-1">
          {rows.map(([label, value]) => (
            <div key={label} className="flex justify-between text-mist">
              <dt>{label}</dt>
              <dd className="font-mono text-paper/80">{value}</dd>
            </div>
          ))}
        </dl>
      )}
    </div>
  )
}
