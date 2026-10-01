export type PrivacyMode = "local" | "hybrid" | "cloud"

export type ProjectStatus =
  | "draft"
  | "analyzing"
  | "concepts_ready"
  | "generating"
  | "ready"
  | "failed"

export type ProjectSummary = {
  id: string
  title: string
  description: string
  status: ProjectStatus
  favorite: boolean
  privacy_mode: PrivacyMode
  youtube_url: string | null
  updated_at: string
  cover_url: string | null
}

export type TextSpec = {
  content: string
  position: "left" | "center" | "right"
  size: "medium" | "large" | "very large"
  color: string
}

export type Concept = {
  id: string
  name: string
  hook: string
  visual_story: string
  subject: string
  background: string
  composition: string
  text: string
  emotional_direction: string
  why_it_works: string
}

export type Critique = {
  overall: number
  passed: boolean
  issues: { type: string; severity: string; message: string }[]
  recommended_changes: string[]
}

export type Generation = {
  id: string
  concept_id: string
  attempt: number
  image_url: string | null
  design_spec: { text: TextSpec }
  critique: Critique | null
}

export type AgentRun = {
  id: string
  agent: string
  status: "running" | "completed" | "failed" | string
  provider: string | null
  error: string | null
}

export type ProjectDetail = ProjectSummary & {
  error: string | null
  youtube_title: string | null
  selected_concept_id: string | null
  concepts: Concept[]
  generations: Generation[]
  agent_runs: AgentRun[]
  references: { id: string; url: string }[]
}

export type SystemStatus = {
  environment: "development" | "production"
  text_provider: string
  image_provider: string
  message: string
}

export const STATUS_LABEL: Record<ProjectStatus, string> = {
  draft: "Draft",
  analyzing: "Studying",
  concepts_ready: "Concepts ready",
  generating: "Rendering",
  ready: "Ready",
  failed: "Needs attention",
}
