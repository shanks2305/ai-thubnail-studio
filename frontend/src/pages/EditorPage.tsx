import { useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import { ApiError, api } from "../api"
import { reportDelete } from "../components/DeleteButton"
import { EditorToolbar, type SaveState } from "../components/EditorToolbar"
import { HeadlineControls } from "../components/HeadlineControls"
import { LayoutControls } from "../components/LayoutControls"
import { TopBar } from "../components/TopBar"
import { draftFromGeneration, draftsMatch, type EditorDraft } from "../editorState"
import type { Generation, ProjectDetail } from "../types"

export function EditorPage() {
  const { projectId = "", generationId = "" } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const project = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => api<ProjectDetail>(`/api/projects/${projectId}`),
  })
  const generation = project.data?.generations.find((item) => item.id === generationId)
  const [draft, setDraft] = useState<EditorDraft | null>(null)
  const [imageUrl, setImageUrl] = useState<string | null>(null)
  const [safeZone, setSafeZone] = useState(true)
  const [save, setSave] = useState<SaveState>({ status: "idle" })
  const [note, setNote] = useState("")

  useEffect(() => {
    if (!generation || draft) return
    setDraft(draftFromGeneration(generation))
    setImageUrl(generation.image_url)
  }, [generation, draft])

  useEffect(() => {
    if (!draft || !generation || !draft.text.content.trim()) return
    if (draftsMatch(draftFromGeneration(generation), draft)) return
    const handle = window.setTimeout(() => {
      setSave({ status: "saving" })
      void api<Generation>(`/api/generations/${generationId}`, {
        method: "PATCH",
        body: JSON.stringify({
          ...draft.text,
          scrim_strength: draft.scrimStrength,
          palette: draft.palette,
          recolor: draft.recolor,
        }),
      })
        .then((updated) => {
          setImageUrl(updated.image_url)
          setSave({ status: "saved" })
          queryClient.setQueryData<ProjectDetail>(["project", projectId], (current) =>
            current ? { ...current, generations: current.generations.map((item) => (item.id === updated.id ? updated : item)) } : current,
          )
        })
        .catch((caught: unknown) => {
          setSave({ status: "error", message: caught instanceof ApiError ? caught.message : "Could not update the thumbnail." })
        })
    }, 400)
    return () => window.clearTimeout(handle)
  }, [draft, generation, generationId, projectId, queryClient])

  const crumbs = [
    { label: "Projects", to: "/" },
    { label: project.data?.title ?? "Project", to: `/projects/${projectId}` },
    { label: "Editor" },
  ]
  if (project.isLoading) return <TopBar crumbs={crumbs} />
  if (!generation || !draft || !project.data) {
    return (
      <>
        <TopBar crumbs={crumbs} />
        <p className="px-6 py-8 text-sm text-ember">This thumbnail is not on the project.</p>
      </>
    )
  }

  const history = project.data.generations.filter((item) => item.concept_id === generation.concept_id)

  return (
    <>
      <TopBar crumbs={crumbs}>
        <EditorToolbar
          save={save}
          generationId={generationId}
          onDelete={() => {
            void api(`/api/generations/${generationId}`, { method: "DELETE" })
              .then(() => navigate(`/projects/${projectId}`))
              .catch(reportDelete)
          }}
        />
      </TopBar>
      <main className="flex flex-1 flex-col lg:flex-row">
        <div className="bg-dots flex flex-1 items-center justify-center p-6 lg:p-10">
          {imageUrl && (
            <div className="relative w-full max-w-4xl">
              <img src={imageUrl} alt="Thumbnail preview" className={`aspect-video w-full rounded-lg object-cover shadow-2xl shadow-black/70 ring-1 ring-line ${save.status === "saving" ? "opacity-70" : ""}`} />
              {safeZone && (
                <div className="pointer-events-none absolute inset-0" aria-hidden>
                  <div className="absolute inset-y-0 right-0 w-[12%] bg-ember/15" />
                  <div className="absolute inset-x-0 bottom-0 h-[14%] bg-gold/15" />
                </div>
              )}
            </div>
          )}
        </div>
        <aside className="w-full shrink-0 overflow-y-auto border-t border-line bg-panel lg:w-80 lg:border-l lg:border-t-0">
          <div className="flex h-11 items-center justify-between border-b border-line px-4 text-sm font-medium">
            Text layer
            <label className="flex items-center gap-2 text-xs font-normal text-mist">
              <input type="checkbox" checked={safeZone} onChange={(event) => setSafeZone(event.target.checked)} />
              Safe zone
            </label>
          </div>
          <form onSubmit={(event) => event.preventDefault()}>
            <HeadlineControls text={draft.text} onChange={(text) => setDraft({ ...draft, text })} />
            <LayoutControls draft={draft} onChange={setDraft} />
          </form>
          <div className="space-y-3 border-t border-line px-4 py-4">
            <p className="label">Variations</p>
            <div className="flex flex-wrap gap-2">
              {(["hook", "crop", "palette", "expression"] as const).map((axis) => (
                <button key={axis} type="button" className="chip capitalize" onClick={() => void vary(projectId, generationId, axis, queryClient)}>
                  {axis}
                </button>
              ))}
            </div>
            <label className="block text-sm">
              <span className="label">Re-render note</span>
              <textarea value={note} onChange={(event) => setNote(event.target.value)} className="field mt-2 min-h-16" placeholder="Move the subject right and darken the headline side." />
            </label>
            <button type="button" className="btn-outline" onClick={() => void rerender(projectId, generationId, note)}>
              Re-render background
            </button>
            {generation.critique && generation.critique.recommended_changes.length > 0 && (
              <ul className="space-y-1 text-xs text-mist">
                {generation.critique.recommended_changes.map((change) => (
                  <li key={change}>{change}</li>
                ))}
              </ul>
            )}
            <p className="label">History</p>
            <div className="flex gap-2 overflow-x-auto">
              {history.map((item) => (
                <Link key={item.id} to={`/projects/${projectId}/editor/${item.id}`} className={`block w-24 shrink-0 ${item.id === generationId ? "ring-2 ring-ember" : ""}`}>
                  {item.image_url && <img src={item.image_url} alt="" className="aspect-video w-full rounded object-cover" />}
                  <span className="text-[11px] text-mist">Pass {item.attempt}</span>
                </Link>
              ))}
            </div>
          </div>
        </aside>
      </main>
    </>
  )
}

async function vary(projectId: string, generationId: string, axis: string, queryClient: ReturnType<typeof useQueryClient>) {
  await api(`/api/generations/${generationId}/variations`, { method: "POST", body: JSON.stringify({ axis }) })
  await queryClient.invalidateQueries({ queryKey: ["project", projectId] })
}

async function rerender(projectId: string, generationId: string, instruction: string) {
  await api(`/api/generations/${generationId}/rerender`, { method: "POST", body: JSON.stringify({ instruction }) })
  window.location.assign(`/projects/${projectId}`)
}
