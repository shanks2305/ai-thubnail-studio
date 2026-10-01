import { Link, Outlet } from "react-router-dom"
import { Icon } from "./Icon"
import { Logo } from "./Logo"
import { Sidebar } from "./Sidebar"

export function Shell() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <div className="flex h-14 items-center justify-between border-b border-line bg-panel px-4 md:hidden">
          <Logo />
          <Link to="/new" className="btn-primary h-8 px-2.5" aria-label="New project">
            <Icon name="plus" />
          </Link>
        </div>
        <Outlet />
      </div>
    </div>
  )
}
