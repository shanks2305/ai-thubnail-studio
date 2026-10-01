import { describe, expect, it } from "vitest"
import { draftFromGeneration, draftsMatch, normalizeText, projectEventsUrl, renderedConceptIds } from "./editorState"
import type { Generation } from "./types"

const generation = {
  id: "g1",
  concept_id: "c1",
  attempt: 1,
  variation_axis: null,
  source_generation_id: null,
  impressions: 0,
  clicks: 0,
  image_url: "/api/assets/a",
  design_spec: { text: { content: "AI WON", position: "left", size: "large", color: "#ffffff" } },
  critique: null,
} satisfies Generation

describe("editor draft", () => {
  it("fills headline defaults and detects an unsaved change", () => {
    const current = draftFromGeneration(generation)
    expect(normalizeText(generation.design_spec.text).font).toBe("anton")
    expect(draftsMatch(current, current)).toBe(true)
    expect(draftsMatch(current, { ...current, text: { ...current.text, stroke: true } })).toBe(false)
  })

  it("keeps each rendered concept once", () => {
    expect(renderedConceptIds([{ concept_id: "c1" }, { concept_id: "c1" }, { concept_id: "c2" }])).toEqual(["c1", "c2"])
  })

  it("adds the access token to the event stream url", () => {
    expect(projectEventsUrl("p1", null)).toBe("/api/projects/p1/events")
    expect(projectEventsUrl("p1", "a b")).toBe("/api/projects/p1/events?access_token=a%20b")
  })
})
