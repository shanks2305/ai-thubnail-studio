import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState, type FormEvent } from "react"
import { api } from "../api"
import { DeleteButton, reportDelete } from "../components/DeleteButton"
import { TopBar } from "../components/TopBar"
import { useLibrary } from "../components/LibraryPickers"

export function LibraryPage() {
  const queryClient = useQueryClient()
  const library = useLibrary()
  const [name, setName] = useState("")
  const [colors, setColors] = useState("#112233,#ff4d2e,#f2c14e")
  const [font, setFont] = useState("anton")
  const [channel, setChannel] = useState("")
  const [error, setError] = useState<string | null>(null)
  const refresh = () => queryClient.invalidateQueries()
  const createKit = useMutation({
    mutationFn: () =>
      api("/api/brand-kits", {
        method: "POST",
        body: JSON.stringify({
          name,
          colors: colors.split(",").map((item) => item.trim()).filter(Boolean),
          font,
          shared: true,
        }),
      }),
    onSuccess: () => {
      setName("")
      setError(null)
      return refresh()
    },
    onError: (caught: Error) => setError(caught.message),
  })
  const remove = useMutation({
    mutationFn: (path: string) => api(path, { method: "DELETE" }),
    onSuccess: refresh,
    onError: reportDelete,
  })
  const createChannel = useMutation({
    mutationFn: () => api("/api/channels", { method: "POST", body: JSON.stringify({ name: channel }) }),
    onSuccess: () => {
      setChannel("")
      return refresh()
    },
  })

  return (
    <>
      <TopBar crumbs={[{ label: "Projects", to: "/" }, { label: "Library" }]} />
      <main className="mx-auto grid w-full max-w-5xl gap-6 px-6 py-8 md:grid-cols-2">
        <section className="card p-5">
          <h1 className="text-lg font-semibold">Brand kits</h1>
          <p className="mt-1 text-sm text-mist">Shared kits are available to teammates.</p>
          <ul className="mt-4 space-y-2 text-sm">
            {library.kits.map((kit) => (
              <li key={kit.id} className="flex items-center justify-between gap-3">
                <span>{kit.name}</span>
                <span className="flex items-center gap-1">
                  {kit.colors.map((color) => (
                    <span key={color} className="h-4 w-4 rounded-sm ring-1 ring-line" style={{ background: color }} />
                  ))}
                  <DeleteButton label="brand kit" onDelete={() => remove.mutate(`/api/brand-kits/${kit.id}`)} />
                </span>
              </li>
            ))}
          </ul>
          <form className="mt-4 space-y-2" onSubmit={(event: FormEvent) => { event.preventDefault(); createKit.mutate() }}>
            <input aria-label="Brand name" value={name} onChange={(event) => setName(event.target.value)} placeholder="Brand name" className="field" />
            <input aria-label="Brand colors" value={colors} onChange={(event) => setColors(event.target.value)} className="field" />
            <select aria-label="Brand font" value={font} onChange={(event) => setFont(event.target.value)} className="field">
              <option value="anton">Anton</option>
              <option value="bebas">Bebas</option>
            </select>
            {error && <p className="text-sm text-ember">{error}</p>}
            <button type="submit" className="btn-primary" disabled={!name.trim()}>Save kit</button>
          </form>
        </section>
        <section className="card space-y-4 p-5">
          <h2 className="text-lg font-semibold">Channels</h2>
          <p className="text-sm text-mist">A channel remembers the style of projects you teach it.</p>
          <ul className="space-y-2 text-sm">
            {library.channels.map((item) => (
              <li key={item.id} className="flex items-center justify-between gap-3">
                <span>{item.name}</span>
                <DeleteButton label="channel" onDelete={() => remove.mutate(`/api/channels/${item.id}`)} />
              </li>
            ))}
          </ul>
          <form className="flex gap-2" onSubmit={(event) => { event.preventDefault(); createChannel.mutate() }}>
            <input aria-label="Channel name" value={channel} onChange={(event) => setChannel(event.target.value)} placeholder="Channel name" className="field" />
            <button type="submit" className="btn-outline" disabled={!channel.trim()}>Add</button>
          </form>
          <h2 className="text-lg font-semibold">Saved styles</h2>
          <ul className="space-y-2 text-sm">
            {library.profiles.map((profile) => (
              <li key={profile.id} className="flex items-center justify-between gap-3">
                <span>{profile.name}</span>
                <DeleteButton label="saved style" onDelete={() => remove.mutate(`/api/profiles/${profile.id}`)} />
              </li>
            ))}
            {library.profiles.length === 0 && <li className="text-mist">Save a style from a project after concepts are ready.</li>}
          </ul>
        </section>
      </main>
    </>
  )
}
