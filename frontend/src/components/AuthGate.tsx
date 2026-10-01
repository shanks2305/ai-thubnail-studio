import { useQuery } from "@tanstack/react-query"
import { useEffect, useState, type FormEvent, type ReactNode } from "react"
import { systemQuery } from "../queries"
import { setStudioToken, studioToken } from "../editorState"

export function AuthGate({ children }: { children: ReactNode }) {
  const system = useQuery(systemQuery)
  const [token, setToken] = useState(studioToken() ?? "")
  const [authed, setAuthed] = useState(Boolean(studioToken()))

  useEffect(() => {
    const onUnauthorized = () => setAuthed(false)
    window.addEventListener("studio-unauthorized", onUnauthorized)
    return () => window.removeEventListener("studio-unauthorized", onUnauthorized)
  }, [])

  if (!system.data?.auth_required || authed) return children

  function submit(event: FormEvent) {
    event.preventDefault()
    setStudioToken(token.trim())
    setAuthed(true)
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-md flex-col justify-center px-6">
      <h1 className="text-2xl font-semibold">Sign in</h1>
      <p className="mt-2 text-sm text-mist">This studio asks for its access token before it opens a project.</p>
      <form onSubmit={submit} className="mt-6 space-y-3">
        <input type="password" aria-label="Access token" value={token} onChange={(event) => setToken(event.target.value)} className="field" />
        <button type="submit" className="btn-primary" disabled={!token.trim()}>Continue</button>
      </form>
    </main>
  )
}
