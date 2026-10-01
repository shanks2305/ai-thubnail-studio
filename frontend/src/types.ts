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
  youtube_url: string | null
  updated_at: string
  cover_url: string | null
}

export type TextSpec = {
  content: string
  position: "left" | "center" | "right"
  size: "medium" | "large" | "very large"
  color: string
  font: "anton" | "bebas"
  stroke: boolean
  vertical: "top" | "middle" | "bottom"
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
  image_prompt: string | null
  archived: boolean
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
  variation_axis: string | null
  source_generation_id: string | null
  impressions: number
  clicks: number
  image_url: string | null
  design_spec: {
    text: Partial<TextSpec> & Pick<TextSpec, "content" | "position" | "size" | "color">
    palette?: string[]
    scrim_strength?: number
    recolor?: boolean
    image_prompt?: string
  }
  critique: Critique | null
}

export type AgentRun = {
  id: string
  agent: string
  status: "running" | "completed" | "failed" | string
  provider: string | null
  error: string | null
  input_tokens: number | null
  output_tokens: number | null
  duration_ms: number | null
}

export type ProjectDetail = ProjectSummary & {
  error: string | null
  youtube_title: string | null
  selected_concept_id: string | null
  selected_generation_id: string | null
  brand_kit_id: string | null
  creator_profile_id: string | null
  channel_id: string | null
  audience_brief: { viewer: string; belief: string; click_reason: string; avoid: string[] } | null
  reference_profile: Record<string, unknown> | null
  concepts: Concept[]
  generations: Generation[]
  agent_runs: AgentRun[]
  references: { id: string; url: string }[]
  face: { id: string; url: string } | null
  experiments: Experiment[]
}

export type Experiment = {
  id: string
  generation_a_id: string
  generation_b_id: string
  winner_id: string | null
  notes: string
}

export type SystemStatus = {
  environment: "development" | "production"
  chat_provider: string
  judge_provider: string
  image_provider: string
  auth_required: boolean
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
