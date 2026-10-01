import { useQuery } from "@tanstack/react-query"
import type { ReactNode } from "react"
import { Link, useLocation } from "react-router-dom"
import { projectsQuery } from "../queries"
import { Icon } from "./Icon"
import { Logo } from "./Logo"
import { SystemStatusCard } from "./SystemStatusCard"

const RECENT_LIMIT = 6

function NavItem({ to, active, children }: { to: string; active: boolean; children: ReactNode }) {
  return (
    <Link
      to={to}
      aria-current={active ? "page" : undefined}
      className={`flex h-8 items-center gap-2.5 rounded-md px-2 text-sm transition ${active ? "bg-panel-2 text-paper" : "text-mist hover:bg-panel-2/60 hover:text-paper"}`}
    >
      {children}
    </Link>
  )
}

export function Sidebar() {
  const { pathname, search } = useLocation()
  const filter = new URLSearchParams(search).get("filter")
  const projects = useQuery(projectsQuery)
  const recent = (projects.data ?? []).slice(0, RECENT_LIMIT)
  const onDashboard = pathname === "/"

  return (
    <aside className="sticky top-0 hidden h-screen w-60 shrink-0 flex-col border-r border-line bg-panel md:flex">
      <div className="flex h-14 items-center border-b border-line px-4">
        <Logo />
      </div>
      <div className="p-3">
        <Link to="/new" className="btn-primary w-full">
          <Icon name="plus" />
          New project
        </Link>
      </div>
      <nav className="space-y-0.5 px-3" aria-label="Main">
        <NavItem to="/" active={onDashboard && filter !== "saved"}>
          <Icon name="grid" /> Projects
        </NavItem>
        <NavItem to="/?filter=saved" active={onDashboard && filter === "saved"}>
          <Icon name="star" /> Saved
        </NavItem>
      </nav>
      {recent.length > 0 && (
        <div className="mt-6 min-h-0 flex-1 overflow-y-auto px-3">
          <p className="label px-2 pb-1.5">Recent</p>
          <div className="space-y-0.5">
            {recent.map((project) => (
              <NavItem key={project.id} to={`/projects/${project.id}`} active={pathname.startsWith(`/projects/${project.id}`)}>
                {project.cover_url ? (
                  <img src={project.cover_url} alt="" className="h-4 w-7 shrink-0 rounded-sm object-cover" />
                ) : (
                  <span className="h-4 w-7 shrink-0 rounded-sm bg-line" />
                )}
                <span className="truncate">{project.title}</span>
              </NavItem>
            ))}
          </div>
        </div>
      )}
      <div className="mt-auto p-3">
        <SystemStatusCard />
      </div>
    </aside>
  )
}
