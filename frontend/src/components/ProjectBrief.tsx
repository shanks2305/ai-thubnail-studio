import { useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "../api"
import type { ProjectDetail } from "../types"
import { StylePicker, styleLabel, type CreativeStyleId } from "./StylePicker"

export function ProjectBrief({ project }: { project: ProjectDetail }) {
  const queryClient = useQueryClient()
  const saveStyle = useMutation({
    mutationFn: (creative_style: CreativeStyleId) =>
      api(`/api/projects/${project.id}`, { method: "PATCH", body: JSON.stringify({ creative_style }) }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["project", project.id] }),
  })
  const busy = project.status === "analyzing" || project.status === "generating"

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
        <div>
          <p className="label">Creator</p>
          <img src={project.face.url} alt="Creator" className="mt-2 h-16 w-16 rounded-full object-cover ring-1 ring-line" />
        </div>
      )}
      {(project.people ?? []).length > 0 && (
        <div>
          <p className="label">People in the video</p>
          <div className="mt-2 flex gap-2">
            {(project.people ?? []).map((person) => (
              <img key={person.id} src={person.url} alt="Person from the video" className="h-16 w-12 rounded-md object-cover ring-1 ring-line" />
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
              <img key={reference.id} src={reference.url} alt="Reference thumbnail" className="aspect-video w-full rounded-md object-cover ring-1 ring-line" />
            ))}
          </div>
        </div>
      )}
    </section>
  )
}
