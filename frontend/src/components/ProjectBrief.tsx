import { useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "../api"
import type { ProjectDetail } from "../types"
import { DeleteButton, reportDelete } from "./DeleteButton"
import { ResearchNotes } from "./ResearchNotes"
import { StylePicker, styleLabel, type CreativeStyleId } from "./StylePicker"

export function ProjectBrief({ project }: { project: ProjectDetail }) {
  const queryClient = useQueryClient()
  const saveStyle = useMutation({
    mutationFn: (creative_style: CreativeStyleId) =>
      api(`/api/projects/${project.id}`, { method: "PATCH", body: JSON.stringify({ creative_style }) }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["project", project.id] }),
  })
  const busy = project.status === "analyzing" || project.status === "generating"
  const removeAsset = useMutation({
    mutationFn: (assetId: string) => api(`/api/assets/${assetId}`, { method: "DELETE" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["project", project.id] }),
    onError: reportDelete,
  })

  return (
    <section className="card space-y-4 p-4">
      <div>
        <h2 className="text-sm font-medium">Style</h2>
        <p className="mt-1 text-xs text-mist">{styleLabel(project.creative_style)} backgrounds. Photos stay on top.</p>
        <div className="mt-3">
          <StylePicker value={project.creative_style || "cinematic"} disabled={busy || saveStyle.isPending} onChange={(id) => saveStyle.mutate(id)} />
        </div>
      </div>
      {project.face && (
        <FacePhoto id={project.face.id} url={project.face.url} disabled={busy} onDelete={(id) => removeAsset.mutate(id)} />
      )}
      {(project.people ?? []).length > 0 && (
        <div>
          <p className="label">People in the video</p>
          <div className="mt-2 flex gap-2">
            {(project.people ?? []).map((person) => (
              <div key={person.id} className="relative">
                <img src={person.url} alt="Person from the video" className="h-16 w-12 rounded-md object-cover ring-1 ring-line" />
                <DeleteButton label="person" disabled={busy} onDelete={() => removeAsset.mutate(person.id)} className="absolute -right-1 -top-1 bg-ink/80" />
              </div>
            ))}
          </div>
        </div>
      )}
      {project.youtube_url && (
        <div>
          <p className="label">Source video</p>
          <a href={project.youtube_url} target="_blank" rel="noreferrer" className="mt-1 block truncate text-sm text-paper hover:text-ember">
            {project.youtube_title ?? project.youtube_url}
          </a>
        </div>
      )}
      <ResearchNotes
        brief={project.research_brief}
        images={project.popular ?? []}
        removeDisabled={busy}
        onRemove={(assetId) => removeAsset.mutate(assetId)}
      />
      {project.audience_brief && (
        <div>
          <p className="label">Audience</p>
          <p className="mt-1 text-sm text-paper">{project.audience_brief.viewer}</p>
          <p className="mt-1 text-xs leading-5 text-mist">{project.audience_brief.click_reason}</p>
        </div>
      )}
      {project.references.length > 0 && (
        <div>
          <p className="label">References</p>
          <div className="mt-2 grid grid-cols-2 gap-2">
            {project.references.map((reference) => (
              <div key={reference.id} className="relative">
                <img src={reference.url} alt="Reference thumbnail" className="aspect-video w-full rounded-md object-cover ring-1 ring-line" />
                <DeleteButton label="reference" disabled={busy} onDelete={() => removeAsset.mutate(reference.id)} className="absolute right-1 top-1 bg-ink/80" />
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  )
}

function FacePhoto({ id, url, disabled, onDelete }: { id: string; url: string; disabled: boolean; onDelete: (id: string) => void }) {
  return (
    <div>
      <p className="label">Creator</p>
      <div className="relative mt-2 h-16 w-16">
        <img src={url} alt="Creator" className="h-16 w-16 rounded-full object-cover ring-1 ring-line" />
        <DeleteButton label="creator photo" disabled={disabled} onDelete={() => onDelete(id)} className="absolute -right-1 -top-1 bg-ink/80" />
      </div>
    </div>
  )
}
