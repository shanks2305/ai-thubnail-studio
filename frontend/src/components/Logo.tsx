import { Link } from "react-router-dom"

export function Logo() {
  return (
    <Link to="/" className="flex items-center gap-2.5">
      <span className="grid h-7 w-8 place-items-center rounded-md bg-gradient-to-br from-ember to-[#ff8a3d] shadow-sm shadow-ember/30">
        <span className="h-3 w-5 rounded-[2px] border-[1.5px] border-white" />
      </span>
      <span className="text-sm font-semibold tracking-tight">Thumbnail Suite</span>
    </Link>
  )
}
