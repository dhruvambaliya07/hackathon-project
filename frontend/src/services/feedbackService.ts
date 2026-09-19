import type { Feedback } from '@/types'
import type { ApiEnvelope, ApiFeedback } from '@/api/types'
import { apiClient, unwrapApiResponse } from '@/services/apiClient'
import { apiMode, demoUserId } from '@/config/runtime'

export interface FeedbackRequest {
  recommendationId: string
  value: Feedback['value']
  feedbackType?: 'interested' | 'not_interested' | 'already_joined' | 'wrong_match'
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

if (apiMode === 'api') {
  feedbackService.submit = async (request) => {
    const feedbackType = request.feedbackType ?? (request.value === 'up' ? 'interested' : 'not_interested')
    const response = await apiClient.post<{ user_id: string; recommendation_id: string; feedback_type: string }, ApiEnvelope<ApiFeedback>>('/feedback', { user_id: demoUserId, recommendation_id: request.recommendationId, feedback_type: feedbackType })
    const result = unwrapApiResponse(response)
    return { id: request.recommendationId, recommendationId: request.recommendationId, value: result.feedback_type === 'interested' ? 'up' : 'down', createdAt: new Date().toISOString() }
  }
  feedbackService.list = async () => []
}
