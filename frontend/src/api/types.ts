export interface ApiEnvelope<T> {
	data: T | null
	meta: { request_id?: string | null; page?: number | null; page_size?: number | null; total?: number | null }
	error: { code: string; message: string; details?: unknown } | null
}

export interface ApiInterest { id: string; name: string; category: string; weight: number }
export interface ApiUser { id: string; name: string; bio: string | null; created_at: string; updated_at: string }
export interface ApiGroup { id: string; name: string; description: string; category: string; image_url: string | null; location: string | null; meeting_frequency: string | null; member_count: number }
export interface ApiEvent { id: string; group_id: string; title: string; description: string; starts_at: string; ends_at: string | null; location: string; capacity: number | null; image_url: string | null }
export interface ApiRecommendation { id: string; type: string; target_type: 'group' | 'event'; target_id: string; title: string; description: string; score: number; matched_interests: string[]; reasons: string[]; explanation: string }
export interface ApiProfile { user: ApiUser; interests: ApiInterest[]; goals: string[]; traits: string[]; saved_groups: ApiGroup[]; interested_events: ApiEvent[] }
export interface ApiInterestAnalysis { original_text: string; interests: Array<{ name: string; confidence: number }>; goals: string[]; traits: string[]; source: 'ai' | 'fallback' }
export interface ApiIcebreaker { icebreaker: string; style: 'casual' | 'friendly' | 'professional' }
export interface ApiFeedback { accepted: boolean; feedback_type: 'interested' | 'not_interested' | 'already_joined' | 'wrong_match' }