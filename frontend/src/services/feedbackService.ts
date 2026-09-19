import type { Feedback } from '@/types'

export interface FeedbackRequest {
  recommendationId: string
  value: Feedback['value']
}

export type FeedbackResponse = Feedback

export interface FeedbackService {
  submit(request: FeedbackRequest): Promise<FeedbackResponse>
  list(): Promise<FeedbackResponse[]>
}

const feedbackKey = 'aatmoday.feedback'

function readFeedback(): Feedback[] {
  if (typeof window === 'undefined') return []
  const stored = window.localStorage.getItem(feedbackKey)
  if (!stored) return []
  try {
    const parsed: unknown = JSON.parse(stored)
    return Array.isArray(parsed) ? parsed as Feedback[] : []
  } catch {
    return []
  }
}

export const feedbackService: FeedbackService = {
  async submit(request) {
    const feedback: Feedback = { id: `feedback-${Date.now()}`, recommendationId: request.recommendationId, value: request.value, createdAt: new Date().toISOString() }
    const next = [...readFeedback().filter((item) => item.recommendationId !== request.recommendationId), feedback]
    window.localStorage.setItem(feedbackKey, JSON.stringify(next))
    return feedback
  },
  async list() { return readFeedback() },
}
