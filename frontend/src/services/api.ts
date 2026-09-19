import { events, groups, recommendations } from '@/data/mockData'
import type { Event, Group, Recommendation } from '@/types'

export interface ApiClient {
  listGroups(): Promise<Group[]>
  listEvents(): Promise<Event[]>
  listRecommendations(): Promise<Recommendation[]>
}

const mockClient: ApiClient = {
  async listGroups() { return groups },
  async listEvents() { return events },
  async listRecommendations() { return recommendations },
}

export const api = mockClient
