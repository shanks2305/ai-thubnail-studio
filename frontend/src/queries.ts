import { queryOptions } from "@tanstack/react-query"
import { api } from "./api"
import type { ProjectSummary, SystemStatus } from "./types"

export const projectsQuery = queryOptions({
  queryKey: ["projects"],
  queryFn: () => api<ProjectSummary[]>("/api/projects"),
})

export const systemQuery = queryOptions({
  queryKey: ["system"],
  queryFn: () => api<SystemStatus>("/api/system"),
})
