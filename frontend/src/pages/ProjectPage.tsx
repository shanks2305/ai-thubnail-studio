import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect } from "react"
import { useParams } from "react-router-dom"
import { api } from "../api"
import { AgentTimeline } from "../components/AgentTimeline"
import { ConceptGrid } from "../components/ConceptGrid"
import { ResultPanel } from "../components/ResultPanel"
import { StatusPill } from "../components/StatusPill"
import type { ProjectDetail } from "../types"

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

  if (project.isLoading) return <p className="mx-auto max-w-6xl px-5 py-10 text-mist">Opening the project…</p>
  if (project.isError || !project.data) return <p className="mx-auto max-w-6xl px-5 py-10 text-ember">This project is not available.</p>

  const data = project.data
  const busy = data.status === "analyzing" || data.status === "generating" || generate.isPending
  const latestFailure = [...data.agent_runs].reverse().find((run) => run.status === "failed")

  return (
    <main className="mx-auto max-w-6xl px-5 py-10">
      <StatusPill status={data.status} />
      <h1 className="mt-3 max-w-3xl font-serif text-4xl tracking-tight md:text-5xl">{data.title}</h1>
      <p className="mt-4 max-w-2xl text-mist">{data.description}</p>
      {data.youtube_title && <p className="mt-2 text-sm text-gold">YouTube: {data.youtube_title}</p>}
      {(data.error || latestFailure?.error) && (
        <div className="mt-6 rounded-2xl border border-ember/40 bg-panel px-4 py-4">
          <p>{data.error || latestFailure?.error}</p>
          {data.concepts.length === 0 && (
            <button type="button" onClick={() => retry.mutate()} className="mt-3 rounded-full border border-line px-4 py-2 text-sm">
              Try again
            </button>
          )}
        </div>
      )}
      <AgentTimeline runs={data.agent_runs} status={data.status} />
      {data.references.length > 0 && (
        <div className="mt-6 flex gap-3">
          {data.references.map((reference) => (
            <img key={reference.id} src={reference.url} alt="" className="h-16 w-28 rounded-lg object-cover" />
          ))}
        </div>
      )}
      <ResultPanel projectId={projectId} generations={data.generations} concepts={data.concepts} />
      {data.concepts.length > 0 && (
        <ConceptGrid
          concepts={data.concepts}
          busy={busy}
          pendingId={generate.isPending ? generate.variables ?? null : null}
          onGenerate={(conceptId) => generate.mutate(conceptId)}
        />
      )}
      {data.status === "analyzing" && data.concepts.length === 0 && (
        <p className="mt-8 text-mist">Working through the brief, the references, and the hooks.</p>
      )}
    </main>
  )
}
