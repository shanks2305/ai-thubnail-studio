import type { Generation, TextSpec } from "./types"

export const TOKEN_KEY = "studio-token"

export type EditorDraft = {
  text: TextSpec
  scrimStrength: number
  palette: string[]
  recolor: boolean
}

export function studioToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY)
}

export function setStudioToken(token: string | null) {
  if (token) sessionStorage.setItem(TOKEN_KEY, token)
  else sessionStorage.removeItem(TOKEN_KEY)
}

export function projectEventsUrl(projectId: string, token = studioToken()): string {
  const path = `/api/projects/${projectId}/events`
  if (!token) return path
  return `${path}?access_token=${encodeURIComponent(token)}`
}

export function normalizeText(text: EditorDraft["text"] | Generation["design_spec"]["text"]): TextSpec {
  return {
    content: text.content,
    position: text.position,
    size: text.size,
    color: text.color,
    font: text.font ?? "anton",
    stroke: text.stroke ?? false,
    vertical: text.vertical ?? "middle",
  }
}

export function draftFromGeneration(generation: Generation): EditorDraft {
  return {
    text: normalizeText(generation.design_spec.text),
    scrimStrength: generation.design_spec.scrim_strength ?? 0,
    palette: generation.design_spec.palette ?? ["#16130f", "#ff4d2e", "#f2c14e"],
    recolor: generation.design_spec.recolor ?? false,
  }
}

export function draftsMatch(current: EditorDraft, next: EditorDraft): boolean {
  return JSON.stringify(current) === JSON.stringify(next)
}

export function renderedConceptIds(generations: { concept_id: string }[]): string[] {
  return [...new Set(generations.map((item) => item.concept_id))]
}
