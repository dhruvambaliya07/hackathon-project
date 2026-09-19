import { events } from '@/data/mockData'
import type { Event } from '@/types'
import { mapEvent } from '@/api/mappers'
import type { ApiEnvelope, ApiEvent, ApiGroup } from '@/api/types'
import { apiMode } from '@/config/runtime'
import { apiClient, unwrapApiResponse } from '@/services/apiClient'

export type EventListResponse = Event[]
export type EventDetailResponse = Event | undefined

export interface EventService {
  list(): Promise<Event[]>
  getById(id: string): Promise<Event | undefined>
  getInterestedIds(): string[]
  toggleInterested(eventId: string): boolean
  downloadCalendarEvent(event: Event): void
}

const interestedKey = 'aatmoday.interestedEvents'

function readIds(): string[] {
  if (typeof window === 'undefined') return []
  const value = window.localStorage.getItem(interestedKey)
  if (!value) return []
  try {
    const parsed: unknown = JSON.parse(value)
    return Array.isArray(parsed) && parsed.every((item): item is string => typeof item === 'string') ? parsed : []
  } catch {
    return []
  }
}

function calendarStamp(date: Date) { return date.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}Z$/, 'Z') }
function escapeCalendarText(value: string) { return value.replace(/\\/g, '\\\\').replace(/;/g, '\\;').replace(/,/g, '\\,').replace(/\n/g, '\\n') }

function toggleId(id: string): boolean {
  const current = readIds()
  const next = current.includes(id) ? current.filter((item) => item !== id) : [...current, id]
  window.localStorage.setItem(interestedKey, JSON.stringify(next))
  return next.includes(id)
}

export const eventService: EventService = {
  async list() { return events },
  async getById(id) { return events.find((event) => event.id === id) },
  getInterestedIds() { return readIds() },
  toggleInterested(id) { return toggleId(id) },
  downloadCalendarEvent(event) {
    const start = event.startsAt ? new Date(event.startsAt) : new Date(`${new Date().getFullYear()} ${event.date} ${event.time}`)
    const end = new Date(start.getTime() + 90 * 60 * 1000)
    const ics = [
      'BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Aatmoday Connect//Events//EN', 'BEGIN:VEVENT',
      `UID:${event.id}@aatmoday.connect`, `DTSTAMP:${calendarStamp(new Date())}`, `DTSTART:${calendarStamp(start)}`, `DTEND:${calendarStamp(end)}`,
      `SUMMARY:${escapeCalendarText(event.title)}`, `DESCRIPTION:${escapeCalendarText(event.description)}`, `LOCATION:${escapeCalendarText(event.location)}`,
      'END:VEVENT', 'END:VCALENDAR',
    ].join('\r\n')
    const blob = new Blob([ics], { type: 'text/calendar;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${event.title.toLowerCase().replace(/[^a-z0-9]+/g, '-')}.ics`
    link.click()
    URL.revokeObjectURL(url)
  },
}

if (apiMode === 'api') {
  eventService.list = async () => {
    const [eventResponse, groupResponse] = await Promise.all([
      apiClient.get<ApiEnvelope<ApiEvent[]>>('/events?page=1&page_size=100'),
      apiClient.get<ApiEnvelope<ApiGroup[]>>('/groups?page=1&page_size=100'),
    ])
    const groupsById = new Map(unwrapApiResponse(groupResponse).map((group) => [group.id, group]))
    return unwrapApiResponse(eventResponse).map((event) => mapEvent(event, groupsById.get(event.group_id)))
  }
  eventService.getById = async (id) => {
    const [eventResponse, groupResponse] = await Promise.all([
      apiClient.get<ApiEnvelope<ApiEvent>>(`/events/${id}`),
      apiClient.get<ApiEnvelope<ApiGroup[]>>('/groups?page=1&page_size=100'),
    ])
    const event = unwrapApiResponse(eventResponse)
    const group = unwrapApiResponse(groupResponse).find((item) => item.id === event.group_id)
    return mapEvent(event, group)
  }
}
