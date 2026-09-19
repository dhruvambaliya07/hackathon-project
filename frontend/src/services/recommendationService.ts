import { events, groups, recommendations } from '@/data/mockData'
import { profileService } from '@/services/profileService'
import type { InterestProfile, Recommendation } from '@/types'
import type { ApiEnvelope, ApiRecommendation } from '@/api/types'
import { mapRecommendation } from '@/api/mappers'
import { apiClient, unwrapApiResponse } from '@/services/apiClient'
import { apiMode, demoUserId } from '@/config/runtime'

export type RecommendationListResponse = Recommendation[]

export interface RecommendationService {
  list(): Promise<Recommendation[]>
  getInterestProfile(): Promise<InterestProfile>
  getSavedIds(): string[]
  getInterestedIds(): string[]
  toggleSaved(recommendationId: string): boolean
  toggleInterested(recommendationId: string): boolean
}

const storageKeys = {
  saved: 'aatmoday.savedRecommendations',
  interested: 'aatmoday.interestedRecommendations',
}

function readIds(key: string): string[] {
  if (typeof window === 'undefined') return []
  const stored = window.localStorage.getItem(key)
  if (!stored) return []
  try {
    const parsed: unknown = JSON.parse(stored)
    return Array.isArray(parsed) && parsed.every((item): item is string => typeof item === 'string') ? parsed : []
  } catch {
    return []
  }
}

function toggleId(key: string, id: string): boolean {
  const ids = readIds(key)
  const nextIds = ids.includes(id) ? ids.filter((item) => item !== id) : [...ids, id]
  window.localStorage.setItem(key, JSON.stringify(nextIds))
  return nextIds.includes(id)
}

export const recommendationService: RecommendationService = {
  async list() {
    const profile = await profileService.getProfile()
    const profileInterests = new Set(profile.signals.map((signal) => signal.name.toLowerCase()))
    return recommendations.map((recommendation) => {
      const matchedInterests = recommendation.matchedInterests.filter((interest) => profileInterests.has(interest.toLowerCase()))
      return { ...recommendation, matchedInterests: matchedInterests.length ? matchedInterests : recommendation.matchedInterests.slice(0, 1) }
    })
  },
  async getInterestProfile() {
    return profileService.getProfile()
  },
  getSavedIds() {
    return readIds(storageKeys.saved)
  },
  getInterestedIds() {
    return readIds(storageKeys.interested)
  },
  toggleSaved(recommendationId) {
    return toggleId(storageKeys.saved, recommendationId)
  },
  toggleInterested(recommendationId) {
    return toggleId(storageKeys.interested, recommendationId)
  },
}

if (apiMode === 'api') {
  recommendationService.list = async () => {
    const profile = await profileService.getProfile()
    const interestText = profile.prompt || profile.signals.map((signal) => signal.name).join(', ') || 'general hobbies'
    const response = await apiClient.post<{ user_id: string; interest_text: string; limit: number }, ApiEnvelope<{ recommendations: ApiRecommendation[] }>>('/recommendations', { user_id: demoUserId, interest_text: interestText, limit: 50 })
    return unwrapApiResponse(response).recommendations.map(mapRecommendation)
  }
  recommendationService.getInterestProfile = profileService.getProfile
}

export function findRecommendationContext(recommendation: Recommendation) {
  return recommendation.type === 'group'
    ? groups.find((group) => group.id === recommendation.targetId)
    : events.find((event) => event.id === recommendation.targetId)
}
