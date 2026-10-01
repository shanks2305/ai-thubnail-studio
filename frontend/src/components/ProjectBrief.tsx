import type { ProjectDetail } from "../types"

export function ProjectBrief({ project }: { project: ProjectDetail }) {
  if (!project.youtube_url && project.references.length === 0) return null

  return (
    <section className="card space-y-4 p-4">
      <h2 className="text-sm font-medium">Inputs</h2>
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
