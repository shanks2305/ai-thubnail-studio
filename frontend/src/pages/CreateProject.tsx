import { useQueryClient } from "@tanstack/react-query"
import { useState, type DragEvent, type FormEvent } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import { ApiError, api } from "../api"
import type { PrivacyMode, ProjectDetail } from "../types"

const PRIVACY: { id: PrivacyMode; title: string; detail: string }[] = [
  { id: "local", title: "Local", detail: "Stays on this machine." },
  { id: "hybrid", title: "Hybrid", detail: "Use a cloud model when one is configured." },
  { id: "cloud", title: "Cloud", detail: "Requires an OpenAI API key." },
]

export function CreateProject() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [description, setDescription] = useState(params.get("prompt") ?? "")
  const [youtube, setYoutube] = useState("")
  const [privacy, setPrivacy] = useState<PrivacyMode>("hybrid")
  const [files, setFiles] = useState<File[]>([])
  const [error, setError] = useState<string | null>(null)
  const [pending, setPending] = useState(false)
  const [dragging, setDragging] = useState(false)

  function addFiles(list: FileList | null) {
    if (!list) return
    setFiles((current) => [...current, ...Array.from(list)].slice(0, 6))
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    setPending(true)
    setError(null)
    try {
      const project = await api<ProjectDetail>("/api/projects", {
        method: "POST",
        body: JSON.stringify({
          description,
          youtube_url: youtube.trim() || null,
          privacy_mode: privacy,
        }),
      })
      if (files.length > 0) {
        const form = new FormData()
        files.forEach((file) => form.append("files", file))
        await api(`/api/projects/${project.id}/references`, { method: "POST", body: form })
      }
      await api(`/api/projects/${project.id}/generate`, { method: "POST" })
      await queryClient.invalidateQueries({ queryKey: ["projects"] })
      navigate(`/projects/${project.id}`)
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "Could not start the project.")
    } finally {
      setPending(false)
    }
  }

  return (
    <main className="mx-auto max-w-3xl px-5 py-10">
      <p className="text-xs uppercase tracking-[0.2em] text-gold">New project</p>
      <h1 className="mt-3 font-serif text-5xl tracking-tight">What is the video about?</h1>
      <p className="mt-4 text-mist">A description is enough. A YouTube link and a reference thumbnail make the direction sharper.</p>
      <form onSubmit={(event) => void onSubmit(event)} className="mt-8 space-y-5">
        <textarea
          required
          minLength={8}
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          placeholder="I tested 20 AI coding tools to see which one can actually replace a developer."
          className="min-h-40 w-full rounded-2xl border border-line bg-panel px-4 py-4 outline-none focus:border-gold"
        />
        <input
          value={youtube}
          onChange={(event) => setYoutube(event.target.value)}
          placeholder="YouTube URL, optional"
          className="w-full rounded-2xl border border-line bg-panel px-4 py-3 outline-none focus:border-gold"
        />
        <label
          onDragOver={(event: DragEvent) => {
            event.preventDefault()
            setDragging(true)
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(event: DragEvent) => {
            event.preventDefault()
            setDragging(false)
            addFiles(event.dataTransfer.files)
          }}
          className={`block rounded-2xl border border-dashed px-4 py-8 text-center text-sm text-mist ${dragging ? "border-gold bg-panel-2" : "border-line bg-panel"}`}
        >
          <input type="file" accept="image/png,image/jpeg,image/webp" multiple className="sr-only" onChange={(event) => addFiles(event.target.files)} />
          Drop reference thumbnails, or browse. PNG, JPG, or WebP.
          {files.length > 0 && <span className="mt-3 block text-paper">{files.map((file) => file.name).join(", ")}</span>}
        </label>
        <fieldset className="grid gap-3 sm:grid-cols-3">
          {PRIVACY.map((option) => (
            <label key={option.id} className={`rounded-2xl border px-4 py-3 ${privacy === option.id ? "border-gold bg-panel-2" : "border-line bg-panel"}`}>
              <input type="radio" name="privacy" className="sr-only" checked={privacy === option.id} onChange={() => setPrivacy(option.id)} />
              <span className="block font-medium">{option.title}</span>
              <span className="mt-1 block text-sm text-mist">{option.detail}</span>
            </label>
          ))}
        </fieldset>
        {error && <p className="text-sm text-ember">{error}</p>}
        <button type="submit" disabled={pending || description.trim().length < 8} className="rounded-full bg-ember px-5 py-2.5 text-sm font-medium text-white disabled:opacity-50">
          {pending ? "Starting…" : "Generate concepts"}
        </button>
      </form>
    </main>
  )
}
