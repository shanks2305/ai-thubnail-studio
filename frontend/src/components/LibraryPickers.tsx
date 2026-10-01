import { useQuery } from "@tanstack/react-query"
import { api } from "../api"

type Kit = { id: string; name: string; colors: string[]; font: string }
type Named = { id: string; name: string }

export function useLibrary() {
  const kits = useQuery({ queryKey: ["brand-kits"], queryFn: () => api<Kit[]>("/api/brand-kits") })
  const profiles = useQuery({ queryKey: ["profiles"], queryFn: () => api<Named[]>("/api/profiles") })
  const channels = useQuery({ queryKey: ["channels"], queryFn: () => api<Named[]>("/api/channels") })
  return { kits: kits.data ?? [], profiles: profiles.data ?? [], channels: channels.data ?? [] }
}

export function LibraryPickers({
  brandKitId,
  profileId,
  channelId,
  onBrand,
  onProfile,
  onChannel,
  face,
  onFace,
}: {
  brandKitId: string
  profileId: string
  channelId: string
  onBrand: (id: string) => void
  onProfile: (id: string) => void
  onChannel: (id: string) => void
  face: File | null
  onFace: (file: File | null) => void
}) {
  const library = useLibrary()
  return (
    <div className="grid gap-3">
      <select aria-label="Brand kit" value={brandKitId} onChange={(event) => onBrand(event.target.value)} className="field">
        <option value="">No brand kit</option>
        {library.kits.map((kit) => (
          <option key={kit.id} value={kit.id}>{kit.name}</option>
        ))}
      </select>
      <select aria-label="Creator profile" value={profileId} onChange={(event) => onProfile(event.target.value)} className="field">
        <option value="">No saved style</option>
        {library.profiles.map((profile) => (
          <option key={profile.id} value={profile.id}>{profile.name}</option>
        ))}
      </select>
      <select aria-label="Channel" value={channelId} onChange={(event) => onChannel(event.target.value)} className="field">
        <option value="">No channel</option>
        {library.channels.map((channel) => (
          <option key={channel.id} value={channel.id}>{channel.name}</option>
        ))}
      </select>
      <label className="text-sm text-mist">
        Creator photo
        <input
          type="file"
          accept="image/png,image/jpeg,image/webp"
          aria-label="Creator photo"
          className="mt-1 block w-full text-sm"
          onChange={(event) => onFace(event.target.files?.[0] ?? null)}
        />
        {face && <span className="mt-1 block text-xs">{face.name}</span>}
      </label>
    </div>
  )
}
