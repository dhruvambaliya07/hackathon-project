import type { InterestProfile } from '@/types'
import { mapAnalysis } from '@/api/mappers'
import type { ApiEnvelope, ApiInterestAnalysis } from '@/api/types'
import { apiMode, demoUserId } from '@/config/runtime'
import { apiClient, unwrapApiResponse } from '@/services/apiClient'

export interface InterestAnalysisRequest { description: string }
export type InterestAnalysisResponse = InterestProfile

export interface InterestService {
  analyze(description: string): Promise<InterestProfile>
  createManualProfile(interests: string[]): InterestProfile
  getStoredProfile(): InterestProfile | null
}

const profileKey = 'aatmoday.interestProfile'

function storeProfile(profile: InterestProfile): InterestProfile {
  window.localStorage.setItem(profileKey, JSON.stringify(profile))
  return profile
}

function readStoredProfile(): InterestProfile | null {
  if (typeof window === 'undefined') return null
  const stored = window.localStorage.getItem(profileKey)
  if (!stored) return null
  try {
    const parsed: unknown = JSON.parse(stored)
    return parsed && typeof parsed === 'object' && 'signals' in parsed ? parsed as InterestProfile : null
  } catch {
    return null
  }
}

const mockProfile: Omit<InterestProfile, 'prompt'> = {
  userId: 'new-student',
  tags: [],
  signals: [
    { id: 'photography', name: 'Photography', score: 92, category: 'Creative', color: 'coral' },
    { id: 'filmmaking', name: 'Filmmaking', score: 84, category: 'Creative', color: 'sun' },
    { id: 'technology', name: 'Technology', score: 71, category: 'Making', color: 'sky' },
    { id: 'events', name: 'Event Management', score: 65, category: 'Community', color: 'mint' },
  ],
  goals: ['Meet people', 'Learn', 'Create'],
  traits: ['Creative', 'Collaborative', 'Curious'],
  explanation: 'Your answer points to a creative maker who likes learning by doing and bringing people together. We used your interests, the activities you mentioned, and the kind of connections you want to make.',
  updatedAt: new Date().toISOString(),
}

const mockInterestService: InterestService = {
  async analyze(description: InterestAnalysisRequest['description']) {
    if (description.trim().length < 12) throw new Error('Tell us a little more about what you are into so we can find a useful starting point.')

    await new Promise<void>((resolve) => window.setTimeout(resolve, 480))
    return storeProfile({ ...mockProfile, prompt: description.trim(), updatedAt: new Date().toISOString() })
  },
  createManualProfile(interests) {
    const selected = interests.length ? interests : ['Curiosity']
    return storeProfile({
      ...mockProfile,
      prompt: selected.join(', '),
      signals: selected.map((name, index) => ({ ...mockProfile.signals[index % mockProfile.signals.length], id: `manual-${index}`, name, score: 72 - index * 6 })),
      explanation: 'This starter profile is based on the interests you selected. You can refine it any time to make your matches more personal.',
      updatedAt: new Date().toISOString(),
    })
  },
  getStoredProfile: readStoredProfile,
}

export const interestService: InterestService = mockInterestService

if (apiMode === 'api') {
  interestService.analyze = async (description) => storeProfile({ ...mapAnalysis(unwrapApiResponse(await apiClient.post<{ text: string }, ApiEnvelope<ApiInterestAnalysis>>('/interests/analyze', { text: description }))), userId: demoUserId })
}