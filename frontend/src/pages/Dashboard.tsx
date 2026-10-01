import { useQuery, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { Link, useSearchParams } from "react-router-dom"
import { api } from "../api"
import { Icon } from "../components/Icon"
import { ProjectCard, ProjectCardSkeleton } from "../components/ProjectCard"
import { ProjectStats } from "../components/ProjectStats"
import { TopBar } from "../components/TopBar"
import { matchesFilter, parseFilter } from "../projectFilters"
import { projectsQuery } from "../queries"
import type { ProjectSummary } from "../types"

const EXAMPLES = [
  "I tested 20 AI coding tools to see which one can actually replace a developer.",
  "I lived in a $50 tent for 30 days and this is what broke first.",
  "The keyboard shortcut that gave me two hours back every week.",
]

export function Dashboard() {
  const queryClient = useQueryClient()
  const [params] = useSearchParams()
  const [search, setSearch] = useState("")
  const filter = parseFilter(params.get("filter"))
  const projects = useQuery(projectsQuery)
  const all = projects.data ?? []
  const term = search.trim().toLowerCase()
  const visible = all.filter(
    (project) => matchesFilter(project, filter) && (!term || `${project.title} ${project.description}`.toLowerCase().includes(term)),
  )

  async function toggleFavorite(project: ProjectSummary) {
    await api(`/api/projects/${project.id}`, {
      method: "PATCH",
      body: JSON.stringify({ favorite: !project.favorite }),
    })
    await queryClient.invalidateQueries({ queryKey: projectsQuery.queryKey })
  }

  return (
    <>
      <TopBar crumbs={[{ label: "Projects" }]}>
        <label className="relative hidden sm:block">
          <Icon name="search" className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-mist/60" />
          <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search projects" aria-label="Search projects" className="field h-9 w-64 py-0 pl-8" />
        </label>
      </TopBar>
      <main className="mx-auto w-full max-w-7xl space-y-8 px-6 py-8">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Projects</h1>
          <p className="mt-1 text-sm text-mist">Describe a video and the studio writes the hooks, directs the frame, and renders an editable thumbnail.</p>
        </div>

        {all.length > 0 && <ProjectStats projects={all} active={filter} />}

        {projects.isError && (
          <p role="alert" className="rounded-lg border border-ember/40 bg-ember/5 px-4 py-3 text-sm text-ember">The studio could not load projects. Is the API running?</p>
        )}

        {projects.data?.length === 0 && (
          <div className="card grid place-items-center px-6 py-14 text-center">
            <span className="grid h-11 w-11 place-items-center rounded-xl bg-ember/10 text-ember ring-1 ring-ember/20">
              <Icon name="sparkles" className="h-5 w-5" />
            </span>
            <h2 className="mt-4 text-lg font-semibold">Create your first thumbnail</h2>
            <p className="mt-1 text-sm text-mist">Start from an example or write your own brief.</p>
            <div className="mt-6 grid w-full max-w-3xl gap-3 text-left md:grid-cols-3">
              {EXAMPLES.map((prompt) => (
                <Link key={prompt} to={`/new?prompt=${encodeURIComponent(prompt)}`} className="rounded-lg border border-line bg-ink p-3.5 text-sm leading-6 text-mist transition hover:border-ember/50 hover:text-paper">
                  {prompt}
                </Link>
              ))}
            </div>
          </div>
        )}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4">
          {projects.isLoading && [0, 1, 2].map((slot) => <ProjectCardSkeleton key={slot} />)}
          {visible.map((project) => (
            <ProjectCard key={project.id} project={project} onToggleFavorite={(item) => void toggleFavorite(item)} />
          ))}
        </div>

        {all.length > 0 && visible.length === 0 && (
          <p className="rounded-lg border border-dashed border-line py-10 text-center text-sm text-mist">No projects match this view.</p>
        )}
      </main>
    </>
  )
}
