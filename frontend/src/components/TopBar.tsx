import { Fragment, type ReactNode } from "react"
import { Link } from "react-router-dom"
import { Icon } from "./Icon"

export type Crumb = { label: string; to?: string }

export function TopBar({ crumbs, children }: { crumbs: Crumb[]; children?: ReactNode }) {
  return (
    <header className="sticky top-0 z-20 flex h-14 shrink-0 items-center justify-between gap-4 border-b border-line bg-ink/80 px-6 backdrop-blur-md">
      <nav aria-label="Breadcrumb" className="flex min-w-0 items-center gap-1.5 text-sm">
        {crumbs.map((crumb, index) => (
          <Fragment key={`${crumb.label}-${index}`}>
            {index > 0 && <Icon name="chevron" className="h-3.5 w-3.5 shrink-0 text-mist/50" />}
            {crumb.to ? (
              <Link to={crumb.to} className="shrink-0 text-mist transition hover:text-paper">
                {crumb.label}
              </Link>
            ) : (
              <span className="truncate font-medium text-paper">{crumb.label}</span>
            )}
          </Fragment>
        ))}
      </nav>
      {children && <div className="flex shrink-0 items-center gap-2">{children}</div>}
    </header>
  )
}
