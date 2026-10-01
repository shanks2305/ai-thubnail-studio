import { useQuery, useQueryClient } from "@tanstack/react-query"
import { Link } from "react-router-dom"
import { useState } from "react"
import { api } from "../api"
import { StatusPill } from "../components/StatusPill"
import type { ProjectSummary } from "../types"

const EXAMPLES = [
  "I tested 20 AI coding tools to see which one can actually replace a developer.",
  "I lived in a $50 tent for 30 days and this is what broke first.",
  "The keyboard shortcut that gave me two hours back every week.",
]

type Filter = "all" | "open" | "ready" | "saved"

export function Dashboard() {
  const queryClient = useQueryClient()
  const [filter, setFilter] = useState<Filter>("all")
  const projects = useQuery({
    queryKey: ["projects"],
    queryFn: () => api<ProjectSummary[]>("/api/projects"),
  })
  const visible = (projects.data ?? []).filter((project) => matches(project, filter))

  async function toggleFavorite(project: ProjectSummary) {
    await api(`/api/projects/${project.id}`, {
      method: "PATCH",
      body: JSON.stringify({ favorite: !project.favorite }),
    })
    await queryClient.invalidateQueries({ queryKey: ["projects"] })
  }

  return (
    <main className="mx-auto max-w-6xl px-5 py-10">
      <p className="text-xs uppercase tracking-[0.2em] text-gold">Studio</p>
      <h1 className="mt-3 max-w-xl font-serif text-5xl leading-[1.05] tracking-tight">
        Thumbnails with a point of view.
      </h1>
      <p className="mt-4 max-w-xl text-mist">
        Describe the video. The studio writes the hooks, chooses a frame, and renders a thumbnail you can still edit.
      </p>

      {projects.data && projects.data.length > 0 && (
        <div className="mt-8 flex flex-wrap gap-2">
          {(["all", "open", "ready", "saved"] as const).map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => setFilter(item)}
              className={`rounded-full px-3 py-1.5 text-sm ${filter === item ? "bg-paper text-ink" : "border border-line text-mist"}`}
            >
              {item === "all" ? "All" : item === "open" ? "In progress" : item === "ready" ? "Ready" : "Saved"}
            </button>
          ))}
        </div>
      )}

      {projects.isLoading && <p className="mt-10 text-mist">Loading projects…</p>}
      {projects.isError && <p className="mt-10 text-ember">The studio could not load projects. Is the API running?</p>}

      {projects.data && projects.data.length === 0 && (
        <div className="mt-10 rounded-3xl border border-line bg-panel p-6">
          <h2 className="font-serif text-3xl">Start with a description</h2>
          <div className="mt-4 grid gap-3">
            {EXAMPLES.map((prompt) => (
              <Link key={prompt} to={`/new?prompt=${encodeURIComponent(prompt)}`} className="rounded-2xl border border-line bg-panel-2 px-4 py-3 text-sm leading-6 hover:border-gold">
                {prompt}
              </Link>
            ))}
          </div>
        </div>
      )}

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        {visible.map((project) => (
          <article key={project.id} className="overflow-hidden rounded-2xl border border-line bg-panel">
            <Link to={`/projects/${project.id}`} className="block">
              {project.cover_url ? (
                <img src={project.cover_url} alt="" className="aspect-video w-full object-cover" />
              ) : (
                <div className="grid aspect-video place-items-center bg-panel-2 px-6 text-center font-serif text-2xl">
                  {project.title}
                </div>
              )}
            </Link>
            <div className="flex items-start justify-between gap-3 px-4 py-4">
              <div>
                <Link to={`/projects/${project.id}`} className="font-medium">
                  {project.title}
                </Link>
                <div className="mt-2">
                  <StatusPill status={project.status} />
                </div>
              </div>
              <button type="button" onClick={() => void toggleFavorite(project)} className="text-sm text-gold">
                {project.favorite ? "Saved" : "Save"}
              </button>
            </div>
          </article>
        ))}
      </div>
    </main>
  )
}

function matches(project: ProjectSummary, filter: Filter) {
  if (filter === "ready") return project.status === "ready"
  if (filter === "saved") return project.favorite
  if (filter === "open") return project.status !== "ready"
  return true
}
