import type { ApiEvent, ApiGroup, ApiInterest, ApiInterestAnalysis, ApiProfile, ApiRecommendation } from '@/api/types'
import type { Event, Group, Interest, InterestProfile, Recommendation } from '@/types'

const colors: Interest['color'][] = ['coral', 'sun', 'sky', 'mint']
const imageFallback = 'https://placehold.co/800x450/png?text=Aatmoday+Connect'

function mapInterest(interest: ApiInterest, index: number): Interest {
  return { id: interest.id, name: interest.name, category: interest.category, color: colors[index % colors.length] }
}

export function mapGroup(group: ApiGroup): Group {
  return { id: group.id, name: group.name, category: group.category, description: group.description, memberCount: group.member_count, imageUrl: group.image_url ?? imageFallback, accent: colors[0], tags: [], location: group.location ?? undefined }
}

export function mapEvent(event: ApiEvent, group?: ApiGroup): Event {
  const startsAt = new Date(event.starts_at)
  return { id: event.id, title: event.title, groupId: event.group_id, groupName: group?.name ?? 'Aatmoday community', description: event.description, date: startsAt.toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' }), time: startsAt.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' }), startsAt: event.starts_at, endsAt: event.ends_at ?? undefined, location: event.location, imageUrl: group?.image_url ?? imageFallback, attendees: 0, tags: [] }
}

export function mapRecommendation(recommendation: ApiRecommendation): Recommendation {
  return { id: recommendation.id, type: recommendation.target_type, targetId: recommendation.target_id, title: recommendation.title, subtitle: recommendation.description, imageUrl: imageFallback, matchScore: recommendation.score, matchedInterests: recommendation.matched_interests, reasons: recommendation.reasons.map((reason) => ({ label: 'Why this matches', detail: reason, score: recommendation.score })), backendExplanation: recommendation.explanation }
}

export function mapAnalysis(analysis: ApiInterestAnalysis): InterestProfile {
  return { userId: '', prompt: analysis.original_text, tags: analysis.interests.map((interest, index) => mapInterest({ id: interest.name.toLowerCase(), name: interest.name, category: 'Interest', weight: interest.confidence }, index)), signals: analysis.interests.map((interest, index) => ({ ...mapInterest({ id: interest.name.toLowerCase(), name: interest.name, category: 'Interest', weight: interest.confidence }, index), score: Math.round(interest.confidence * 100) })), goals: analysis.goals, traits: analysis.traits, explanation: analysis.source === 'fallback' ? 'This profile was created using a deterministic fallback while AI was unavailable.' : 'This profile was extracted from your interests.', updatedAt: new Date().toISOString() }
}

export function mapProfile(profile: ApiProfile): InterestProfile {
  return { userId: profile.user.id, prompt: profile.user.bio ?? '', tags: profile.interests.map(mapInterest), signals: profile.interests.map((interest, index) => ({ ...mapInterest(interest, index), score: Math.round(interest.weight * 100) })), goals: profile.goals, traits: profile.traits, explanation: 'Your matches are based on the interests, goals, and traits in your profile.', updatedAt: profile.user.updated_at }
}