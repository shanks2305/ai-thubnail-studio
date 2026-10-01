import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect } from "react"
import { useParams } from "react-router-dom"
import { api } from "../api"
import { AgentTimeline } from "../components/AgentTimeline"
import { ConceptGrid } from "../components/ConceptGrid"
import { ProjectBrief } from "../components/ProjectBrief"
import { EmptyCanvas, ResultPanel } from "../components/ResultPanel"
import { StatusPill } from "../components/StatusPill"
import { TopBar } from "../components/TopBar"
import type { ProjectDetail } from "../types"

function canvasMessage(project: ProjectDetail) {
  if (project.status === "generating") return "Rendering thumbnail…"
  if (project.status === "analyzing") return "Writing concepts…"
  if (project.concepts.length > 0) return "Pick a concept below to render"
  return "Nothing rendered yet"
}

export function ProjectPage() {
  const { projectId = "" } = useParams()
  const queryClient = useQueryClient()
  const project = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => api<ProjectDetail>(`/api/projects/${projectId}`),
    refetchInterval: (query) => {
      const status = query.state.data?.status
      return status === "analyzing" || status === "generating" ? 1200 : false
    },
  })

  useEffect(() => {
    const source = new EventSource(`/api/projects/${projectId}/events`)
    source.onmessage = () => {
      void queryClient.invalidateQueries({ queryKey: ["project", projectId] })
    }
    return () => source.close()
  }, [projectId, queryClient])

  const generate = useMutation({
    mutationFn: (conceptId: string) =>
      api(`/api/projects/${projectId}/concepts/${conceptId}/generate`, { method: "POST" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["project", projectId] }),
  })
  const retry = useMutation({
    mutationFn: () => api(`/api/projects/${projectId}/generate`, { method: "POST" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["project", projectId] }),
  })

  const crumbs = [{ label: "Projects", to: "/" }, { label: project.data?.title ?? "Project" }]
  if (project.isLoading) return <TopBar crumbs={crumbs} />
  if (project.isError || !project.data) {
    return (
      <>
        <TopBar crumbs={crumbs} />
        <p className="px-6 py-8 text-sm text-ember">This project is not available.</p>
      </>
    )
  }

  const data = project.data
  const busy = data.status === "analyzing" || data.status === "generating" || generate.isPending
  const latestFailure = [...data.agent_runs].reverse().find((run) => run.status === "failed")
  const errorMessage = data.error || latestFailure?.error
  const latest = data.generations.at(-1)

  return (
    <>
      <TopBar crumbs={crumbs}>
        <StatusPill status={data.status} />
      </TopBar>
      <main className="mx-auto grid w-full max-w-7xl gap-6 px-6 py-6 lg:grid-cols-[minmax(0,1fr)_18rem]">
        <div className="min-w-0 space-y-6">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">{data.title}</h1>
            <p className="mt-1.5 max-w-3xl text-sm leading-6 text-mist">{data.description}</p>
          </div>
          {errorMessage && (
            <div role="alert" className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-ember/40 bg-ember/5 px-4 py-3">
              <p className="text-sm">{errorMessage}</p>
              {data.concepts.length === 0 && (
                <button type="button" onClick={() => retry.mutate()} disabled={retry.isPending} className="btn-outline">
                  Try again
                </button>
              )}
            </div>
          )}
          {latest?.image_url ? (
            <ResultPanel
              projectId={projectId}
              generation={latest}
              imageUrl={latest.image_url}
              passes={data.generations.length}
              concept={data.concepts.find((item) => item.id === latest.concept_id)}
            />
          ) : (
            <EmptyCanvas message={canvasMessage(data)} busy={data.status === "analyzing" || data.status === "generating"} />
          )}
          {data.concepts.length > 0 && (
            <ConceptGrid
              concepts={data.concepts}
              busy={busy}
              pendingId={generate.isPending ? generate.variables ?? null : null}
              selectedId={latest ? data.selected_concept_id : null}
              onGenerate={(conceptId) => generate.mutate(conceptId)}
            />
          )}
        </div>
        <aside className="space-y-4 lg:sticky lg:top-20 lg:self-start">
          <AgentTimeline runs={data.agent_runs} status={data.status} />
          <ProjectBrief project={data} />
        </aside>
      </main>
    </>
  )
}
