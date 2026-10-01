import { Link, NavLink, Outlet } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { api } from "../api"
import type { SystemStatus } from "../types"

export function Shell() {
  const system = useQuery({
    queryKey: ["system"],
    queryFn: () => api<SystemStatus>("/api/system"),
  })

  return (
    <div className="min-h-screen">
      <header className="border-b border-line/80">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-5 py-4">
          <Link to="/" className="flex items-center gap-3">
            <span className="grid h-9 w-11 place-items-center rounded-md bg-ember">
              <span className="h-4 w-7 rounded-[3px] border-2 border-paper" />
            </span>
            <span className="font-serif text-xl tracking-tight">Thumbnail Suite</span>
          </Link>
          <NavLink
            to="/new"
            className="rounded-full bg-ember px-4 py-2 text-sm font-medium text-white"
          >
            New project
          </NavLink>
        </div>
      </header>
      <Outlet />
      {system.data && (
        <footer className="mx-auto max-w-6xl px-5 py-8 text-sm text-mist">{system.data.message}</footer>
      )}
    </div>
  )
}
