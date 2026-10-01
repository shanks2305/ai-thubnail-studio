import { useQueryClient } from "@tanstack/react-query"
import { useState, type FormEvent } from "react"
import { Link, useNavigate, useSearchParams } from "react-router-dom"
import { ApiError, api } from "../api"
import { FormSection } from "../components/FormSection"
import { Icon } from "../components/Icon"
import { ReferencePicker } from "../components/ReferencePicker"
import { Spinner } from "../components/Spinner"
import { TopBar } from "../components/TopBar"
import type { ProjectDetail } from "../types"

const MIN_DESCRIPTION = 8

export function CreateProject() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [description, setDescription] = useState(params.get("prompt") ?? "")
  const [youtube, setYoutube] = useState("")
  const [files, setFiles] = useState<File[]>([])
  const [error, setError] = useState<string | null>(null)
  const [pending, setPending] = useState(false)
  const tooShort = description.trim().length < MIN_DESCRIPTION

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
    <>
      <TopBar crumbs={[{ label: "Projects", to: "/" }, { label: "New project" }]} />
      <main className="mx-auto w-full max-w-4xl px-6 py-8">
        <h1 className="text-2xl font-semibold tracking-tight">New project</h1>
        <p className="mt-1 text-sm text-mist">A description is enough. A YouTube link and reference thumbnails sharpen the direction.</p>
        <form onSubmit={(event) => void onSubmit(event)} className="card mt-6 overflow-hidden">
          <FormSection step={1} title="Describe the video" hint="The hook, the stakes, and who it is for.">
            <textarea
              required
              autoFocus
              minLength={MIN_DESCRIPTION}
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              aria-label="Video description"
              placeholder="I tested 20 AI coding tools to see which one can actually replace a developer."
              className="field min-h-36 resize-y leading-6"
            />
          </FormSection>
          <FormSection step={2} title="YouTube link" hint="Pulls the title and context from the video." optional>
            <input inputMode="url" value={youtube} onChange={(event) => setYoutube(event.target.value)} aria-label="YouTube link" placeholder="https://youtube.com/watch?v=…" className="field" />
          </FormSection>
          <FormSection step={3} title="References" hint="Thumbnails whose style you want to borrow." optional>
            <ReferencePicker files={files} onChange={setFiles} />
          </FormSection>
          {error && <p role="alert" className="mx-6 mb-4 rounded-lg border border-ember/40 bg-ember/5 px-4 py-3 text-sm text-ember">{error}</p>}
          <div className="flex items-center justify-between gap-4 border-t border-line bg-ink/40 px-6 py-4">
            <span className="text-xs text-mist">{tooShort ? `Description needs at least ${MIN_DESCRIPTION} characters` : "Generates four concept directions"}</span>
            <div className="flex gap-2">
              <Link to="/" className="btn-ghost">Cancel</Link>
              <button type="submit" disabled={pending || tooShort} className="btn-primary">
                {pending ? <Spinner /> : <Icon name="sparkles" />}
                {pending ? "Starting…" : "Generate concepts"}
              </button>
            </div>
          </div>
        </form>
      </main>
    </>
  )
}
