import type { ProjectDetail } from "../types"

export function ProjectBrief({ project }: { project: ProjectDetail }) {
  if (!project.youtube_url && project.references.length === 0 && !project.audience_brief && !project.face) return null

  return (
    <section className="card space-y-4 p-4">
      <h2 className="text-sm font-medium">Inputs</h2>
      {project.audience_brief && (
        <div>
          <p className="label">Audience</p>
          <p className="mt-1 text-sm text-paper">{project.audience_brief.viewer}</p>
          <p className="mt-1 text-xs leading-5 text-mist">{project.audience_brief.click_reason}</p>
        </div>
      )}
      {project.face && (
        <div>
          <p className="label">Creator</p>
          <img src={project.face.url} alt="Creator" className="mt-2 h-16 w-16 rounded-full object-cover ring-1 ring-line" />
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
