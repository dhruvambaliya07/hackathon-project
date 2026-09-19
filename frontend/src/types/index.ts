export interface User {
  id: string
  name: string
  handle: string
  avatarUrl: string
  year: string
  course: string
  bio: string
  interests: string[]
}

export interface Interest {
  id: string
  name: string
  category: string
  color: 'coral' | 'mint' | 'sun' | 'sky'
}

export interface InterestSignal {
  id: string
  name: string
  score: number
  category: string
  color: Interest['color']
}

export interface InterestProfile {
  userId: string
  prompt: string
  tags: Interest[]
  signals: InterestSignal[]
  goals: string[]
  traits: string[]
  explanation: string
  updatedAt: string
}

export interface Group {
  id: string
  name: string
  category: string
  description: string
  memberCount: number
  imageUrl: string
  accent: 'coral' | 'mint' | 'sun' | 'sky'
  tags: string[]
  nextEvent?: string
}

export interface Event {
  id: string
  title: string
  groupId: string
  groupName: string
  description: string
  date: string
  time: string
  location: string
  imageUrl: string
  attendees: number
  tags: string[]
}

export interface RecommendationReason {
  label: string
  detail: string
  score: number
}

export interface Icebreaker {
  id: string
  text: string
  context: string
}

export interface Recommendation {
  id: string
  type: 'group' | 'event'
  targetId: string
  title: string
  subtitle: string
  imageUrl: string
  matchScore: number
  matchedInterests: string[]
  reasons: RecommendationReason[]
  icebreakers: Icebreaker[]
}

export interface Feedback {
  id: string
  recommendationId: string
  value: 'up' | 'down'
  createdAt: string
}
