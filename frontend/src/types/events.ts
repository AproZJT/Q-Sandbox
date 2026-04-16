export type SandboxStage = 'success' | 'error' | 'timeout' | 'finished' | 'unknown'

export interface SSEEnvelope<TPayload = Record<string, unknown>> {
  submission_id: string
  event_id: number
  ts: string
  type: string
  payload: TPayload
}

export interface SandboxResultPayload {
  exit_code: number
  time_ms: number
  stage: SandboxStage
  summary: string
}
