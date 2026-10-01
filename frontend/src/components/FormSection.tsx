import type { ReactNode } from "react"

type Props = {
  step: number
  title: string
  hint: string
  optional?: boolean
  children: ReactNode
}

export function FormSection({ step, title, hint, optional = false, children }: Props) {
  return (
    <section className="grid gap-4 border-b border-line px-6 py-6 last:border-b-0 md:grid-cols-[13rem_minmax(0,1fr)]">
      <div className="flex gap-3">
        <span className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-panel-2 text-xs font-medium tabular-nums text-mist ring-1 ring-line">
          {step}
        </span>
        <div>
          <h2 className="text-sm font-medium">
            {title}
            {optional && <span className="ml-1.5 font-normal text-mist">Optional</span>}
          </h2>
          <p className="mt-1 text-xs leading-5 text-mist">{hint}</p>
        </div>
      </div>
      <div>{children}</div>
    </section>
  )
}
