import type { Interest, InterestProfile } from '@/types'

export interface ProfileService {
  getProfile(): Promise<InterestProfile>
  updateInterests(interests: string[]): Promise<InterestProfile>
}

const profileKey = 'aatmoday.interestProfile'
const colors: Interest['color'][] = ['coral', 'sun', 'sky', 'mint']

const defaultProfile: InterestProfile = {
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

function readProfile(): InterestProfile {
  if (typeof window === 'undefined') return defaultProfile
  const stored = window.localStorage.getItem(profileKey)
  if (!stored) return defaultProfile
  try {
    const parsed: unknown = JSON.parse(stored)
    return parsed && typeof parsed === 'object' && 'signals' in parsed ? parsed as InterestProfile : defaultProfile
  } catch {
    return defaultProfile
  }
}

function writeProfile(profile: InterestProfile) {
  window.localStorage.setItem(profileKey, JSON.stringify(profile))
  return profile
}

export const profileService: ProfileService = {
  async getProfile() { return readProfile() },
  async updateInterests(interests) {
    const current = readProfile()
    const nextSignals = interests.map((name, index) => {
      const existing = current.signals.find((signal) => signal.name.toLowerCase() === name.toLowerCase())
      return existing ?? { id: name.toLowerCase().replace(/\s+/g, '-'), name, score: Math.max(58, 78 - index * 6), category: 'Exploring', color: colors[index % colors.length] }
    })
    return writeProfile({ ...current, signals: nextSignals, updatedAt: new Date().toISOString() })
  },
}

export const profileInterestOptions = ['Photography', 'Filmmaking', 'Technology', 'Event Management', 'Music', 'Design', 'Entrepreneurship', 'Sports']
