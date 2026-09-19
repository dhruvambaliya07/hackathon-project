import { groups } from '@/data/mockData'
import type { Group } from '@/types'
import { mapGroup } from '@/api/mappers'
import type { ApiEnvelope, ApiGroup } from '@/api/types'
import { apiMode } from '@/config/runtime'
import { apiClient, unwrapApiResponse } from '@/services/apiClient'

export type GroupListResponse = Group[]
export type GroupDetailResponse = Group | undefined

export interface GroupService {
  list(): Promise<Group[]>
  getById(id: string): Promise<Group | undefined>
  getInterestedIds(): string[]
  getSavedIds(): string[]
  toggleInterested(groupId: string): boolean
  toggleSaved(groupId: string): boolean
}

const keys = { interested: 'aatmoday.interestedGroups', saved: 'aatmoday.savedGroups' }

function readIds(key: string): string[] {
  if (typeof window === 'undefined') return []
  const value = window.localStorage.getItem(key)
  if (!value) return []
  try {
    const parsed: unknown = JSON.parse(value)
    return Array.isArray(parsed) && parsed.every((item): item is string => typeof item === 'string') ? parsed : []
  } catch {
    return []
  }
}

function toggleId(key: string, id: string): boolean {
  const current = readIds(key)
  const next = current.includes(id) ? current.filter((item) => item !== id) : [...current, id]
  window.localStorage.setItem(key, JSON.stringify(next))
  return next.includes(id)
}

export const groupService: GroupService = {
  async list() { return groups },
  async getById(id) { return groups.find((group) => group.id === id) },
  getInterestedIds() { return readIds(keys.interested) },
  getSavedIds() { return readIds(keys.saved) },
  toggleInterested(id) { return toggleId(keys.interested, id) },
  toggleSaved(id) { return toggleId(keys.saved, id) },
}

if (apiMode === 'api') {
  groupService.list = async () => mapGroupList(unwrapApiResponse(await apiClient.get<ApiEnvelope<ApiGroup[]>>('/groups?page=1&page_size=100')))
  groupService.getById = async (id) => mapGroup(unwrapApiResponse(await apiClient.get<ApiEnvelope<ApiGroup>>(`/groups/${id}`)))
}

function mapGroupList(items: ApiGroup[]): Group[] { return items.map(mapGroup) }