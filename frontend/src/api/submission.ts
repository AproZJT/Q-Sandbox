export interface CreateSubmissionRequest {
  problem_id: string
  language: 'cpp'
  mode: 'review' | 'socratic'
  source_code: string
}

export interface CreateSubmissionResponse {
  submission_id: string
  stream_url: string
  created_at: string
}

const API_BASE = 'http://127.0.0.1:8000'

export async function createSubmission(payload: CreateSubmissionRequest): Promise<CreateSubmissionResponse> {
  const response = await fetch(`${API_BASE}/api/v1/submissions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(`创建 submission 失败: ${response.status} ${text}`)
  }

  return (await response.json()) as CreateSubmissionResponse
}

export function toStreamUrl(streamUrl: string): string {
  if (streamUrl.startsWith('http://') || streamUrl.startsWith('https://')) {
    return streamUrl
  }
  return `${API_BASE}${streamUrl}`
}
