import type { InterestProfile } from '@/types'

export interface InterestAnalysisRequest { description: string }
export type InterestAnalysisResponse = InterestProfile

export interface InterestService {
  analyze(description: string): Promise<InterestProfile>
  createManualProfile(interests: string[]): InterestProfile
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
    return { ...mockProfile, prompt: description.trim(), updatedAt: new Date().toISOString() }
  },
  createManualProfile(interests) {
    const selected = interests.length ? interests : ['Curiosity']
    return {
      ...mockProfile,
      prompt: selected.join(', '),
      signals: selected.map((name, index) => ({ ...mockProfile.signals[index % mockProfile.signals.length], id: `manual-${index}`, name, score: 72 - index * 6 })),
      explanation: 'This starter profile is based on the interests you selected. You can refine it any time to make your matches more personal.',
      updatedAt: new Date().toISOString(),
    }
  },
}

export const interestService: InterestService = mockInterestService