import { useQueryClient } from "@tanstack/react-query"
import { useState, type FormEvent } from "react"
import { Link, useNavigate, useSearchParams } from "react-router-dom"
import { ApiError, api } from "../api"
import { FormSection } from "../components/FormSection"
import { Icon } from "../components/Icon"
import { LibraryPickers } from "../components/LibraryPickers"
import { ReferencePicker } from "../components/ReferencePicker"
import { StylePicker, type CreativeStyleId } from "../components/StylePicker"
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
  const [brandKitId, setBrandKitId] = useState("")
  const [profileId, setProfileId] = useState("")
  const [channelId, setChannelId] = useState("")
  const [face, setFace] = useState<File | null>(null)
  const [people, setPeople] = useState<File[]>([])
  const [style, setStyle] = useState<CreativeStyleId>("cinematic")
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
          brand_kit_id: brandKitId || null,
          creator_profile_id: profileId || null,
          channel_id: channelId || null,
          creative_style: style,
        }),
      })
      if (face) {
        const form = new FormData()
        form.append("file", face)
        await api(`/api/projects/${project.id}/face`, { method: "POST", body: form })
      }
      if (people.length > 0) {
        const form = new FormData()
        people.forEach((file) => form.append("files", file))
        await api(`/api/projects/${project.id}/people`, { method: "POST", body: form })
      }
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
          <FormSection step={2} title="Creative style" hint="The look of the background. Your photos stay photographic on top of it.">
            <StylePicker value={style} onChange={setStyle} />
          </FormSection>
          <FormSection step={3} title="YouTube link" hint="Pulls the title, and uses people already visible in that video when you do not upload photos." optional>
            <input inputMode="url" value={youtube} onChange={(event) => setYoutube(event.target.value)} aria-label="YouTube link" placeholder="https://youtube.com/watch?v=…" className="field" />
          </FormSection>
          <FormSection step={4} title="References" hint="Thumbnails whose style you want to borrow." optional>
            <ReferencePicker files={files} onChange={setFiles} />
          </FormSection>
          <FormSection step={5} title="People and brand" hint="The creator and anyone who appears in the video are placed on the thumbnail." optional>
            <LibraryPickers
              brandKitId={brandKitId}
              profileId={profileId}
              channelId={channelId}
              onBrand={setBrandKitId}
              onProfile={setProfileId}
              onChannel={setChannelId}
              face={face}
              onFace={setFace}
              people={people}
              onPeople={setPeople}
            />
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
