import type { Concept } from "../types"

type Props = {
  concepts: Concept[]
  busy: boolean
  pendingId: string | null
  onGenerate: (conceptId: string) => void
}

export function ConceptGrid({ concepts, busy, pendingId, onGenerate }: Props) {
  return (
    <section className="mt-10">
      <h2 className="font-serif text-3xl">Four directions</h2>
      <p className="mt-2 max-w-xl text-mist">Pick the frame you want rendered. The others stay here if you want another pass.</p>
      <div className="mt-5 grid gap-4 md:grid-cols-2">
        {concepts.map((concept) => (
          <article key={concept.id} className="flex flex-col rounded-2xl border border-line bg-panel p-5">
            <p className="text-xs uppercase tracking-[0.16em] text-gold">{concept.name}</p>
            <h3 className="mt-3 font-serif text-3xl leading-none tracking-tight">{concept.hook}</h3>
            <p className="mt-4 text-sm leading-6 text-mist">{concept.visual_story}</p>
            <p className="mt-3 text-sm leading-6">{concept.why_it_works}</p>
            <button
              type="button"
              disabled={busy}
              onClick={() => onGenerate(concept.id)}
              className="mt-5 self-start rounded-full bg-ember px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
            >
              {pendingId === concept.id ? "Starting…" : "Generate thumbnail"}
            </button>
          </article>
        ))}
      </div>
    </section>
  )
}
