import { useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { ApiError, api } from "../api"
import type { Generation, ProjectDetail, TextSpec } from "../types"

const SWATCHES = ["#ffffff", "#111111", "#f2c14e", "#ff4d2e"]
const POSITIONS: TextSpec["position"][] = ["left", "center", "right"]
const SIZES: TextSpec["size"][] = ["medium", "large", "very large"]

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
  const [note, setNote] = useState<string | null>(null)

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
      setNote("Saving…")
      void api<Generation>(`/api/generations/${generationId}`, {
        method: "PATCH",
        body: JSON.stringify(text),
      })
        .then((updated) => {
          setImageUrl(updated.image_url)
          setNote(null)
          queryClient.setQueryData<ProjectDetail>(["project", projectId], (currentProject) => {
            if (!currentProject) return currentProject
            return {
              ...currentProject,
              generations: currentProject.generations.map((item) => (item.id === updated.id ? updated : item)),
            }
          })
        })
        .catch((caught: unknown) => {
          setNote(caught instanceof ApiError ? caught.message : "Could not update the headline.")
        })
    }, 400)
    return () => window.clearTimeout(handle)
  }, [generation, generationId, projectId, queryClient, text])

  if (project.isLoading) return <p className="mx-auto max-w-6xl px-5 py-10 text-mist">Opening the editor…</p>
  if (!generation || !text) return <p className="mx-auto max-w-6xl px-5 py-10 text-ember">This thumbnail is not on the project.</p>

  return (
    <main className="mx-auto grid max-w-6xl gap-8 px-5 py-10 lg:grid-cols-[minmax(0,1fr)_18rem]">
      <div>
        <Link to={`/projects/${projectId}`} className="text-sm text-mist">
          Back to concepts
        </Link>
        <h1 className="mt-3 font-serif text-4xl">Edit the headline</h1>
        {imageUrl && <img src={imageUrl} alt="Thumbnail preview" className="mt-6 aspect-video w-full rounded-2xl bg-ink object-cover" />}
        {note && <p className="mt-3 text-sm text-mist">{note}</p>}
      </div>
      <form className="space-y-5" onSubmit={(event) => event.preventDefault()}>
        <label className="block text-sm">
          Headline
          <textarea
            value={text.content}
            maxLength={80}
            onChange={(event) => setText({ ...text, content: event.target.value })}
            className="mt-2 min-h-28 w-full rounded-2xl border border-line bg-panel px-3 py-3 outline-none focus:border-gold"
          />
        </label>
        <div>
          <p className="text-sm">Position</p>
          <div className="mt-2 flex gap-2">
            {POSITIONS.map((position) => (
              <button key={position} type="button" onClick={() => setText({ ...text, position })} className={chip(text.position === position)}>
                {position}
              </button>
            ))}
          </div>
        </div>
        <div>
          <p className="text-sm">Size</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {SIZES.map((size) => (
              <button key={size} type="button" onClick={() => setText({ ...text, size })} className={chip(text.size === size)}>
                {size}
              </button>
            ))}
          </div>
        </div>
        <div>
          <p className="text-sm">Color</p>
          <div className="mt-2 flex items-center gap-2">
            {SWATCHES.map((color) => (
              <button
                key={color}
                type="button"
                aria-label={color}
                onClick={() => setText({ ...text, color })}
                className={`h-8 w-8 rounded-full border ${text.color.toLowerCase() === color ? "border-paper" : "border-transparent"}`}
                style={{ background: color }}
              />
            ))}
            <input type="color" value={text.color} onChange={(event) => setText({ ...text, color: event.target.value })} aria-label="Custom color" />
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <a href={`/api/generations/${generationId}/export?format=png`} className="rounded-full bg-paper px-4 py-2 text-sm font-medium text-ink">PNG</a>
          <a href={`/api/generations/${generationId}/export?format=jpeg`} className="rounded-full border border-line px-4 py-2 text-sm">JPG</a>
          <a href={`/api/generations/${generationId}/export?format=webp`} className="rounded-full border border-line px-4 py-2 text-sm">WebP</a>
        </div>
      </form>
    </main>
  )
}

function chip(active: boolean) {
  return `rounded-full px-3 py-1.5 text-sm capitalize ${active ? "bg-paper text-ink" : "border border-line"}`
}
