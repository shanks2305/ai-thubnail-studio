import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { api } from "../api"
import type { ProjectDetail } from "../types"
import { DeleteButton, reportDelete } from "./DeleteButton"

export function StudioTools({ project }: { project: ProjectDetail }) {
  const queryClient = useQueryClient()
  const [name, setName] = useState("")
  const [left, setLeft] = useState(project.generations[0]?.id ?? "")
  const [right, setRight] = useState(project.generations.at(-1)?.id ?? "")
  const [notes, setNotes] = useState("")
  const refresh = () => queryClient.invalidateQueries({ queryKey: ["project", project.id] })
  const saveStyle = useMutation({
    mutationFn: () => api(`/api/projects/${project.id}/profile`, { method: "POST", body: JSON.stringify({ name }) }),
    onSuccess: () => {
      setName("")
      return refresh()
    },
  })
  const experiment = useMutation({
    mutationFn: () =>
      api<{ id: string }>(`/api/projects/${project.id}/experiments`, {
        method: "POST",
        body: JSON.stringify({ generation_a_id: left, generation_b_id: right }),
      }),
    onSuccess: (created) =>
      api(`/api/experiments/${created.id}`, { method: "PATCH", body: JSON.stringify({ notes }) }).then(refresh),
  })
  const choose = useMutation({
    mutationFn: ({ id, winner }: { id: string; winner: string }) =>
      api(`/api/experiments/${id}`, { method: "PATCH", body: JSON.stringify({ winner_id: winner }) }),
    onSuccess: refresh,
  })
  const removeTest = useMutation({
    mutationFn: (id: string) => api(`/api/experiments/${id}`, { method: "DELETE" }),
    onSuccess: refresh,
    onError: reportDelete,
  })

  return (
    <section className="card space-y-4 p-4">
      <h2 className="text-sm font-medium">Style and tests</h2>
      <form className="flex gap-2" onSubmit={(event) => { event.preventDefault(); saveStyle.mutate() }}>
        <input value={name} onChange={(event) => setName(event.target.value)} aria-label="Style name" placeholder="Save this style" className="field" />
        <button type="submit" className="btn-outline" disabled={!name.trim() || !project.reference_profile}>Save</button>
      </form>
      {project.channel_id && (
        <button
          type="button"
          className="btn-ghost"
          onClick={() =>
            void api(`/api/channels/${project.channel_id}/learn`, {
              method: "POST",
              body: JSON.stringify({ project_id: project.id }),
            }).then(refresh)
          }
        >
          Teach this channel
        </button>
      )}
      {project.generations.length > 1 && (
        <form className="grid gap-2" onSubmit={(event) => { event.preventDefault(); experiment.mutate() }}>
          <div className="grid grid-cols-2 gap-2">
            <select aria-label="Thumbnail A" value={left} onChange={(event) => setLeft(event.target.value)} className="field">
              {project.generations.map((item) => <option key={item.id} value={item.id}>{item.design_spec.text.content}</option>)}
            </select>
            <select aria-label="Thumbnail B" value={right} onChange={(event) => setRight(event.target.value)} className="field">
              {project.generations.map((item) => <option key={item.id} value={item.id}>{item.design_spec.text.content}</option>)}
            </select>
          </div>
          <input value={notes} onChange={(event) => setNotes(event.target.value)} aria-label="Test notes" placeholder="What are you comparing?" className="field" />
          <button type="submit" className="btn-outline" disabled={!left || !right || left === right}>Start A/B test</button>
        </form>
      )}
      {project.experiments.map((item) => (
        <div key={item.id} className="flex flex-wrap items-center gap-2 text-xs text-mist">
          <span>{item.notes || "A/B test"}</span>
          <button type="button" className="chip" onClick={() => choose.mutate({ id: item.id, winner: item.generation_a_id })}>A wins</button>
          <button type="button" className="chip" onClick={() => choose.mutate({ id: item.id, winner: item.generation_b_id })}>B wins</button>
          {item.winner_id && <span>Winner saved</span>}
          <DeleteButton label="test" disabled={project.status === "analyzing" || project.status === "generating"} onDelete={() => removeTest.mutate(item.id)} />
        </div>
      ))}
    </section>
  )
}
