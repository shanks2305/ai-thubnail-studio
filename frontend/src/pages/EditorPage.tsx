import { useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { ApiError, api } from "../api"
import { EditorToolbar, type SaveState } from "../components/EditorToolbar"
import { HeadlineControls } from "../components/HeadlineControls"
import { TopBar } from "../components/TopBar"
import type { Generation, ProjectDetail, TextSpec } from "../types"

export function EditorPage() {
  const { projectId = "", generationId = "" } = useParams()
  const queryClient = useQueryClient()
  const project = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => api<ProjectDetail>(`/api/projects/${projectId}`),
  })
  const generation = project.data?.generations.find((item) => item.id === generationId)
  const [text, setText] = useState<TextSpec | null>(null)
  const [imageUrl, setImageUrl] = useState<string | null>(null)
  const [save, setSave] = useState<SaveState>({ status: "idle" })

  useEffect(() => {
    if (!generation || text) return
    setText(generation.design_spec.text)
    setImageUrl(generation.image_url)
  }, [generation, text])

  useEffect(() => {
    if (!text || !generation || !text.content.trim()) return
    const current = generation.design_spec.text
    const unchanged =
      current.content === text.content &&
      current.position === text.position &&
      current.size === text.size &&
      current.color === text.color
    if (unchanged) return
    const handle = window.setTimeout(() => {
      setSave({ status: "saving" })
      void api<Generation>(`/api/generations/${generationId}`, {
        method: "PATCH",
        body: JSON.stringify(text),
      })
        .then((updated) => {
          setImageUrl(updated.image_url)
          setSave({ status: "saved" })
          queryClient.setQueryData<ProjectDetail>(["project", projectId], (currentProject) => {
            if (!currentProject) return currentProject
            return {
              ...currentProject,
              generations: currentProject.generations.map((item) => (item.id === updated.id ? updated : item)),
            }
          })
        })
        .catch((caught: unknown) => {
          setSave({ status: "error", message: caught instanceof ApiError ? caught.message : "Could not update the headline." })
        })
    }, 400)
    return () => window.clearTimeout(handle)
  }, [generation, generationId, projectId, queryClient, text])

  const crumbs = [
    { label: "Projects", to: "/" },
    { label: project.data?.title ?? "Project", to: `/projects/${projectId}` },
    { label: "Editor" },
  ]
  if (project.isLoading) return <TopBar crumbs={crumbs} />
  if (!generation || !text) {
    return (
      <>
        <TopBar crumbs={crumbs} />
        <p className="px-6 py-8 text-sm text-ember">This thumbnail is not on the project.</p>
      </>
    )
  }

  return (
    <>
      <TopBar crumbs={crumbs}>
        <EditorToolbar save={save} generationId={generationId} />
      </TopBar>
      <main className="flex flex-1 flex-col lg:flex-row">
        <div className="bg-dots flex flex-1 items-center justify-center p-6 lg:p-10">
          {imageUrl && (
            <img src={imageUrl} alt="Thumbnail preview" className={`aspect-video w-full max-w-4xl rounded-lg object-cover shadow-2xl shadow-black/70 ring-1 ring-line transition ${save.status === "saving" ? "opacity-70" : ""}`} />
          )}
        </div>
        <aside className="w-full shrink-0 border-t border-line bg-panel lg:w-80 lg:border-l lg:border-t-0">
          <div className="flex h-11 items-center border-b border-line px-4 text-sm font-medium">Text layer</div>
          <form onSubmit={(event) => event.preventDefault()}>
            <HeadlineControls text={text} onChange={setText} />
          </form>
        </aside>
      </main>
    </>
  )
}
