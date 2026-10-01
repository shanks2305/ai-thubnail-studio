import { projectEventsUrl, setStudioToken, studioToken } from "./editorState"

export class ApiError extends Error {}

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers)
  const token = studioToken()
  if (token) headers.set("Authorization", `Bearer ${token}`)
  if (init?.body && !(init.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json")
  }
  const response = await fetch(path, { ...init, headers })
  if (response.status === 401) {
    setStudioToken(null)
    window.dispatchEvent(new Event("studio-unauthorized"))
  }
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { detail?: unknown } | null
    const detail = payload?.detail
    throw new ApiError(typeof detail === "string" ? detail : "The request did not go through.")
  }
  if (response.status === 204) {
    return undefined as T
  }
  const contentType = response.headers.get("content-type") ?? ""
  if (!contentType.includes("application/json")) {
    return undefined as T
  }
  return (await response.json()) as T
}

export { projectEventsUrl }

