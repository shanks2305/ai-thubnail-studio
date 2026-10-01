import type { ResearchBrief } from "../types"
import { DeleteButton } from "./DeleteButton"

export function ResearchNotes({
  brief,
  images,
  onRemove,
  removeDisabled,
}: {
  brief: ResearchBrief | null
  images: { id: string; url: string }[]
  onRemove?: (id: string) => void
  removeDisabled?: boolean
}) {
  if (!brief) return null
  const videos = brief.popular_videos ?? []
  const visible = brief.game || brief.facts.length > 0 || videos.length > 0 || images.length > 0 || brief.visual_anchor
  if (!visible) return null

  return (
    <div>
      <p className="label">Research</p>
      {brief.game && (
        <>
          <p className="mt-1 text-sm text-paper">{brief.game.name}</p>
          {brief.game.summary && <p className="mt-1 line-clamp-3 text-xs leading-5 text-mist">{brief.game.summary}</p>}
        </>
      )}
      {!brief.game && brief.visual_anchor && <p className="mt-1 text-xs leading-5 text-mist">{brief.visual_anchor}</p>}
      {brief.facts.length > 0 && (
        <ul className="mt-2 space-y-1">
          {brief.facts.map((fact) => (
            <li key={fact} className="text-xs leading-5 text-mist">{fact}</li>
          ))}
        </ul>
      )}
      {images.length > 0 && (
        <div className="mt-2 grid grid-cols-2 gap-2">
          {images.map((image, index) => (
            <div key={image.id} className="relative">
              {onRemove && <DeleteButton label="popular thumbnail" disabled={removeDisabled} onDelete={() => onRemove(image.id)} className="absolute right-1 top-1 bg-ink/80" />}
              <a href={videos[index]?.url || image.url} target="_blank" rel="noreferrer">
                <img src={image.url} alt={videos[index]?.title || "Popular thumbnail"} className="aspect-video w-full rounded-md object-cover ring-1 ring-line" />
                {videos[index] && (
                  <span className="mt-1 block truncate text-[11px] text-mist">{videos[index].title} · {views(videos[index].views)}</span>
                )}
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function views(count: number) {
  if (count >= 1_000_000) return `${(count / 1_000_000).toFixed(1)}M views`
  if (count >= 1_000) return `${Math.round(count / 1_000)}K views`
  return `${count} views`
}
