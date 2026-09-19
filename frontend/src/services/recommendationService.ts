import { events, groups, recommendations } from '@/data/mockData'
import type { InterestProfile, Recommendation } from '@/types'

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

const interestProfile: InterestProfile = {
  userId: 'u1',
  prompt: 'I want to make things, meet curious people, and get better at taking photos.',
  tags: [],
  signals: [
    { id: 'photography', name: 'Photography', score: 92, category: 'Creative', color: 'coral' },
    { id: 'filmmaking', name: 'Filmmaking', score: 84, category: 'Creative', color: 'sun' },
    { id: 'technology', name: 'Technology', score: 71, category: 'Making', color: 'sky' },
    { id: 'events', name: 'Event Management', score: 65, category: 'Community', color: 'mint' },
  ],
  goals: ['Meet people', 'Learn', 'Create'],
  traits: ['Creative', 'Collaborative', 'Curious'],
  explanation: 'Your matches lean creative, hands-on, and social. Each score is a relevance signal based on the interests and goals in your profile, not a measure of you.',
  updatedAt: new Date().toISOString(),
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
    return recommendations
  },
  async getInterestProfile() {
    return interestProfile
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

export function findRecommendationContext(recommendation: Recommendation) {
  return recommendation.type === 'group'
    ? groups.find((group) => group.id === recommendation.targetId)
    : events.find((event) => event.id === recommendation.targetId)
}
